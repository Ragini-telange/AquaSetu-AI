from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class PredictionMode(str, Enum):
    HISTORICAL_LOOKUP = "historical_lookup"
    CUSTOM_SCENARIO = "custom_scenario"

class WaterLevelPredictionRequest(BaseModel):
    mode: PredictionMode = Field(
        default=PredictionMode.HISTORICAL_LOOKUP,
        description="Prediction mode: 'historical_lookup' or 'custom_scenario'"
    )
    # Mode A: Historical Lookup Fields
    well_id: Optional[str] = Field(
        None,
        description="CGWB Well ID (e.g. 'W153803073591301') for historical lookup"
    )
    prediction_date: Optional[str] = Field(
        None,
        description="Historical monitoring date (YYYY-MM-DD) between 2021-02-15 and 2025-06-18"
    )
    
    # Mode B: Custom / Scenario Prediction Fields
    district_name: Optional[str] = Field(None, description="Maharashtra District (e.g. 'Pune', 'Wardha')")
    season: Optional[str] = Field(None, description="'Pre-Monsoon', 'Monsoon', 'Post-Monsoon', or 'Winter'")
    latitude: Optional[float] = Field(None, description="Well latitude")
    longitude: Optional[float] = Field(None, description="Well longitude")
    well_depth_m: Optional[float] = Field(None, ge=0.5, le=200.0, description="Total depth of well in meters")
    
    # Lag Features (Past groundwater depth readings)
    lag_1: Optional[float] = Field(None, ge=0.0, description="Most recent prior water level reading (m bgl)")
    lag_2: Optional[float] = Field(None, ge=0.0, description="Water level 2 periods prior (m bgl)")
    lag_4: Optional[float] = Field(None, ge=0.0, description="Water level ~1 year / 4 periods prior (m bgl)")
    past_rolling_mean_3: Optional[float] = Field(None, ge=0.0, description="Rolling mean of past 3 readings (m bgl)")
    past_rolling_std_3: Optional[float] = Field(None, ge=0.0, description="Rolling std dev of past 3 readings (m bgl)")
    
    # Antecedent Rainfall Accumulators
    rain_prior_30d: Optional[float] = Field(None, ge=0.0, description="Cumulative rainfall in prior 30 days (mm)")
    rain_prior_60d: Optional[float] = Field(None, ge=0.0, description="Cumulative rainfall in prior 60 days (mm)")
    rain_prior_90d: Optional[float] = Field(None, ge=0.0, description="Cumulative rainfall in prior 90 days (mm)")
    rain_prior_180d: Optional[float] = Field(None, ge=0.0, description="Cumulative rainfall in prior 180 days (mm)")
    
    # Cyclical Month Encoding (Optional, derived if date given)
    month_sin: Optional[float] = Field(None, ge=-1.0, le=1.0)
    month_cos: Optional[float] = Field(None, ge=-1.0, le=1.0)

class EvaluationContext(BaseModel):
    test_r2: float = 0.7766
    test_mae_m: float = 1.3247
    test_rmse_m: float = 1.9295
    cv_r2_mean: float = 0.7110
    cv_rmse_mean_m: float = 1.9066
    selection_basis: str = "Decisive Winner across all TimeSeriesSplit Cross-Validation Metrics"

class WaterLevelPredictionResponse(BaseModel):
    mode: str
    well_id: Optional[str] = None
    prediction_date: Optional[str] = None
    model_used: str = "7. KNN Regressor (k=7)"
    predicted_water_level_m_bgl: float = Field(..., description="Predicted depth to water table in meters below ground level")
    well_depth_m: Optional[float] = Field(None, description="Physical well depth in meters")
    effective_water_column_m: Optional[float] = Field(None, description="Calculated as well_depth_m - predicted_water_level_m_bgl")
    historical_actual_m_bgl: Optional[float] = Field(None, description="Actual observed water level if an observation exists for this date")
    absolute_error_m: Optional[float] = Field(None, description="Absolute difference between predicted and actual observation")
    features_used: Dict[str, Any] = Field(..., description="Complete 16-feature vector passed into the model pipeline")
    evaluation_context: EvaluationContext = Field(default_factory=EvaluationContext)
