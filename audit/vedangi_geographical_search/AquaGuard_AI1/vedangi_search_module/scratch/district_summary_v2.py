import pandas as pd, os, sys
csv_path = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\datasets\ground_water_level_manual_quarterly_maharashtra_1970_2025.csv'
print('Loading CSV with latin1 encoding...')
# read with appropriate encoding, avoid low_memory warnings
try:
    df = pd.read_csv(csv_path, encoding='latin1', low_memory=False)
except Exception as e:
    print('Failed to read CSV:', e)
    sys.exit(1)
# Strip whitespace from column names
df.columns = [c.strip() for c in df.columns]
# Create coordinate tuple for exact lat/lon
df['coord'] = list(zip(df['Latitude'], df['Longitude']))
# Filter rows with valid coordinates for location counting
coord_valid = df.dropna(subset=['Latitude', 'Longitude'])
# Group by district name
loc_counts = coord_valid.groupby('District Name')['coord'].nunique().rename('unique_location_count')
well_counts = df.groupby('District Name')['Well ID'].nunique().rename('unique_well_id_count')
summary = pd.concat([loc_counts, well_counts], axis=1).reset_index()
summary = summary.sort_values('unique_location_count', ascending=True)
# Save summary CSV
out_path = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module\processed_data\district_summary.csv'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
summary.to_csv(out_path, index=False)
print('Summary written to', out_path)
print('First 10 rows:')
print(summary.head(10).to_string(index=False))
print('...')
print('Last 10 rows:')
print(summary.tail(10).to_string(index=False))
