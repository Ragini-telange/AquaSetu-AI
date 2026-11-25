import os
import time
import math
import joblib
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple, List
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.regression import (
    WaterLevelPredictionRequest,
    WaterLevelPredictionResponse,
    PredictionMode,
    EvaluationContext
)

class RegressionService:
    def __init__(self):
        self.model_artifact: Optional[Dict[str, Any]] = None
        self.pipeline = None
        self.df_historical: Optional[pd.DataFrame] = None
        self.well_index: Dict[str, pd.DataFrame] = {}
        self.well_date_index: Dict[Tuple[str, str], pd.Series] = {}
        self.wells_metadata: List[Dict[str, Any]] = []
        self.is_initialized = False

    def initialize(self):
        if self.is_initialized:
            return

        model_path = settings.get_absolute_path(settings.REGRESSION_MODEL_PATH)
        data_path = settings.get_absolute_path(settings.REGRESSION_DATA_PATH)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Regression model artifact not found at: {model_path}")
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Regression dataset not found at: {data_path}")

        print(f"[RegressionService] Loading model artifact from {model_path}...")
        self.model_artifact = joblib.load(model_path)
        self.pipeline = self.model_artifact['pipeline']

        print(f"[RegressionService] Loading historical feature dataset from {data_path}...")
        self.df_historical = pd.read_csv(data_path, low_memory=False)
        self.df_historical['Date'] = pd.to_datetime(self.df_historical['Date']).dt.strftime('%Y-%m-%d')
        
        # Build in-memory lookup cache by well_id
        for well_id, group in self.df_historical.groupby('Well ID'):
            sorted_group = group.sort_values('Date').reset_index(drop=True)
            self.well_index[str(well_id)] = sorted_group

            r = sorted_group.iloc[-1]
            lat = float(r['Latitude']) if ('Latitude' in r and not pd.isna(r['Latitude'])) else None
            lon = float(r['Longitude']) if ('Longitude' in r and not pd.isna(r['Longitude'])) else None
            depth = float(r['Well Depth, m']) if ('Well Depth, m' in r and not pd.isna(r['Well Depth, m'])) else None
            self.wells_metadata.append({
                'well_id': str(well_id),
                'district': str(r.get('District Name', '')),
                'block': str(r.get('Block Name', '')),
                'village': str(r.get('Village', '')),
                'latitude': lat,
                'longitude': lon,
                'well_depth_m': depth,
                'well_type': str(r.get('Well Type (Dug Well, Piezometer)', 'Dug Well')),
                'latest_date': str(r.get('Date', '')),
                'total_observations': len(sorted_group)
            })

        self.is_initialized = True
        print(f"[RegressionService] Initialized with {len(self.well_index)} wells and {len(self.df_historical)} records.")

    def get_wells(self, district: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if not self.is_initialized:
            self.initialize()
        if district:
            d_clean = district.strip().lower()
            res = [w for w in self.wells_metadata if w['district'].lower() == d_clean]
        else:
            res = self.wells_metadata
        if limit and limit > 0:
            return res[:limit]
        return res

    def get_districts(self) -> List[str]:
        if not self.is_initialized:
            self.initialize()
        districts = sorted(list(set(w['district'] for w in self.wells_metadata if w['district'])))
        return districts

    def get_well_details(self, well_id: str) -> Optional[Dict[str, Any]]:
        if not self.is_initialized:
            self.initialize()
        clean_id = str(well_id).strip()
        if clean_id not in self.well_index:
            return None
        group = self.well_index[clean_id]
        records = []
        for _, row in group.iterrows():
            wl = row.get('Water Level, m bgl')
            rain = row.get('Rain_Prior_30d', 0.0)
            records.append({
                'date': str(row.get('Date', '')),
                'water_level_m_bgl': round(float(wl), 2) if not pd.isna(wl) else None,
                'rainfall_30d': round(float(rain), 1) if not pd.isna(rain) else 0.0,
                'season': str(row.get('Season', ''))
            })
        r = group.iloc[-1]
        lat = float(r['Latitude']) if ('Latitude' in r and not pd.isna(r['Latitude'])) else None
        lon = float(r['Longitude']) if ('Longitude' in r and not pd.isna(r['Longitude'])) else None
        depth = float(r['Well Depth, m']) if ('Well Depth, m' in r and not pd.isna(r['Well Depth, m'])) else None
        return {
            'well_id': clean_id,
            'district': str(r.get('District Name', '')),
            'block': str(r.get('Block Name', '')),
            'village': str(r.get('Village', '')),
            'latitude': lat,
            'longitude': lon,
            'well_depth_m': depth,
            'well_type': str(r.get('Well Type (Dug Well, Piezometer)', 'Dug Well')),
            'historical_records': records
        }

    def predict(self, req: WaterLevelPredictionRequest) -> WaterLevelPredictionResponse:
        if not self.is_initialized:
            self.initialize()

        if req.mode == PredictionMode.HISTORICAL_LOOKUP:
            return self._predict_historical(req)
        else:
            return self._predict_scenario(req)

    def _predict_historical(self, req: WaterLevelPredictionRequest) -> WaterLevelPredictionResponse:
        if not req.well_id:
            raise HTTPException(
                status_code=400,
                detail="Field 'well_id' is required for mode 'historical_lookup'."
            )

        well_id = str(req.well_id).strip()
        if well_id not in self.well_index:
            raise HTTPException(
                status_code=404,
                detail=f"Well ID '{well_id}' not found in Maharashtra groundwater repository. Available wells: {len(self.well_index)}."
            )

        well_records = self.well_index[well_id]

        target_date = req.prediction_date
        exact_match = False
        selected_row = None

        if target_date:
            date_match = well_records[well_records['Date'] == target_date]
            if len(date_match) > 0:
                selected_row = date_match.iloc[0]
                exact_match = True
            else:
                # Find closest earlier monitoring observation
                earlier = well_records[well_records['Date'] <= target_date]
                if len(earlier) > 0:
                    selected_row = earlier.iloc[-1]
                else:
                    selected_row = well_records.iloc[0]
        else:
            # Default to latest recorded observation
            selected_row = well_records.iloc[-1]
            target_date = str(selected_row['Date'])
            exact_match = True

        # Extract features
        num_features = self.model_artifact['num_features']
        cat_features = self.model_artifact['cat_features']
        all_feature_cols = num_features + cat_features

        features_dict = {}
        for col in all_feature_cols:
            val = selected_row.get(col, None)
            if pd.isna(val):
                val = None
            elif isinstance(val, (np.floating, float)):
                val = float(val)
            elif isinstance(val, (np.integer, int)):
                val = int(val)
            features_dict[col] = val

        # Predict
        input_df = pd.DataFrame([features_dict])
        pred_val = float(self.pipeline.predict(input_df)[0])
        pred_val = round(pred_val, 2)

        well_depth = float(selected_row.get('Well Depth, m', 0.0)) if not pd.isna(selected_row.get('Well Depth, m')) else None
        effective_col = round(well_depth - pred_val, 2) if well_depth is not None else None

        actual_val = None
        abs_err = None

        # Safeguard: Do not show historical actual values or prediction errors when no actual observation exists for that date
        if exact_match and ('Water Level, m bgl' in selected_row or 'Target_Water_Level' in selected_row):
            raw_actual = selected_row.get('Water Level, m bgl', selected_row.get('Target_Water_Level'))
            if not pd.isna(raw_actual):
                actual_val = round(float(raw_actual), 2)
                abs_err = round(abs(actual_val - pred_val), 2)

        return WaterLevelPredictionResponse(
            mode=req.mode.value,
            well_id=well_id,
            prediction_date=target_date,
            model_used=self.model_artifact.get('model_name', '7. KNN Regressor (k=7)'),
            predicted_water_level_m_bgl=pred_val,
            well_depth_m=well_depth,
            effective_water_column_m=effective_col,
            historical_actual_m_bgl=actual_val,
            absolute_error_m=abs_err,
            features_used=features_dict,
            evaluation_context=EvaluationContext()
        )

    def _predict_scenario(self, req: WaterLevelPredictionRequest) -> WaterLevelPredictionResponse:
        # Require essential spatial context
        district = req.district_name or "Pune"
        season = req.season or "Post-Monsoon"
        lat = req.latitude or 18.5204
        lon = req.longitude or 73.8567
        well_depth = req.well_depth_m or 15.0

        month_sin = req.month_sin if req.month_sin is not None else float(np.sin(2 * np.pi * 10 / 12))
        month_cos = req.month_cos if req.month_cos is not None else float(np.cos(2 * np.pi * 10 / 12))

        features_dict = {
            'Lag_1': req.lag_1 if req.lag_1 is not None else 4.0,
            'Lag_2': req.lag_2 if req.lag_2 is not None else 4.5,
            'Lag_4': req.lag_4 if req.lag_4 is not None else 4.2,
            'Past_Rolling_Mean_3': req.past_rolling_mean_3 if req.past_rolling_mean_3 is not None else 4.25,
            'Past_Rolling_Std_3': req.past_rolling_std_3 if req.past_rolling_std_3 is not None else 0.40,
            'Rain_Prior_30d': req.rain_prior_30d if req.rain_prior_30d is not None else 100.0,
            'Rain_Prior_60d': req.rain_prior_60d if req.rain_prior_60d is not None else 250.0,
            'Rain_Prior_90d': req.rain_prior_90d if req.rain_prior_90d is not None else 350.0,
            'Rain_Prior_180d': req.rain_prior_180d if req.rain_prior_180d is not None else 450.0,
            'Well Depth, m': well_depth,
            'Latitude': lat,
            'Longitude': lon,
            'Month_Sin': month_sin,
            'Month_Cos': month_cos,
            'Season': season,
            'District Name': district
        }

        input_df = pd.DataFrame([features_dict])
        pred_val = round(float(self.pipeline.predict(input_df)[0]), 2)
        effective_col = round(well_depth - pred_val, 2) if well_depth is not None else None

        return WaterLevelPredictionResponse(
            mode=req.mode.value,
            well_id=req.well_id,
            prediction_date=req.prediction_date,
            model_used=self.model_artifact.get('model_name', '7. KNN Regressor (k=7)'),
            predicted_water_level_m_bgl=pred_val,
            well_depth_m=well_depth,
            effective_water_column_m=effective_col,
            historical_actual_m_bgl=None,  # No actual observation exists for hypothetical scenario
            absolute_error_m=None,
            features_used=features_dict,
            evaluation_context=EvaluationContext()
        )

regression_service = RegressionService()
