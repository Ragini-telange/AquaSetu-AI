import pandas as pd, os, sys
path = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module\processed_data\groundwater_locations.csv'
print('Reading groundwater_locations')
try:
    df = pd.read_csv(path)
except Exception as e:
    print('Error reading CSV:', e)
    sys.exit(1)
# Strip whitespace from column names
df.columns = [c.strip() for c in df.columns]
# Filter for Pune district
df_pune = df[df['districts'].str.strip().eq('Pune')]
if df_pune.empty:
    print('No rows found for Pune')
    sys.exit(1)
min_lat = df_pune['Latitude'].min()
max_lat = df_pune['Latitude'].max()
min_lon = df_pune['Longitude'].min()
max_lon = df_pune['Longitude'].max()
print('Pune groundwater locations:')
print(f'Count: {len(df_pune)}')
print(f'Lat range: {min_lat:.6f} to {max_lat:.6f}')
print(f'Lon range: {min_lon:.6f} to {max_lon:.6f}')
# Propose buffer (e.g., 0.02 degree ≈ 2km)
buffer = 0.02
bbox = {
    'min_lat': min_lat - buffer,
    'max_lat': max_lat + buffer,
    'min_lon': min_lon - buffer,
    'max_lon': max_lon + buffer,
}
print('Proposed buffered bounding box:')
print(bbox)
# Save the bbox to a temporary json for later use (optional)
import json
out_json = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module\scratch\pune_bbox.json'
with open(out_json, 'w') as f:
    json.dump(bbox, f)
print('BBox saved to', out_json)
