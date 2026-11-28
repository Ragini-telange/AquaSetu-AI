import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    APP_NAME: str = "AquaGuard AI Backend"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Base workspace directory (defaults to D:\AquaGuard)
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    # Ragini Regression Paths
    REGRESSION_MODEL_PATH: str = "audit/ragini_regression/01_Ragini_Regression/models/best_model_experiment_b_groundwater_rainfall.joblib"
    REGRESSION_DATA_PATH: str = "audit/ragini_regression/01_Ragini_Regression/clean_data/experiment_B_groundwater_rainfall.csv"

    # Sakshi Classification Paths
    CLASSIFICATION_MODEL_PATH: str = "audit/sakshi_classification/project_aiml/models/water_quality_model.pkl"
    CLASSIFICATION_PREDICTIONS_PATH: str = "audit/sakshi_classification/project_aiml/reports/water_quality_station_predictions.csv"
    CLASSIFICATION_RAW_DATA_PATH: str = "audit/sakshi_classification/project_aiml/data/raw/gwq_chemical_parameter_manual_cgwb_an_1961_2025.csv"
    CLASSIFICATION_SIMULATED_DATA_PATH: str = "audit/sakshi_classification/project_aiml/data/maharashtra_simulated_water_quality.csv"

    # Vedangi Geographical Paths
    STATEWIDE_LOCATIONS_PATH: str = "audit/vedangi_geographical_search/AquaGuard_AI1/vedangi_search_module/processed_data/groundwater_locations.csv"
    PUNE_SNAP_PATH: str = "audit/vedangi_geographical_search/AquaGuard_AI1/vedangi_search_module/processed_data/pune_location_node_snap.csv"
    PUNE_GRAPH_RAW_PATH: str = "audit/vedangi_geographical_search/AquaGuard_AI1/vedangi_search_module/pune_road_network.graphml"
    PUNE_GRAPH_CACHE_PATH: str = "backend/cache/pune_road_network_cached.joblib"

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]

    def get_absolute_path(self, relative_path: str) -> str:
        if os.path.isabs(relative_path):
            return relative_path
        return os.path.normpath(os.path.join(self.BASE_DIR, relative_path))

settings = Settings()
