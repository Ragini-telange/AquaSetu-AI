import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api_router import api_router
from app.services.regression_service import regression_service
from app.services.classification_service import classification_service
from app.services.spatial_service import spatial_service
from app.services.routing_service import routing_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Pre-load models, datasets, and graph cache
    print("=" * 60)
    print("AQUAGUARD AI BACKEND: INITIALIZING SERVICES...")
    print("=" * 60)
    t_start = time.time()
    
    regression_service.initialize()
    classification_service.initialize()
    spatial_service.initialize()
    routing_service.initialize()
    
    print("=" * 60)
    print(f"ALL SERVICES INITIALIZED IN {time.time() - t_start:.2f}s")
    print("AQUAGUARD AI BACKEND READY.")
    print("=" * 60)
    yield
    # Shutdown
    print("Shutting down AquaGuard AI Backend...")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "AquaGuard AI Backend: Unified API for AI-Based Groundwater Level Prediction, "
        "Water Quality Potability Classification, Statewide Spatial Well Search, and Pune Road Network Routing."
    ),
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["System"])
def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_v1": "/api/v1"
    }

@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "regression": regression_service.is_initialized,
            "classification": classification_service.is_initialized,
            "spatial": spatial_service.is_initialized,
            "routing": routing_service.is_initialized
        }
    }
