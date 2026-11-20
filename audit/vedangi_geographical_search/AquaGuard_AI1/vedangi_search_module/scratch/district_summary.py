import pandas as pd, os
csv_path = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\datasets\ground_water_level_manual_quarterly_maharashtra_1970_2025.csv'
print('Loading CSV...')
df = pd.read_csv(csv_path)
# strip column whitespace
df.columns = [c.strip() for c in df.columns]
# create coordinate tuple
df['coord'] = list(zip(df['Latitude'], df['Longitude']))
# drop rows with missing lat/lon for location counting
coord_valid = df.dropna(subset=['Latitude', 'Longitude'])
# group by district name
loc_counts = coord_valid.groupby('District Name')['coord'].nunique().rename('unique_location_count')
well_counts = df.groupby('District Name')['Well ID'].nunique().rename('unique_well_id_count')
summary = pd.concat([loc_counts, well_counts], axis=1).reset_index()
summary = summary.sort_values('unique_location_count', ascending=True)
out_path = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module\processed_data\district_summary.csv'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
summary.to_csv(out_path, index=False)
print('Summary written to', out_path)
print(summary.head(10).to_string(index=False))
print('...')
print(summary.tail(10).to_string(index=False))
