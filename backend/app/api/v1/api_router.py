from fastapi import APIRouter
from app.api.v1.endpoints.regression import router as regression_router
from app.api.v1.endpoints.classification import router as classification_router
from app.api.v1.endpoints.spatial import router as spatial_router
from app.api.v1.endpoints.routing import router as routing_router

api_router = APIRouter()

# Module 1: Ragini - Groundwater Level Prediction
api_router.include_router(regression_router, tags=["Ragini - Groundwater Regression"])

# Module 2: Sakshi - Water Quality Classification
api_router.include_router(classification_router, tags=["Sakshi - Water Quality Classification"])

# Module 3A: Vedangi - Statewide Spatial Search
api_router.include_router(spatial_router, tags=["Vedangi - Statewide Spatial Search"])

# Module 3B: Vedangi - Pune Road Network Routing
api_router.include_router(routing_router, tags=["Vedangi - Pune Road Routing"])
