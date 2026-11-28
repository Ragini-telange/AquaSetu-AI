import os
import joblib
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.schemas.classification import (
    WaterPotabilityRequest,
    WaterPotabilityResponse,
    ExceededParameter,
    DistrictClassificationSummary,
    VerifiedClassificationStation,
    DistrictClassificationCoverageResponse,
)

# District alias normalization to map variations onto the 33 canonical spatial districts
DISTRICT_ALIASES = {
    'buldhana': 'buldana',
    'sindhudurg': 'sindudurg',
    'ahmadnagar': 'ahmednagar',
    'chhatrapati sambhajinagar': 'aurangabad',
    'dharashiv': 'osmanabad',
    'yawatmal': 'yavatmal',
    'bid': 'beed',
}

# Maharashtra geographic bounding box for verifying sample coordinates
MAHARASHTRA_BOUNDS = {
    'lat_min': 15.5,
    'lat_max': 22.3,
    'lon_min': 72.5,
    'lon_max': 81.0,
}

# Raw CGWB chemical column -> XGBoost model feature mapping (matching Sakshi's training pipeline)
RAW_CHEM_FEATURE_MAP = {
    'Potential of Hydrogen (pH)': 'pH',
    'Electric Conductivity (μS/cm)': 'Electrical_Conductivity',
    'Total Dissolved Solids (mg/L)': 'TDS',
    'Total Hardness (mgCaCO3/L)': 'Total_Hardness',
    'Calcium (mg/L)': 'Calcium',
    'Magnesium (mg/L)': 'Magnesium',
    'Chloride (mg/L)': 'Chloride',
    'Sulphate (mg/L)': 'Sulphate',
    'Iron(mg/L)': 'Iron',
    'Bicarbonate (mg/L)': 'Bicarbonate',
    'Sodium (mg/L)': 'Sodium',
}

class ClassificationService:
    # Official Bureau of Indian Standards (BIS IS 10500:2012) Acceptable Limits
    BIS_STANDARDS = {
        'pH': {'min': 6.5, 'max': 8.5, 'unit': '', 'desc': 'Permissible drinking water pH range is 6.5 to 8.5.'},
        'TDS': {'max': 500.0, 'unit': 'mg/L', 'desc': 'Acceptable Total Dissolved Solids limit is 500 mg/L.'},
        'Total_Hardness': {'max': 200.0, 'unit': 'mg/L', 'desc': 'Acceptable total hardness as CaCO3 is 200 mg/L.'},
        'Calcium': {'max': 75.0, 'unit': 'mg/L', 'desc': 'Acceptable calcium concentration is 75 mg/L.'},
        'Magnesium': {'max': 30.0, 'unit': 'mg/L', 'desc': 'Acceptable magnesium concentration is 30 mg/L.'},
        'Chloride': {'max': 250.0, 'unit': 'mg/L', 'desc': 'Acceptable chloride concentration is 250 mg/L.'},
        'Sulphate': {'max': 200.0, 'unit': 'mg/L', 'desc': 'Acceptable sulphate concentration is 200 mg/L.'},
        'Iron': {'max': 1.0, 'unit': 'mg/L', 'desc': 'Acceptable dissolved iron concentration is 1.0 mg/L.'}
    }

    def __init__(self):
        self.model_artifact: Optional[Dict[str, Any]] = None
        self.pipeline = None
        self.feature_names: List[str] = []
        self.is_initialized = False

    def initialize(self):
        if self.is_initialized:
            return

        model_path = settings.get_absolute_path(settings.CLASSIFICATION_MODEL_PATH)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Classification model artifact not found at: {model_path}")

        print(f"[ClassificationService] Loading water quality model from {model_path}...")
        self.model_artifact = joblib.load(model_path)
        self.pipeline = self.model_artifact['pipeline']
        self.feature_names = self.model_artifact['features']
        self.is_initialized = True
        print(f"[ClassificationService] Initialized with {len(self.feature_names)} features: {self.feature_names}")

    def classify_potability(self, req: WaterPotabilityRequest) -> WaterPotabilityResponse:
        if not self.is_initialized:
            self.initialize()

        # Handle domain-specific fallback for TDS: TDS = EC * 0.64
        tds_calculated = False
        tds_val = req.TDS
        if tds_val is None:
            tds_val = round(req.Electrical_Conductivity * 0.64, 2)
            tds_calculated = True

        feature_values = {
            'pH': req.pH,
            'Electrical_Conductivity': req.Electrical_Conductivity,
            'TDS': tds_val,
            'Total_Hardness': req.Total_Hardness,
            'Calcium': req.Calcium,
            'Magnesium': req.Magnesium,
            'Chloride': req.Chloride,
            'Sulphate': req.Sulphate,
            'Iron': req.Iron,
            'Bicarbonate': req.Bicarbonate,
            'Sodium': req.Sodium
        }

        # Check BIS physicochemical compliance
        exceeded: List[ExceededParameter] = []
        for param, limits in self.BIS_STANDARDS.items():
            val = feature_values.get(param)
            if val is not None:
                if 'min' in limits and val < limits['min']:
                    exceeded.append(ExceededParameter(
                        parameter=param,
                        observed_value=val,
                        acceptable_limit=f">={limits['min']} {limits['unit']}".strip(),
                        description=f"{param} is below the minimum permissible limit ({val} < {limits['min']})."
                    ))
                if 'max' in limits and val > limits['max']:
                    exceeded.append(ExceededParameter(
                        parameter=param,
                        observed_value=val,
                        acceptable_limit=f"<={limits['max']} {limits['unit']}".strip(),
                        description=f"{param} exceeds the maximum permissible limit ({val} > {limits['max']})."
                    ))

        # Build ordered DataFrame matching the exact 11 features expected by the pipeline
        ordered_df = pd.DataFrame([{f: feature_values[f] for f in self.feature_names}])

        # Predict
        pred_code = int(self.pipeline.predict(ordered_df)[0])
        prob_dist = self.pipeline.predict_proba(ordered_df)[0]
        prob_non_potable = round(float(prob_dist[0]), 4)
        prob_potable = round(float(prob_dist[1]), 4)

        potability_label = "Potable" if pred_code == 1 else "Non-Potable"
        confidence_score = max(prob_potable, prob_non_potable)

        return WaterPotabilityResponse(
            potability_code=pred_code,
            potability_label=potability_label,
            probability_potable=prob_potable,
            probability_non_potable=prob_non_potable,
            confidence_score=confidence_score,
            standards_basis="BIS IS 10500:2012 Drinking Water Specification",
            exceeded_parameters=exceeded,
            input_tds_calculated=tds_calculated
        )

    @staticmethod
    def _normalize_district_name(raw_name: Any) -> str:
        if raw_name is None or (isinstance(raw_name, float) and np.isnan(raw_name)):
            return ""
        cleaned = str(raw_name).strip().lower()
        return DISTRICT_ALIASES.get(cleaned, cleaned)

    @staticmethod
    def _is_valid_maharashtra_coord(lat: Any, lon: Any) -> bool:
        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except (TypeError, ValueError):
            return False
        if np.isnan(lat_f) or np.isnan(lon_f):
            return False
        return (
            MAHARASHTRA_BOUNDS['lat_min'] <= lat_f <= MAHARASHTRA_BOUNDS['lat_max']
            and MAHARASHTRA_BOUNDS['lon_min'] <= lon_f <= MAHARASHTRA_BOUNDS['lon_max']
        )

    def build_district_coverage(
        self,
        df_locations: pd.DataFrame,
        df_predictions: Optional[pd.DataFrame] = None,
    ) -> DistrictClassificationCoverageResponse:
        """Aggregate district-level potability coverage across all 33 Maharashtra districts."""
        loc_df = df_locations.copy()
        loc_df.columns = [c.strip() for c in loc_df.columns]

        district_centroids = (
            loc_df.groupby('districts', as_index=False)
            .agg(
                latitude=('Latitude', 'mean'),
                longitude=('Longitude', 'mean'),
                monitoring_locations_count=('location_id', 'count'),
            )
            .sort_values('districts')
        )

        canonical_lookup: Dict[str, str] = {
            self._normalize_district_name(d): str(d)
            for d in district_centroids['districts']
        }

        district_stats: Dict[str, Dict[str, int]] = {
            str(d): {'tested': 0, 'potable': 0, 'non_potable': 0, 'actual': 0, 'simulated': 0}
            for d in district_centroids['districts']
        }
        verified_stations: List[VerifiedClassificationStation] = []
        out_of_state_count = 0
        out_of_state_districts: List[str] = []

        if df_predictions is not None and not df_predictions.empty:
            pred_df = df_predictions.copy()
            pred_df.columns = [c.strip() for c in pred_df.columns]
            seen_out_districts = set()

            for idx, row in pred_df.iterrows():
                raw_state = row.get('State')
                if raw_state is not None and not (isinstance(raw_state, float) and np.isnan(raw_state)):
                    if str(raw_state).strip().lower() != 'maharashtra':
                        out_of_state_count += 1
                        raw_dist = row.get('District')
                        if raw_dist is not None and str(raw_dist).strip():
                            seen_out_districts.add(str(raw_dist).strip())
                        continue

                raw_dist = row.get('District')
                norm_dist = self._normalize_district_name(raw_dist)
                canonical_dist = canonical_lookup.get(norm_dist)

                if not canonical_dist:
                    out_of_state_count += 1
                    if raw_dist is not None and str(raw_dist).strip():
                        seen_out_districts.add(str(raw_dist).strip())
                    continue

                pred_code = row.get('Predicted_Potable')
                if pred_code is None or (isinstance(pred_code, float) and np.isnan(pred_code)):
                    label_str = str(row.get('Predicted_Potability_Label') or row.get('Potability_Label') or '').strip().lower()
                    if label_str == 'potable':
                        pred_code = 1
                    elif label_str == 'non-potable':
                        pred_code = 0
                    else:
                        continue
                pred_int = 1 if int(pred_code) == 1 else 0

                sample_source = str(row.get('Source') or 'Actual').strip()
                is_simulated = sample_source.lower() == 'simulated'

                district_stats[canonical_dist]['tested'] += 1
                if pred_int == 1:
                    district_stats[canonical_dist]['potable'] += 1
                else:
                    district_stats[canonical_dist]['non_potable'] += 1
                if is_simulated:
                    district_stats[canonical_dist]['simulated'] += 1
                else:
                    district_stats[canonical_dist]['actual'] += 1

                if self._is_valid_maharashtra_coord(row.get('Latitude'), row.get('Longitude')):
                    prob_val = row.get('Potability_Probability')
                    prob_float = round(float(prob_val), 4) if prob_val is not None and not pd.isna(prob_val) else None
                    verified_stations.append(
                        VerifiedClassificationStation(
                            id=f"dataset-{canonical_dist.lower()}-{idx}",
                            name=str(row.get('Station') or f"{canonical_dist} Station"),
                            district=canonical_dist,
                            latitude=round(float(row['Latitude']), 6),
                            longitude=round(float(row['Longitude']), 6),
                            potability_code=pred_int,
                            potability_label='Potable' if pred_int == 1 else 'Non-Potable',
                            probability_potable=prob_float,
                            source='Simulated Model Prediction' if is_simulated else 'Classification Dataset',
                        )
                    )

            out_of_state_districts = sorted(seen_out_districts)

        districts_out: List[DistrictClassificationSummary] = []
        districts_with_data = 0
        total_tested = 0
        total_potable = 0
        total_non_potable = 0
        simulated_districts_count = 0
        actual_districts_count = 0

        for _, row in district_centroids.iterrows():
            dist_name = str(row['districts'])
            stats = district_stats[dist_name]
            tested = stats['tested']
            potable = stats['potable']
            non_potable = stats['non_potable']
            is_sim_dist = stats['simulated'] > 0 or tested == 0
            source_label = 'Simulated' if is_sim_dist else 'Actual'

            total_tested += tested
            total_potable += potable
            total_non_potable += non_potable

            if tested >= 1:
                districts_with_data += 1
                if source_label == 'Actual':
                    actual_districts_count += 1
                else:
                    simulated_districts_count += 1
                potability_pct = round((potable / tested) * 100.0, 1)
                dominant = 'Potable' if potable >= non_potable else 'Non-Potable'
                status = dominant
                if potable > 0 and non_potable > 0:
                    note = (
                        f"Dominant class: {dominant} ({potable} Potable, {non_potable} Non-Potable). "
                        f"Classified via XGBoost pipeline ({source_label} 11-parameter inputs)."
                    )
                else:
                    note = (
                        f"All {tested} samples classified as {dominant} via XGBoost pipeline "
                        f"({source_label} 11-parameter inputs)."
                    )
            else:
                # Fallback safety if dataset omits a district
                potability_pct = 0.0
                dominant = 'Non-Potable'
                status = 'Non-Potable'
                source_label = 'Simulated'
                note = "District summary awaiting chemical sample ingestion."

            districts_out.append(
                DistrictClassificationSummary(
                    district=dist_name,
                    latitude=round(float(row['latitude']), 6),
                    longitude=round(float(row['longitude']), 6),
                    monitoring_locations_count=int(row['monitoring_locations_count']),
                    tested_samples=tested,
                    potable_samples=potable,
                    non_potable_samples=non_potable,
                    potability_percentage=potability_pct,
                    dominant_classification=dominant,
                    classification_source=source_label,
                    status=status,
                    has_verified_coordinates=True,
                    data_source_note=note,
                )
            )

        out_note = (
            f"Note: Original CGWB raw file contains {out_of_state_count} out-of-state records ({', '.join(out_of_state_districts)}). "
            if out_of_state_count > 0
            else ""
        )
        scope_note = (
            f"{out_note}"
            f"All {len(districts_out)} Maharashtra districts evaluated via existing XGBoost pipeline "
            f"({total_tested} samples: {total_potable} Potable, {total_non_potable} Non-Potable; "
            f"{actual_districts_count} Actual / {simulated_districts_count} Simulated districts)."
        )

        return DistrictClassificationCoverageResponse(
            total_districts=len(districts_out),
            districts_with_data=districts_with_data,
            districts_without_data=len(districts_out) - districts_with_data,
            total_tested_samples=total_tested,
            total_potable_samples=total_potable,
            total_non_potable_samples=total_non_potable,
            districts=districts_out,
            verified_stations=verified_stations,
            dataset_scope_note=scope_note,
        )

    def classify_chemical_dataframe(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Classify raw chemical water-quality records using the existing XGBoost pipeline."""
        if not self.is_initialized:
            self.initialize()

        df = df_raw.copy()
        df.columns = [c.strip() for c in df.columns]

        rename_cols = {src: dst for src, dst in RAW_CHEM_FEATURE_MAP.items() if src in df.columns}
        if rename_cols:
            df = df.rename(columns=rename_cols)

        for feat in self.feature_names:
            if feat not in df.columns:
                df[feat] = np.nan
            df[feat] = pd.to_numeric(df[feat], errors='coerce')

        # Standard domain fallback: TDS = 0.64 * EC when TDS is missing
        if 'TDS' in df.columns and 'Electrical_Conductivity' in df.columns:
            df['TDS'] = df['TDS'].fillna(df['Electrical_Conductivity'] * 0.64)

        X = df[self.feature_names]
        preds = self.pipeline.predict(X)
        probs = self.pipeline.predict_proba(X)[:, 1]

        df['Predicted_Potable'] = preds.astype(int)
        df['Predicted_Potability_Label'] = np.where(df['Predicted_Potable'] == 1, 'Potable', 'Non-Potable')
        df['Potability_Probability'] = np.round(probs.astype(float), 4)
        return df

    def get_district_classification_coverage(self) -> DistrictClassificationCoverageResponse:
        if not self.is_initialized:
            self.initialize()

        locations_path = settings.get_absolute_path(settings.STATEWIDE_LOCATIONS_PATH)
        if not os.path.exists(locations_path):
            raise FileNotFoundError(f"Statewide groundwater locations file not found at: {locations_path}")
        df_locations = pd.read_csv(locations_path)

        raw_path = settings.get_absolute_path(settings.CLASSIFICATION_RAW_DATA_PATH)
        preds_path = settings.get_absolute_path(settings.CLASSIFICATION_PREDICTIONS_PATH)
        sim_path = settings.get_absolute_path(settings.CLASSIFICATION_SIMULATED_DATA_PATH)

        frames: List[pd.DataFrame] = []
        if os.path.exists(raw_path):
            df_raw = pd.read_csv(raw_path)
            df_raw_classified = self.classify_chemical_dataframe(df_raw)
            df_raw_classified['Source'] = 'Actual'
            frames.append(df_raw_classified)
        elif os.path.exists(preds_path):
            df_pred = pd.read_csv(preds_path)
            df_pred['Source'] = 'Actual'
            frames.append(df_pred)

        if os.path.exists(sim_path):
            df_sim = pd.read_csv(sim_path)
            df_sim_classified = self.classify_chemical_dataframe(df_sim)
            if 'Source' not in df_sim_classified.columns:
                df_sim_classified['Source'] = 'Simulated'
            frames.append(df_sim_classified)

        df_combined = pd.concat(frames, ignore_index=True) if frames else None
        return self.build_district_coverage(df_locations=df_locations, df_predictions=df_combined)

classification_service = ClassificationService()
