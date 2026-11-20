from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class NearestWellRequest(BaseModel):
    latitude: float = Field(..., ge=15.0, le=23.0, description="Query latitude in Maharashtra (approx 15.6 - 22.1)")
    longitude: float = Field(..., ge=72.0, le=81.5, description="Query longitude in Maharashtra (approx 72.6 - 80.9)")
    max_results: int = Field(5, ge=1, le=50, description="Maximum nearest wells to return")
    filter_district: Optional[str] = Field(None, description="Optional district name filter (e.g. 'Pune', 'Solapur', 'Wardha')")

class WellLocationItem(BaseModel):
    location_id: int
    district: str
    block: str
    village: str
    latitude: float
    longitude: float
    distance_km: float
    well_ids: List[str]
    num_wells: int
    pune_road_node_id: Optional[int] = Field(None, description="Snapped Pune road network node ID if well is located in Pune district")
    snap_distance_m: Optional[float] = Field(None, description="Distance from well coordinates to road network node in meters")

class NearestWellResponse(BaseModel):
    query_coords: Dict[str, float]
    total_found: int
    filter_district: Optional[str] = None
    nearest_wells: List[WellLocationItem]
    coverage_note: str = "Statewide spatial nearest-neighbor search across all 33 Maharashtra districts (4,381 well locations)."
