import os
import pandas as pd
import geopandas as gpd
import osmnx as ox
import networkx as nx
from shapely.geometry import Point

# ---------- Configurable parameters ----------
MAX_SNAPPING_DISTANCE_M = 100  # metres

# Paths (relative to project root)
BASE_DIR = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module'
GROUNDWATER_CSV = os.path.join(BASE_DIR, 'processed_data', 'groundwater_locations.csv')
GRAPHML_PATH = os.path.join(BASE_DIR, 'pune_road_network.graphml')

# Output files
OUT_ALL = os.path.join(BASE_DIR, 'processed_data', 'pune_location_node_snap.csv')
OUT_UNMATCHED = os.path.join(BASE_DIR, 'processed_data', 'pune_unmatched_locations.csv')

# ---------- Load data ----------
print('Loading groundwater locations...')
gw_df = pd.read_csv(GROUNDWATER_CSV)
# Ensure column names have no leading/trailing spaces
gw_df.columns = [c.strip() for c in gw_df.columns]
# Filter to Pune district only
gw_df = gw_df[gw_df['districts'].str.strip().eq('Pune')].copy()
print(f'Filtered to Pune district: {len(gw_df)} rows')

print('Loading road network graph...')
G = ox.load_graphml(GRAPHML_PATH)
# Project graph to UTM (meters) for accurate distance calculations
print('Projecting graph to UTM...')
G_proj = ox.project_graph(G)

# Build a GeoDataFrame of groundwater points (WGS84)
print('Creating GeoDataFrame of groundwater points...')
points_gdf = gpd.GeoDataFrame(
    gw_df.copy(),
    geometry=gpd.points_from_xy(gw_df['Longitude'], gw_df['Latitude']),
    crs='EPSG:4326'
)
# Project points to same CRS as graph (meters)
points_proj = points_gdf.to_crs(G_proj.graph['crs'])

# Extract projected x/y arrays for nearest node lookup
xs = points_proj.geometry.x.values
ys = points_proj.geometry.y.values

print('Finding nearest graph nodes...')
nearest_node_ids = ox.distance.nearest_nodes(G_proj, X=xs, Y=ys)

# Compute Euclidean distance (in meters) between point and its nearest node
node_x = nx.get_node_attributes(G_proj, 'x')
node_y = nx.get_node_attributes(G_proj, 'y')

distances = []
for pid, nid in zip(range(len(nearest_node_ids)), nearest_node_ids):
    dx = xs[pid] - node_x[nid]
    dy = ys[pid] - node_y[nid]
    dist = (dx**2 + dy**2) ** 0.5
    distances.append(dist)

# Assemble results DataFrame
results = gw_df.copy()
results['nearest_node_id'] = nearest_node_ids
results['snap_distance_m'] = distances
results['match_status'] = results['snap_distance_m'].apply(lambda d: 'Matched' if d <= MAX_SNAPPING_DISTANCE_M else 'Unmatched')

# Save full results
print(f'Saving all results to {OUT_ALL}')
results.to_csv(OUT_ALL, index=False)

# Save unmatched report
unmatched = results[results['match_status'] == 'Unmatched']
print(f'Saving unmatched report ({len(unmatched)} rows) to {OUT_UNMATCHED}')
unmatched.to_csv(OUT_UNMATCHED, index=False)

# ---------- Validation & summary ----------
matched_count = (results['match_status'] == 'Matched').sum()
unmatched_count = (results['match_status'] == 'Unmatched').sum()
print('\n=== Summary ===')
print(f'Total groundwater locations processed: {len(results)}')
print(f'Matched (<= {MAX_SNAPPING_DISTANCE_M} m): {matched_count}')
print(f'Unmatched (> {MAX_SNAPPING_DISTANCE_M} m): {unmatched_count}')
if matched_count > 0:
    print(f'  Snap distance – mean: {results.loc[results["match_status"] == "Matched", "snap_distance_m"].mean():.2f} m')
    print(f'  Snap distance – min:  {results.loc[results["match_status"] == "Matched", "snap_distance_m"].min():.2f} m')
    print(f'  Snap distance – max:  {results.loc[results["match_status"] == "Matched", "snap_distance_m"].max():.2f} m')

# Verify that all reported node IDs exist in the graph
missing_nodes = set(results['nearest_node_id']) - set(G_proj.nodes)
if missing_nodes:
    print(f'ERROR: {len(missing_nodes)} reported node IDs not found in the graph!')
else:
    print('All reported node IDs verified in the graph.')

print('Phase 3 completed.')
