import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

@pytest.fixture(scope="module")
def client():
    # Lifespan executes with TestClient context
    with TestClient(app) as test_client:
        yield test_client

# -------------------------------------------------------------
# 1. SYSTEM HEALTH AND ROOT TESTS
# -------------------------------------------------------------
def test_root_and_health(client):
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["status"] == "online"

    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    data = res_health.json()
    assert data["status"] == "healthy"
    assert data["services"]["regression"] is True
    assert data["services"]["classification"] is True
    assert data["services"]["spatial"] is True
    assert data["services"]["routing"] is True

# -------------------------------------------------------------
# 2. REGRESSION ENDPOINT TESTS (RAGINI EXPERIMENT B)
# -------------------------------------------------------------
def test_regression_historical_lookup(client):
    payload = {
        "mode": "historical_lookup",
        "well_id": "W153803073591301",
        "prediction_date": "2024-05-15"
    }
    res = client.post("/api/v1/predict/water-level", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "historical_lookup"
    assert data["well_id"] == "W153803073591301"
    assert "predicted_water_level_m_bgl" in data
    assert isinstance(data["predicted_water_level_m_bgl"], float)
    assert data["predicted_water_level_m_bgl"] > 0
    assert data["model_used"] == "7. KNN Regressor (k=7)"
    assert "confidence_interval" not in data  # Safeguard: no unsupported intervals
    assert data["evaluation_context"]["test_r2"] == 0.7766

def test_regression_custom_scenario(client):
    payload = {
        "mode": "custom_scenario",
        "district_name": "Pune",
        "season": "Post-Monsoon",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "well_depth_m": 12.0,
        "lag_1": 3.5,
        "lag_2": 4.2,
        "lag_4": 3.8,
        "past_rolling_mean_3": 3.85,
        "past_rolling_std_3": 0.35,
        "rain_prior_30d": 150.0,
        "rain_prior_60d": 320.0,
        "rain_prior_90d": 450.0,
        "rain_prior_180d": 500.0
    }
    res = client.post("/api/v1/predict/water-level", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "custom_scenario"
    assert isinstance(data["predicted_water_level_m_bgl"], float)
    # Safeguard: Do not show historical actual values or prediction errors when no actual observation exists
    assert data["historical_actual_m_bgl"] is None
    assert data["absolute_error_m"] is None

def test_regression_invalid_well(client):
    payload = {
        "mode": "historical_lookup",
        "well_id": "NON_EXISTENT_WELL_999999"
    }
    res = client.post("/api/v1/predict/water-level", json=payload)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_regression_wells_and_districts(client):
    res_dist = client.get("/api/v1/regression/districts")
    assert res_dist.status_code == 200
    districts = res_dist.json()
    assert len(districts) > 20
    assert "Pune" in districts

    res_wells = client.get("/api/v1/regression/wells?district=Pune&limit=10")
    assert res_wells.status_code == 200
    data = res_wells.json()
    assert data["total"] > 0
    assert len(data["wells"]) <= 10
    assert data["wells"][0]["district"].lower() == "pune"

    res_detail = client.get("/api/v1/regression/wells/W153803073591301")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["well_id"] == "W153803073591301"
    assert len(detail["historical_records"]) >= 15

# -------------------------------------------------------------
# 3. WATER QUALITY CLASSIFICATION TESTS (SAKSHI)
# -------------------------------------------------------------
def test_classification_potable(client):
    # Compliant water parameters within BIS IS 10500:2012
    payload = {
        "pH": 7.2,
        "Electrical_Conductivity": 600.0,
        "TDS": 384.0,
        "Total_Hardness": 180.0,
        "Calcium": 50.0,
        "Magnesium": 25.0,
        "Chloride": 140.0,
        "Sulphate": 90.0,
        "Iron": 0.1,
        "Bicarbonate": 200.0,
        "Sodium": 45.0
    }
    res = client.post("/api/v1/classify/water-potability", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["potability_code"] == 1
    assert data["potability_label"] == "Potable"
    assert data["probability_potable"] > 0.8
    assert len(data["exceeded_parameters"]) == 0
    assert "Advisory:" in data["regulatory_advisory"]

def test_classification_non_potable_exceeded(client):
    # Non-compliant sample exceeding pH, TDS, Sulphate, Iron
    payload = {
        "pH": 9.2,
        "Electrical_Conductivity": 2200.0,
        "TDS": 1408.0,
        "Total_Hardness": 350.0,
        "Calcium": 90.0,
        "Magnesium": 45.0,
        "Chloride": 320.0,
        "Sulphate": 280.0,
        "Iron": 1.8,
        "Bicarbonate": 350.0,
        "Sodium": 120.0
    }
    res = client.post("/api/v1/classify/water-potability", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["potability_code"] == 0
    assert data["potability_label"] == "Non-Potable"
    assert len(data["exceeded_parameters"]) >= 3
    exceeded_names = [e["parameter"] for e in data["exceeded_parameters"]]
    assert "pH" in exceeded_names
    assert "TDS" in exceeded_names
    assert "Sulphate" in exceeded_names

def test_classification_tds_fallback(client):
    # Omitting TDS: backend should calculate TDS = 0.64 * EC = 320.0
    payload = {
        "pH": 7.4,
        "Electrical_Conductivity": 500.0,
        "Total_Hardness": 150.0,
        "Calcium": 40.0,
        "Magnesium": 20.0,
        "Chloride": 100.0,
        "Sulphate": 75.0,
        "Iron": 0.05,
        "Bicarbonate": 180.0,
        "Sodium": 30.0
    }
    res = client.post("/api/v1/classify/water-potability", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["input_tds_calculated"] is True


def test_classification_district_coverage_actual(client):
    res = client.get("/api/v1/classification/district-coverage")
    assert res.status_code == 200
    data = res.json()
    assert data["total_districts"] == 33
    assert len(data["districts"]) == 33
    assert data["districts_with_data"] == 33
    assert data["districts_without_data"] == 0
    assert data["total_tested_samples"] == 165
    assert data["total_potable_samples"] == 97
    assert data["total_non_potable_samples"] == 68
    potable_dists = sum(1 for d in data["districts"] if d["dominant_classification"] == "Potable")
    non_potable_dists = sum(1 for d in data["districts"] if d["dominant_classification"] == "Non-Potable")
    assert potable_dists == 20
    assert non_potable_dists == 13
    assert potable_dists + non_potable_dists == 33
    assert "Andaman" in data["dataset_scope_note"]
    assert "Simulated" in data["dataset_scope_note"]
    for d in data["districts"]:
        assert 15.5 <= d["latitude"] <= 22.3
        assert 72.5 <= d["longitude"] <= 81.0
        assert d["monitoring_locations_count"] > 0
        assert d["tested_samples"] == 5
        assert d["dominant_classification"] in ("Potable", "Non-Potable")
        assert d["status"] == d["dominant_classification"]
        assert d["classification_source"] == "Simulated"
        assert d["potability_percentage"] is not None


def test_classification_district_coverage_aggregation_scenarios():
    import pandas as pd
    from app.services.classification_service import classification_service
    from app.core.config import settings

    df_locs = pd.read_csv(settings.get_absolute_path(settings.STATEWIDE_LOCATIONS_PATH))
    df_mock = pd.DataFrame([
        # Potable district (Pune: 3 potable, Actual)
        {"District": "Pune", "Station": "P1", "Latitude": 18.52, "Longitude": 73.85, "Predicted_Potable": 1, "Potability_Probability": 0.95, "Source": "Actual"},
        {"District": "Pune", "Station": "P2", "Latitude": 18.55, "Longitude": 73.82, "Predicted_Potable": 1, "Potability_Probability": 0.91, "Source": "Actual"},
        {"District": "Pune", "Station": "P3", "Latitude": 18.49, "Longitude": 73.88, "Predicted_Potable": 1, "Potability_Probability": 0.89, "Source": "Actual"},
        # Non-Potable district (Solapur: 2 non-potable, Actual)
        {"District": "Solapur", "Station": "S1", "Latitude": 17.66, "Longitude": 75.91, "Predicted_Potable": 0, "Potability_Probability": 0.12, "Source": "Actual"},
        {"District": "Solapur", "Station": "S2", "Latitude": 17.68, "Longitude": 75.92, "Predicted_Potable": 0, "Potability_Probability": 0.08, "Source": "Actual"},
        # Mixed district (Nagpur: 2 potable, 1 non-potable, 1 missing GPS coords -> dominant Potable)
        {"District": "Nagpur", "Station": "N1", "Latitude": 21.14, "Longitude": 79.08, "Predicted_Potable": 1, "Potability_Probability": 0.93, "Source": "Simulated"},
        {"District": "Nagpur", "Station": "N2", "Latitude": None, "Longitude": None, "Predicted_Potable": 1, "Potability_Probability": 0.87, "Source": "Simulated"},
        {"District": "Nagpur", "Station": "N3", "Latitude": 21.16, "Longitude": 79.10, "Predicted_Potable": 0, "Potability_Probability": 0.15, "Source": "Simulated"},
    ])

    coverage = classification_service.build_district_coverage(df_locs, df_mock)
    assert coverage.total_districts == 33
    assert coverage.districts_with_data == 3
    assert coverage.total_tested_samples == 8
    assert coverage.total_potable_samples == 5
    assert coverage.total_non_potable_samples == 3
    # Missing GPS row (N2) must not appear as a verified station
    assert len(coverage.verified_stations) == 7

    by_dist = {d.district: d for d in coverage.districts}
    assert by_dist["Pune"].dominant_classification == "Potable"
    assert by_dist["Pune"].classification_source == "Actual"
    assert by_dist["Pune"].potability_percentage == 100.0
    assert by_dist["Solapur"].dominant_classification == "Non-Potable"
    assert by_dist["Solapur"].classification_source == "Actual"
    assert by_dist["Solapur"].potability_percentage == 0.0
    assert by_dist["Nagpur"].dominant_classification == "Potable"
    assert by_dist["Nagpur"].classification_source == "Simulated"
    assert by_dist["Nagpur"].potability_percentage == 66.7


def test_classification_raw_chemical_pipeline_and_state_filtering():
    import pandas as pd
    from app.services.classification_service import classification_service
    from app.core.config import settings

    df_locs = pd.read_csv(settings.get_absolute_path(settings.STATEWIDE_LOCATIONS_PATH))
    df_raw_mh = pd.DataFrame([
        {
            "State": "Maharashtra",
            "District": "Pune",
            "Station": "Test Station P1",
            "Latitude": 18.5529,
            "Longitude": 73.8262,
            "Potential of Hydrogen (pH)": 7.2,
            "Electric Conductivity (μS/cm)": 600.0,
            "Total Dissolved Solids (mg/L)": None,  # Exercise 0.64 * EC fallback
            "Total Hardness (mgCaCO3/L)": 180.0,
            "Calcium (mg/L)": 50.0,
            "Magnesium (mg/L)": 25.0,
            "Chloride (mg/L)": 140.0,
            "Sulphate (mg/L)": 90.0,
            "Iron(mg/L)": 0.1,
            "Bicarbonate (mg/L)": 200.0,
            "Sodium (mg/L)": 45.0,
        },
        {
            "State": "Maharashtra",
            "District": "Pune",
            "Station": "Test Station P2",
            "Latitude": 18.5204,
            "Longitude": 73.8567,
            "Potential of Hydrogen (pH)": 9.2,
            "Electric Conductivity (μS/cm)": 2200.0,
            "Total Dissolved Solids (mg/L)": 1408.0,
            "Total Hardness (mgCaCO3/L)": 350.0,
            "Calcium (mg/L)": 90.0,
            "Magnesium (mg/L)": 45.0,
            "Chloride (mg/L)": 320.0,
            "Sulphate (mg/L)": 280.0,
            "Iron(mg/L)": 1.8,
            "Bicarbonate (mg/L)": 350.0,
            "Sodium (mg/L)": 120.0,
        },
        {
            # Non-Maharashtra row must be excluded by State filter
            "State": "Andaman And Nicobar Islands",
            "District": "South Andaman",
            "Station": "Annikat",
            "Latitude": 11.7086,
            "Longitude": 92.65,
            "Potential of Hydrogen (pH)": 7.4,
            "Electric Conductivity (μS/cm)": 500.0,
            "Total Dissolved Solids (mg/L)": 320.0,
            "Total Hardness (mgCaCO3/L)": 150.0,
            "Calcium (mg/L)": 40.0,
            "Magnesium (mg/L)": 20.0,
            "Chloride (mg/L)": 100.0,
            "Sulphate (mg/L)": 75.0,
            "Iron(mg/L)": 0.05,
            "Bicarbonate (mg/L)": 180.0,
            "Sodium (mg/L)": 30.0,
        },
    ])

    classified = classification_service.classify_chemical_dataframe(df_raw_mh)
    assert list(classified["Predicted_Potable"]) == [1, 0, 1]

    coverage = classification_service.build_district_coverage(df_locs, classified)
    assert coverage.districts_with_data == 1
    assert coverage.total_tested_samples == 2
    assert coverage.total_potable_samples == 1
    assert coverage.total_non_potable_samples == 1
    pune = next(d for d in coverage.districts if d.district == "Pune")
    assert pune.dominant_classification == "Potable"
    assert pune.potability_percentage == 50.0

# -------------------------------------------------------------
# 4. SPATIAL STATEWIDE NEAREST-WELL SEARCH TESTS (VEDANGI)
# -------------------------------------------------------------
def test_spatial_statewide_nearest_well(client):
    payload = {
        "latitude": 18.5204,
        "longitude": 73.8567,
        "max_results": 3
    }
    res = client.post("/api/v1/spatial/nearest-well", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_found"] == 3
    assert len(data["nearest_wells"]) == 3
    # Check that distance is sorted ascending
    dists = [w["distance_km"] for w in data["nearest_wells"]]
    assert dists == sorted(dists)
    # Check well attributes
    assert data["nearest_wells"][0]["district"] == "Pune"
    assert data["nearest_wells"][0]["pune_road_node_id"] is not None

def test_spatial_district_filtered_search(client):
    payload = {
        "latitude": 20.9611,
        "longitude": 78.5625,
        "max_results": 4,
        "filter_district": "Wardha"
    }
    res = client.post("/api/v1/spatial/nearest-well", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_found"] > 0
    for w in data["nearest_wells"]:
        assert w["district"].lower() == "wardha"

def test_spatial_locations_and_districts(client):
    res_dist = client.get("/api/v1/spatial/districts")
    assert res_dist.status_code == 200
    districts = res_dist.json()
    assert len(districts) == 33

    res_locs = client.get("/api/v1/spatial/locations?district=Wardha&limit=10")
    assert res_locs.status_code == 200
    data = res_locs.json()
    assert data["total"] > 0
    assert len(data["locations"]) <= 10
    assert data["locations"][0]["district"].lower() == "wardha"

# -------------------------------------------------------------
# 5. PUNE ROAD ROUTING TESTS (VEDANGI)
# -------------------------------------------------------------
def test_pune_routing_astar(client):
    # Pair 1: Sarati to Sarati (12788595845 -> 12788595830)
    payload = {
        "start_node_id": 12788595845,
        "target_node_id": 12788595830,
        "algorithm": "A*"
    }
    res = client.post("/api/v1/routing/pune", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["algorithm"] == "A*"
    assert abs(data["total_distance_m"] - 227.06) < 0.1
    assert data["edge_count"] == 5
    assert len(data["route_node_ids"]) == 6
    assert data["route_geometry"] is not None
    assert len(data["route_geometry"]) == 6

def test_pune_routing_bidirectional(client):
    payload = {
        "start_node_id": 12788595845,
        "target_node_id": 12788595830,
        "algorithm": "Bidirectional"
    }
    res = client.post("/api/v1/routing/pune", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["edge_count"] == 3
    assert abs(data["total_distance_m"] - 237.65) < 0.1

def test_pune_routing_invalid_node_boundary(client):
    payload = {
        "start_node_id": 9999999999999,
        "target_node_id": 12788595830,
        "algorithm": "A*"
    }
    res = client.post("/api/v1/routing/pune", json=payload)
    assert res.status_code == 404
    assert "strictly restricted to pune district" in res.json()["detail"].lower()
