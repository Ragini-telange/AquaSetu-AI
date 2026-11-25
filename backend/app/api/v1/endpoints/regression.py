from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.regression import (
    WaterLevelPredictionRequest,
    WaterLevelPredictionResponse,
    WellsListResponse,
    WellDetailsResponse,
    WellMetadataItem
)
from app.services.regression_service import regression_service

router = APIRouter()

@router.get(
    "/regression/wells",
    response_model=WellsListResponse,
    summary="List Groundwater Monitoring Wells",
    description="Retrieves monitoring wells with verified coordinates and historical coverage from the Maharashtra CGWB repository."
)
def list_wells(
    district: Optional[str] = Query(None, description="Filter wells by Maharashtra district name (e.g., 'Pune', 'Wardha')"),
    limit: Optional[int] = Query(None, ge=1, le=5000, description="Optional maximum wells to return")
) -> WellsListResponse:
    wells_data = regression_service.get_wells(district=district, limit=limit)
    return WellsListResponse(
        total=len(wells_data),
        district_filter=district,
        wells=[WellMetadataItem(**w) for w in wells_data]
    )

@router.get(
    "/regression/wells/{well_id}",
    response_model=WellDetailsResponse,
    summary="Get Well Details and Historical Series",
    description="Retrieves physical metadata and historical quarterly observations for a specific CGWB monitoring well."
)
def get_well_details(well_id: str) -> WellDetailsResponse:
    details = regression_service.get_well_details(well_id)
    if not details:
        raise HTTPException(
            status_code=404,
            detail=f"Well ID '{well_id}' not found in Maharashtra groundwater repository."
        )
    return WellDetailsResponse(**details)

@router.get(
    "/regression/districts",
    response_model=List[str],
    summary="List Available Districts",
    description="Returns all unique Maharashtra districts present in the regression groundwater repository."
)
def list_districts() -> List[str]:
    return regression_service.get_districts()

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
