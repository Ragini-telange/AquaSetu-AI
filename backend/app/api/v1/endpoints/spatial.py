from typing import Optional, List
from fastapi import APIRouter, Query
from app.schemas.spatial import NearestWellRequest, NearestWellResponse, LocationsListResponse, WellLocationItem
from app.services.spatial_service import spatial_service

router = APIRouter()

@router.get(
    "/spatial/locations",
    response_model=LocationsListResponse,
    summary="List Statewide Well Locations",
    description="Retrieves groundwater monitoring locations with coordinates and Pune road snap info."
)
def list_locations(
    district: Optional[str] = Query(None, description="Optional district name filter"),
    limit: Optional[int] = Query(None, ge=1, le=5000, description="Optional limit of locations")
) -> LocationsListResponse:
    locs = spatial_service.get_locations(district=district, limit=limit)
    return LocationsListResponse(
        total=len(locs),
        district_filter=district,
        locations=[WellLocationItem(**loc) for loc in locs]
    )

@router.get(
    "/spatial/districts",
    response_model=List[str],
    summary="List Districts in Spatial Repository",
    description="Returns all unique Maharashtra districts present in the statewide spatial location database."
)
def list_spatial_districts() -> List[str]:
    return spatial_service.get_districts()

@router.post(
    "/spatial/nearest-well",
    response_model=NearestWellResponse,
    summary="Statewide Nearest-Well Spatial Search",
    description=(
        "Performs spatial nearest-neighbor search across all 4,381 well locations in all 33 Maharashtra districts "
        "using fast 2D spatial indexing (KDTree + Haversine calculation). "
        "Allows optional district filtering. Cross-references snapped Pune road network node IDs for Pune wells."
    )
)
def find_nearest_wells(request: NearestWellRequest) -> NearestWellResponse:
    return spatial_service.find_nearest_wells(request)
