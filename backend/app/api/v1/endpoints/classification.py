from fastapi import APIRouter
from app.schemas.classification import (
    WaterPotabilityRequest,
    WaterPotabilityResponse,
    DistrictClassificationCoverageResponse,
)
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


@router.get(
    "/classification/district-coverage",
    response_model=DistrictClassificationCoverageResponse,
    summary="Maharashtra 33-District Water Quality Classification Coverage",
    description=(
        "Returns district-level water quality potability coverage across all 33 Maharashtra districts "
        "classified by the existing XGBoost pipeline using verified CGWB district coordinates, "
        "actual Maharashtra chemical records where available, and clearly labelled simulated 11-parameter inputs."
    )
)
def get_classification_district_coverage() -> DistrictClassificationCoverageResponse:
    return classification_service.get_district_classification_coverage()
