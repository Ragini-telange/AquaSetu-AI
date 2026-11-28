/**
 * AquaSetu API Client Service
 * Connects directly to the FastAPI backend running at http://localhost:8000
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// -------------------------------------------------------------
// Type Definitions matching Backend Pydantic Schemas
// -------------------------------------------------------------

export interface EvaluationContext {
  test_r2: number;
  test_mae_m: number;
  test_rmse_m: number;
  cv_r2_mean: number;
  cv_rmse_mean_m: number;
  selection_basis: string;
}

export interface WaterLevelPredictionRequest {
  mode: 'historical_lookup' | 'custom_scenario';
  well_id?: string;
  prediction_date?: string;
  district_name?: string;
  season?: string;
  latitude?: number;
  longitude?: number;
  well_depth_m?: number;
  lag_1?: number;
  lag_2?: number;
  lag_4?: number;
  past_rolling_mean_3?: number;
  past_rolling_std_3?: number;
  rain_prior_30d?: number;
  rain_prior_60d?: number;
  rain_prior_90d?: number;
  rain_prior_180d?: number;
  month_sin?: number;
  month_cos?: number;
}

export interface WaterLevelPredictionResponse {
  mode: string;
  well_id?: string;
  prediction_date?: string;
  model_used: string;
  predicted_water_level_m_bgl: number;
  well_depth_m?: number;
  effective_water_column_m?: number;
  historical_actual_m_bgl?: number | null;
  absolute_error_m?: number | null;
  features_used: Record<string, any>;
  evaluation_context: EvaluationContext;
}

export interface WellMetadataItem {
  well_id: string;
  district: string;
  block: string;
  village: string;
  latitude: number | null;
  longitude: number | null;
  well_depth_m: number | null;
  well_type: string;
  latest_date: string | null;
  total_observations: number;
}

export interface WellsListResponse {
  total: number;
  district_filter: string | null;
  wells: WellMetadataItem[];
}

export interface WellHistoricalRecord {
  date: string;
  water_level_m_bgl: number | null;
  rainfall_30d: number;
  season: string;
}

export interface WellDetailsResponse {
  well_id: string;
  district: string;
  block: string;
  village: string;
  latitude: number | null;
  longitude: number | null;
  well_depth_m: number | null;
  well_type: string;
  historical_records: WellHistoricalRecord[];
}

export interface LocationsListResponse {
  total: number;
  district_filter: string | null;
  locations: WellLocationItem[];
}

export interface WaterPotabilityRequest {
  pH: number;
  Electrical_Conductivity: number;
  TDS?: number | null;
  Total_Hardness: number;
  Calcium: number;
  Magnesium: number;
  Chloride: number;
  Sulphate: number;
  Iron: number;
  Bicarbonate: number;
  Sodium: number;
}

export interface ExceededParameter {
  parameter: string;
  observed_value: number;
  acceptable_limit: string;
  description: string;
}

export interface WaterPotabilityResponse {
  potability_code: number;
  potability_label: 'Potable' | 'Non-Potable';
  probability_potable: number;
  probability_non_potable: number;
  confidence_score: number;
  standards_basis: string;
  exceeded_parameters: ExceededParameter[];
  input_tds_calculated: boolean;
  regulatory_advisory: string;
}

export interface NearestWellRequest {
  latitude: number;
  longitude: number;
  max_results?: number;
  filter_district?: string;
}

export interface WellLocationItem {
  location_id: number;
  district: string;
  block: string;
  village: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  well_ids: string[];
  num_wells: number;
  pune_road_node_id?: number | null;
  snap_distance_m?: number | null;
}

export interface NearestWellResponse {
  query_coords: { latitude: number; longitude: number };
  total_found: number;
  filter_district?: string | null;
  nearest_wells: WellLocationItem[];
  coverage_note: string;
}

export interface PuneRoutingRequest {
  start_node_id: number;
  target_node_id: number;
  algorithm: 'A*' | 'Bidirectional' | 'BFS' | 'Greedy_Best_First' | 'IDDFS' | 'DFS';
  max_depth?: number;
}

export interface PuneRoutingResponse {
  success: boolean;
  algorithm: string;
  start_node_id: number;
  target_node_id: number;
  total_distance_m?: number | null;
  total_distance_km?: number | null;
  edge_count?: number | null;
  expanded_nodes: number;
  execution_time_ms: number;
  route_node_ids?: number[] | null;
  route_geometry?: [number, number][] | null;
  error_message?: string | null;
  network_scope: string;
}

export interface HealthResponse {
  status: string;
  timestamp: number;
  services: {
    regression: boolean;
    classification: boolean;
    spatial: boolean;
    routing: boolean;
  };
}

export interface DistrictClassificationSummary {
  district: string;
  latitude: number;
  longitude: number;
  monitoring_locations_count: number;
  tested_samples: number;
  potable_samples: number;
  non_potable_samples: number;
  potability_percentage: number | null;
  dominant_classification: 'Potable' | 'Non-Potable';
  classification_source: 'Actual' | 'Simulated';
  status: string;
  has_verified_coordinates: boolean;
  data_source_note: string;
}

export interface VerifiedClassificationStation {
  id: string;
  name: string;
  district: string;
  latitude: number;
  longitude: number;
  potability_code: number;
  potability_label: 'Potable' | 'Non-Potable';
  probability_potable: number | null;
  source: string;
}

export interface DistrictClassificationCoverageResponse {
  total_districts: number;
  districts_with_data: number;
  districts_without_data: number;
  total_tested_samples: number;
  total_potable_samples: number;
  total_non_potable_samples: number;
  districts: DistrictClassificationSummary[];
  verified_stations: VerifiedClassificationStation[];
  dataset_scope_note: string;
}

// -------------------------------------------------------------
// API Request Helper
// -------------------------------------------------------------

async function postJSON<T>(endpoint: string, body: any): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    let errorMsg = `Server error ${res.status}`;
    try {
      const errData = await res.json();
      if (errData.detail) {
        errorMsg = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

async function getJSON<T>(endpoint: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!res.ok) {
    let errorMsg = `Server error ${res.status}`;
    try {
      const errData = await res.json();
      if (errData.detail) {
        errorMsg = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

export async function checkBackendHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/health`);
  if (!res.ok) {
    throw new Error(`Backend health check failed with status ${res.status}`);
  }
  return res.json();
}

export async function predictWaterLevel(req: WaterLevelPredictionRequest): Promise<WaterLevelPredictionResponse> {
  return postJSON<WaterLevelPredictionResponse>('/api/v1/predict/water-level', req);
}

export async function classifyWaterPotability(req: WaterPotabilityRequest): Promise<WaterPotabilityResponse> {
  return postJSON<WaterPotabilityResponse>('/api/v1/classify/water-potability', req);
}

export async function findNearestWells(req: NearestWellRequest): Promise<NearestWellResponse> {
  return postJSON<NearestWellResponse>('/api/v1/spatial/nearest-well', req);
}

export async function findPuneRoute(req: PuneRoutingRequest): Promise<PuneRoutingResponse> {
  return postJSON<PuneRoutingResponse>('/api/v1/routing/pune', req);
}

export async function getRegressionWells(district?: string, limit?: number): Promise<WellsListResponse> {
  const params = new URLSearchParams();
  if (district) params.append('district', district);
  if (limit) params.append('limit', String(limit));
  const query = params.toString() ? `?${params.toString()}` : '';
  return getJSON<WellsListResponse>(`/api/v1/regression/wells${query}`);
}

export async function getRegressionDistricts(): Promise<string[]> {
  return getJSON<string[]>('/api/v1/regression/districts');
}

export async function getWellDetails(wellId: string): Promise<WellDetailsResponse> {
  return getJSON<WellDetailsResponse>(`/api/v1/regression/wells/${encodeURIComponent(wellId)}`);
}

export async function getSpatialLocations(district?: string, limit?: number): Promise<LocationsListResponse> {
  const params = new URLSearchParams();
  if (district) params.append('district', district);
  if (limit) params.append('limit', String(limit));
  const query = params.toString() ? `?${params.toString()}` : '';
  return getJSON<LocationsListResponse>(`/api/v1/spatial/locations${query}`);
}

export async function getSpatialDistricts(): Promise<string[]> {
  return getJSON<string[]>('/api/v1/spatial/districts');
}

export async function getClassificationDistrictCoverage(): Promise<DistrictClassificationCoverageResponse> {
  return getJSON<DistrictClassificationCoverageResponse>('/api/v1/classification/district-coverage');
}
