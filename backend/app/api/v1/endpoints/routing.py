from fastapi import APIRouter
from app.schemas.routing import PuneRoutingRequest, PuneRoutingResponse
from app.services.routing_service import routing_service

router = APIRouter()

@router.post(
    "/routing/pune",
    response_model=PuneRoutingResponse,
    summary="Pune Road Network Pathfinding (6 Algorithms)",
    description=(
        "Executes graph search algorithms on the 170,253-node directed OpenStreetMap road network of Pune District. "
        "Supports six verified algorithms: 'A*' (distance-optimal), 'Bidirectional' (hop-optimal low-expansion), "
        "'BFS' (hop-optimal), 'Greedy_Best_First' (heuristic), 'IDDFS' (depth-bounded), and 'DFS'. "
        "Strictly restricted to Pune District. Returns node sequences and coordinate geometry for mapping."
    )
)
def find_pune_route(request: PuneRoutingRequest) -> PuneRoutingResponse:
    return routing_service.find_route(request)
