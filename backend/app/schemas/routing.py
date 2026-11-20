from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class SearchAlgorithm(str, Enum):
    ASTAR = "A*"
    BIDIRECTIONAL = "Bidirectional"
    BFS = "BFS"
    GREEDY_BEST_FIRST = "Greedy_Best_First"
    IDDFS = "IDDFS"
    DFS = "DFS"

class PuneRoutingRequest(BaseModel):
    start_node_id: int = Field(..., description="Starting road network node ID in Pune (e.g. 12788595845)")
    target_node_id: int = Field(..., description="Target road network node ID in Pune (e.g. 12788595830)")
    algorithm: SearchAlgorithm = Field(
        default=SearchAlgorithm.ASTAR,
        description="Search algorithm: 'A*', 'Bidirectional', 'BFS', 'Greedy_Best_First', 'IDDFS', or 'DFS'"
    )
    max_depth: Optional[int] = Field(
        25, ge=1, le=100,
        description="Exploration depth limit for IDDFS algorithm (default: 25)"
    )

class PuneRoutingResponse(BaseModel):
    success: bool
    algorithm: str
    start_node_id: int
    target_node_id: int
    total_distance_m: Optional[float] = Field(None, description="Shortest accumulated road route distance in meters")
    total_distance_km: Optional[float] = Field(None, description="Shortest accumulated road route distance in kilometers")
    edge_count: Optional[int] = Field(None, description="Number of road segments / hops in route")
    expanded_nodes: int = Field(..., description="Number of graph nodes expanded during search")
    execution_time_ms: float = Field(..., description="Search execution latency in milliseconds")
    route_node_ids: Optional[List[int]] = Field(None, description="Ordered sequence of node IDs along the route")
    route_geometry: Optional[List[List[float]]] = Field(None, description="Ordered [latitude, longitude] pairs for map rendering")
    error_message: Optional[str] = None
    network_scope: str = "Strictly Pune District Road Network (170,253 nodes). Routing outside Pune is not supported."
