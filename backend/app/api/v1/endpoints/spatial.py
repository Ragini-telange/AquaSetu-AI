from fastapi import APIRouter
from app.schemas.spatial import NearestWellRequest, NearestWellResponse
from app.services.spatial_service import spatial_service

router = APIRouter()

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
