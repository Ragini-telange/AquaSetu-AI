# AquaGuard AI: Production FastAPI Backend

Unified AI service powering groundwater table depth prediction, drinking water potability classification, statewide spatial nearest-well lookup, and Pune road network graph pathfinding.

---

## 1. System Architecture & Module Separation

The backend cleanly separates the three research modules into independent domain services:

```text
backend/
├── app/
│   ├── main.py                     # FastAPI application factory & lifespan loader
│   ├── core/
│   │   ├── config.py               # Settings & artifact path resolution
│   ├── api/
│   │   └── v1/
│   │       ├── api_router.py       # Central v1 router mount
│   │       └── endpoints/
│   │           ├── regression.py     # Ragini: /api/v1/predict/water-level
│   │           ├── classification.py # Sakshi: /api/v1/classify/water-potability
│   │           ├── spatial.py        # Vedangi: /api/v1/spatial/nearest-well
│   │           └── routing.py        # Vedangi: /api/v1/routing/pune
│   ├── schemas/                    # Pydantic v2 request/response contracts
│   │   ├── regression.py
│   │   ├── classification.py
│   │   ├── spatial.py
│   │   └── routing.py
│   └── services/                   # Independent business & ML inference logic
│       ├── regression_service.py     # KNN (k=7) + 65k historical features repository
│       ├── classification_service.py # XGBoost + BIS IS 10500:2012 compliance engine
│       ├── spatial_service.py        # 4,381 statewide locations + 2D KDTree index
│       └── routing_service.py        # 170k-node Pune OSM graph + 6 pathfinding algorithms
├── cache/
│   └── pune_road_network_cached.joblib # Compressed pre-parsed binary graph cache (10.17 MB)
├── scripts/
│   └── build_graph_cache.py        # Regeneration script for binary road network cache
├── tests/
│   └── test_api_endpoints.py       # Integration tests exercising all 4 endpoints
├── requirements.txt                # Pinned dependencies (scikit-learn==1.6.1)
├── .env.example
└── README.md
```

---

## 2. Environment Setup & Installation

### Prerequisites
- Python **3.10.x** (or 3.11.x) 64-bit
- Windows / Linux / macOS

### Setup Virtual Environment
```bash
cd backend
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Linux / macOS:
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note on Scikit-Learn Compatibility**: `scikit-learn==1.6.1` is strictly pinned to ensure seamless unpickling of all trained pipelines without requiring code monkeypatches or compatibility stubs.

---

## 3. Pune Road Network Graph Cache Management

The OpenStreetMap road network graph for Pune District is originally provided as `pune_road_network.graphml` (199.5 MB XML). To optimize backend cold-start performance, a binary cache is pre-generated:

| Format | File | Disk Size | Cold Startup Load Time |
|---|---|---|---|
| **Raw XML** | `pune_road_network.graphml` | 199.50 MB | 28.6 seconds |
| **Binary Cache** | `pune_road_network_cached.joblib` | 10.17 MB | **7.0 seconds** (4.1x faster) |

### How to Regenerate the Cache
If the underlying `pune_road_network.graphml` is updated or replaced, regenerate the cache using:

```bash
python scripts/build_graph_cache.py
```
This utility automatically reads the raw GraphML, verifies node and edge counts, builds the typed MultiDiGraph, and validates that benchmark routes (e.g. A\* 227.06 m and BFS 237.65 m) match 100%. The original GraphML is preserved untouched.

---

## 4. Running the Backend Server

### Development Mode (with hot-reload)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 5. Running Integration Tests

Run the complete test suite across all four endpoints:

```bash
pytest tests/test_api_endpoints.py -v
```

All tests execute against real project model artifacts and datasets without mock fallbacks.

---

## 6. Endpoints Overview

| Method | Endpoint | Module Owner | Description |
|---|---|---|---|
| `POST` | `/api/v1/predict/water-level` | Ragini | Experiment B KNN Regressor ($k=7$) for historical well lookup or custom scenarios. |
| `POST` | `/api/v1/classify/water-potability` | Sakshi | XGBoost classifier against BIS IS 10500:2012 with itemized physicochemical limit exceedances. |
| `POST` | `/api/v1/spatial/nearest-well` | Vedangi | 2D spatial search across all 4,381 well locations in 33 Maharashtra districts ($< 1\text{ ms}$). |
| `POST` | `/api/v1/routing/pune` | Vedangi | Road network routing on Pune's 170k-node graph with A\*, Bidirectional, BFS, GBFS, IDDFS, DFS. |
