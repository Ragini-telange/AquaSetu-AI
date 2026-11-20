import pandas as pd, json, os, sys
csv_path = r'C:\\Users\\Vedangi\\Documents\\AquaGuard_AI1\\datasets\\ground_water_level_manual_quarterly_maharashtra_1970_2025.csv'
if not os.path.exists(csv_path):
    print('CSV not found')
    sys.exit(1)
# Read with latin1 encoding to handle special chars
df = pd.read_csv(csv_path, encoding='latin1', low_memory=False)
report = {}
# 1. Unique Well IDs
report['unique_well_ids'] = int(df['Well ID'].nunique())
# 2. Unique districts (District Name column has trailing space)
report['unique_districts'] = int(df['District Name '].nunique())
# 3. Unique blocks
report['unique_blocks'] = int(df['Block Name '].nunique())
# 4. Unique villages
report['unique_villages'] = int(df['Village '].nunique())
# 5. Unique lat-long pairs (rounded to 6 decimals to avoid floating noise)
lat_col = 'Latitude '
lon_col = 'Longitude '
coords = df[[lat_col, lon_col]].dropna()
coords_rounded = coords.round(6)
report['unique_coordinate_pairs'] = int(coords_rounded.drop_duplicates().shape[0])
# 6. Well IDs with multiple coordinate pairs
well_coord_counts = df.groupby('Well ID')[[lat_col, lon_col]].apply(lambda g: g.dropna().drop_duplicates().shape[0])
multiple_coords_wells = well_coord_counts[well_coord_counts > 1]
report['well_ids_multiple_coords'] = int(multiple_coords_wells.shape[0])
# 7. Different Well IDs sharing same coordinates
coord_to_wells = df.groupby([lat_col, lon_col])['Well ID'].nunique()
shared_coords = coord_to_wells[coord_to_wells > 1]
report['coordinate_shared_by_multiple_wells'] = int(shared_coords.shape[0])
# 8. Records outside Maharashtra bbox (preliminary)
# Approx bbox: lat 15.6-22.1, lon 72.6-80.9
outside = df[(df[lat_col] < 15.6) | (df[lat_col] > 22.1) | (df[lon_col] < 72.6) | (df[lon_col] > 80.9)]
report['records_outside_bbox'] = int(outside.shape[0])
# 9. 10 examples of duplicate rows (full rows)
dup_mask = df.duplicated(keep=False)
duplicate_rows = df[dup_mask].head(10)
report['duplicate_row_examples'] = duplicate_rows.to_dict(orient='records')
# 10. 10 examples of wells with conflicting coordinates
conflict_examples = []
for well_id, grp in df.groupby('Well ID'):
    unique_coords = grp[[lat_col, lon_col]].dropna().drop_duplicates()
    if unique_coords.shape[0] > 1:
        # take first well record with each unique coord
        for _, row in unique_coords.head(10).iterrows():
            conflict_examples.append({
                'Well ID': well_id,
                'Latitude': row[lat_col],
                'Longitude': row[lon_col]
            })
    if len(conflict_examples) >= 10:
        break
report['wells_conflicting_coords_examples'] = conflict_examples[:10]
# 11. Well ID stability across dates (count distinct dates per well)
date_col = 'Date of Monitoring'
well_date_counts = df.groupby('Well ID')[date_col].nunique()
report['well_ids_multiple_dates'] = int((well_date_counts > 1).sum())
# Explanation about graph nodes
report['graph_node_explanation'] = (
    "Each observation (row) records a water‑level measurement at a specific time. "
    "For routing you need a spatial network, so the natural graph nodes are the *unique geographic locations* (unique latitude‑longitude pairs). "
    "Multiple rows sharing the same coordinates represent the same physical monitoring site and therefore map to a single node."
)
print(json.dumps(report, indent=2, ensure_ascii=False))
