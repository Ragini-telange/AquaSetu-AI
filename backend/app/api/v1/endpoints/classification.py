from fastapi import APIRouter
from app.schemas.classification import WaterPotabilityRequest, WaterPotabilityResponse
from app.services.classification_service import classification_service

router = APIRouter()

@router.post(
    "/classify/water-potability",
    response_model=WaterPotabilityResponse,
    summary="Classify Drinking Water Potability",
    description=(
        "Classifies water potability against Bureau of Indian Standards (BIS IS 10500:2012) "
        "using Sakshi's verified XGBoost classification pipeline. "
        "Requires the exact 11 physicochemical features. Applies automatic TDS estimation (TDS = 0.64 * EC) "
        "if TDS is omitted. Includes an itemized list of exceeded BIS limits and official advisory notice."
    )
)
def classify_water_potability(request: WaterPotabilityRequest) -> WaterPotabilityResponse:
    return classification_service.classify_potability(request)
