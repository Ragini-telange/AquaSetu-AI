from fastapi import APIRouter, Depends
from app.schemas.regression import WaterLevelPredictionRequest, WaterLevelPredictionResponse
from app.services.regression_service import regression_service

router = APIRouter()

@router.post(
    "/predict/water-level",
    response_model=WaterLevelPredictionResponse,
    summary="Predict Groundwater Table Depth (m bgl)",
    description=(
        "Predicts groundwater level using Ragini's verified Experiment B KNN Regressor (k=7). "
        "Supports 'historical_lookup' (retrieves precomputed lags and antecedent rainfall for a selected well) "
        "and 'custom_scenario' (evaluates user-provided hydrological scenarios). "
        "Does not display actual values or prediction errors for dates where no observation exists."
    )
)
def predict_water_level(request: WaterLevelPredictionRequest) -> WaterLevelPredictionResponse:
    return regression_service.predict(request)
