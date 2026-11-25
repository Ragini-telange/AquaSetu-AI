import os
import math
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from scipy.spatial import KDTree

from app.core.config import settings
from app.schemas.spatial import NearestWellRequest, NearestWellResponse, WellLocationItem

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

class SpatialService:
    def __init__(self):
        self.df_locations: Optional[pd.DataFrame] = None
        self.snap_dict: Dict[int, Dict[str, Any]] = {}
        self.coords_array: Optional[np.ndarray] = None
        self.kdtree: Optional[KDTree] = None
        self.locations_metadata: List[Dict[str, Any]] = []
        self.is_initialized = False

    def initialize(self):
        if self.is_initialized:
            return

        locations_path = settings.get_absolute_path(settings.STATEWIDE_LOCATIONS_PATH)
        snap_path = settings.get_absolute_path(settings.PUNE_SNAP_PATH)

        if not os.path.exists(locations_path):
            raise FileNotFoundError(f"Statewide groundwater locations file not found at: {locations_path}")

        print(f"[SpatialService] Loading statewide groundwater locations from {locations_path}...")
        self.df_locations = pd.read_csv(locations_path)
        
        # Standardize column names (strip whitespace: 'Latitude ', 'Longitude ')
        self.df_locations.columns = [c.strip() for c in self.df_locations.columns]

        # Load Pune snapping dictionary if available
        if os.path.exists(snap_path):
            print(f"[SpatialService] Loading Pune node snaps from {snap_path}...")
            df_snap = pd.read_csv(snap_path)
            for _, row in df_snap.iterrows():
                loc_id = int(row['location_id'])
                matched = str(row.get('match_status', '')).strip().lower() == 'matched'
                node_id = int(row['nearest_node_id']) if (matched and not pd.isna(row.get('nearest_node_id'))) else None
                snap_dist = float(row['snap_distance_m']) if (matched and not pd.isna(row.get('snap_distance_m'))) else None
                self.snap_dict[loc_id] = {
                    'node_id': node_id,
                    'snap_distance_m': round(snap_dist, 2) if snap_dist is not None else None
                }

        # Build KDTree on coordinates (lat, lon)
        self.coords_array = self.df_locations[['Latitude', 'Longitude']].values
        self.kdtree = KDTree(self.coords_array)

        # Precompute locations metadata
        self.locations_metadata = []
        for _, row in self.df_locations.iterrows():
            loc_id = int(row['location_id'])
            raw_wells = str(row.get('well_ids', ''))
            well_ids = [w.strip() for w in raw_wells.replace('[', '').replace(']', '').replace("'", "").split(',') if w.strip()]
            snap_info = self.snap_dict.get(loc_id, {})
            self.locations_metadata.append({
                'location_id': loc_id,
                'district': str(row.get('districts', '')),
                'block': str(row.get('blocks', '')),
                'village': str(row.get('villages', '')),
                'latitude': round(float(row['Latitude']), 6),
                'longitude': round(float(row['Longitude']), 6),
                'distance_km': 0.0,
                'well_ids': well_ids,
                'num_wells': int(row.get('num_well_ids', len(well_ids))),
                'pune_road_node_id': snap_info.get('node_id'),
                'snap_distance_m': snap_info.get('snap_distance_m')
            })

        self.is_initialized = True
        print(f"[SpatialService] Initialized with {len(self.df_locations)} locations across {self.df_locations['districts'].nunique()} districts.")

    def get_locations(self, district: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if not self.is_initialized:
            self.initialize()
        if district:
            d_clean = district.strip().lower()
            res = [loc for loc in self.locations_metadata if loc['district'].lower() == d_clean]
        else:
            res = self.locations_metadata
        if limit and limit > 0:
            return res[:limit]
        return res

    def get_districts(self) -> List[str]:
        if not self.is_initialized:
            self.initialize()
        return sorted(list(set(loc['district'] for loc in self.locations_metadata if loc['district'])))

    def find_nearest_wells(self, req: NearestWellRequest) -> NearestWellResponse:
        if not self.is_initialized:
            self.initialize()

        query_lat = req.latitude
        query_lon = req.longitude
        k = req.max_results
        district_filter = req.filter_district.strip().lower() if req.filter_district else None

        # Filter candidate pool if district is provided
        if district_filter:
            mask = self.df_locations['districts'].str.lower() == district_filter
            subset_df = self.df_locations[mask].copy()
            if len(subset_df) == 0:
                return NearestWellResponse(
                    query_coords={'latitude': query_lat, 'longitude': query_lon},
                    total_found=0,
                    filter_district=req.filter_district,
                    nearest_wells=[]
                )
            coords = subset_df[['Latitude', 'Longitude']].values
            tree = KDTree(coords)
            actual_k = min(k, len(subset_df))
            distances, indices = tree.query([query_lat, query_lon], k=actual_k)
            if actual_k == 1:
                indices = [indices]
            selected_rows = subset_df.iloc[indices]
        else:
            actual_k = min(k * 2, len(self.df_locations))
            distances, indices = self.kdtree.query([query_lat, query_lon], k=actual_k)
            selected_rows = self.df_locations.iloc[indices]

        results: List[WellLocationItem] = []
        for _, row in selected_rows.iterrows():
            loc_id = int(row['location_id'])
            well_lat = float(row['Latitude'])
            well_lon = float(row['Longitude'])
            dist_km = haversine_km(query_lat, query_lon, well_lat, well_lon)

            # Parse well IDs string
            raw_wells = str(row.get('well_ids', ''))
            well_ids = [w.strip() for w in raw_wells.replace('[', '').replace(']', '').replace("'", "").split(',') if w.strip()]

            snap_info = self.snap_dict.get(loc_id, {})
            node_id = snap_info.get('node_id')
            snap_dist = snap_info.get('snap_distance_m')

            results.append(WellLocationItem(
                location_id=loc_id,
                district=str(row.get('districts', '')),
                block=str(row.get('blocks', '')),
                village=str(row.get('villages', '')),
                latitude=round(well_lat, 6),
                longitude=round(well_lon, 6),
                distance_km=dist_km,
                well_ids=well_ids,
                num_wells=int(row.get('num_well_ids', len(well_ids))),
                pune_road_node_id=node_id,
                snap_distance_m=snap_dist
            ))

        # Sort strictly by true Haversine distance
        results.sort(key=lambda x: x.distance_km)
        results = results[:k]

        return NearestWellResponse(
            query_coords={'latitude': query_lat, 'longitude': query_lon},
            total_found=len(results),
            filter_district=req.filter_district,
            nearest_wells=results
        )

spatial_service = SpatialService()
