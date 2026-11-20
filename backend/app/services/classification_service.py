import os
import joblib
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.schemas.classification import (
    WaterPotabilityRequest,
    WaterPotabilityResponse,
    ExceededParameter
)

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

classification_service = ClassificationService()
