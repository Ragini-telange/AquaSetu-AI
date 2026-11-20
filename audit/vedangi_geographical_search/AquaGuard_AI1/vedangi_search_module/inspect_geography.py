import pandas as pd, json, os, sys

# ------------------------------------------------------------
# 1️⃣ Verify CSV file path (read‑only, no modifications)
# ------------------------------------------------------------
csv_path = r'C:\\Users\\Vedangi\\Documents\\AquaGuard_AI1\\datasets\\ground_water_level_manual_quarterly_maharashtra_1970_2025.csv'
if not os.path.isfile(csv_path):
    sys.stderr.write(f"ERROR: CSV file not found at {csv_path}\n")
    sys.exit(1)

# ------------------------------------------------------------
# 2️⃣ Load dataset (latin‑1 handles special characters)
# ------------------------------------------------------------
# Use low_memory=False for reliable dtype inference on a large file
# and set encoding explicitly – this is a read‑only operation.
try:
    df = pd.read_csv(csv_path, encoding='latin1', low_memory=False)
except Exception as e:
    sys.stderr.write(f"ERROR while reading CSV: {e}\n")
    sys.exit(1)

# ------------------------------------------------------------
# 3️⃣ Safety checks – missing IDs / coordinates
# ------------------------------------------------------------
# Ensure we have a column named exactly 'Well ID' (case‑sensitive).
well_id_col = 'Well ID'
if well_id_col not in df.columns:
    sys.stderr.write("ERROR: 'Well ID' column missing in CSV.\n")
    sys.exit(1)

# Latitude / Longitude column names include trailing spaces in the source file.
lat_col = 'Latitude '
lon_col = 'Longitude '
for col in (lat_col, lon_col):
    if col not in df.columns:
        sys.stderr.write(f"ERROR: Expected column '{col}' not found.\n")
        sys.exit(1)

# Drop rows where Well ID is missing – they cannot be linked to a location.
df = df.dropna(subset=[well_id_col])

# ------------------------------------------------------------
# 4️⃣ Helper: round coordinates to 6 decimal places
# ------------------------------------------------------------
# This eliminates tiny floating‑point differences that are not meaningful
# for geographic matching.
coords = df[[lat_col, lon_col]].copy()
coords_rounded = coords.round(6)
df['lat_rounded'] = coords_rounded[lat_col]
df['lon_rounded'] = coords_rounded[lon_col]

# ------------------------------------------------------------
# 5️⃣ Build the report
# ------------------------------------------------------------
report = {}

# Unique identifiers
report['unique_well_ids'] = int(df[well_id_col].nunique())
report['unique_districts'] = int(df['District Name '].nunique()) if 'District Name ' in df.columns else None
report['unique_blocks'] = int(df['Block Name '].nunique()) if 'Block Name ' in df.columns else None
report['unique_villages'] = int(df['Village '].nunique()) if 'Village ' in df.columns else None

# Unique coordinate pairs (rounded)
unique_coords = df[['lat_rounded', 'lon_rounded']].dropna().drop_duplicates()
report['unique_coordinate_pairs'] = int(unique_coords.shape[0])

# Well IDs that have more than one distinct coordinate pair
well_coord_counts = (
    df.groupby(well_id_col)
      [['lat_rounded', 'lon_rounded']]
      .apply(lambda g: g.dropna().drop_duplicates().shape[0])
)
report['well_ids_multiple_coords'] = int((well_coord_counts > 1).sum())

# Different wells sharing the same coordinate pair
coord_to_wells = (
    df.groupby(['lat_rounded', 'lon_rounded'])[well_id_col]
      .nunique()
)
report['coordinate_shared_by_multiple_wells'] = int((coord_to_wells > 1).sum())

# Preliminary bounding‑box check for Maharashtra (approx.)
# Latitude: 15.6‑22.1, Longitude: 72.6‑80.9
bbox_mask = (
    (df[lat_col] < 15.6) | (df[lat_col] > 22.1) |
    (df[lon_col] < 72.6) | (df[lon_col] > 80.9)
)
report['records_outside_bbox'] = int(df[bbox_mask].shape[0])

# Duplicate rows (exact copies across all columns)
dup_mask = df.duplicated(keep=False)
duplicate_rows = df[dup_mask].head(10)
report['duplicate_row_examples'] = duplicate_rows.to_dict(orient='records')

# Wells with conflicting coordinates (should be empty after rounding)
conflict_examples = []
for well, grp in df.groupby(well_id_col):
    uniq = grp[['lat_rounded', 'lon_rounded']].dropna().drop_duplicates()
    if uniq.shape[0] > 1:
        for _, row in uniq.head(10).iterrows():
            conflict_examples.append({
                'Well ID': well,
                'Latitude': row['lat_rounded'],
                'Longitude': row['lon_rounded']
            })
    if len(conflict_examples) >= 10:
        break
report['wells_conflicting_coords_examples'] = conflict_examples[:10]

# Well ID stability across monitoring dates
date_col = 'Date of Monitoring'
if date_col in df.columns:
    well_date_counts = df.groupby(well_id_col)[date_col].nunique()
    report['well_ids_multiple_dates'] = int((well_date_counts > 1).sum())
else:
    report['well_ids_multiple_dates'] = None

# Explanation for later graph construction
report['graph_node_explanation'] = (
    "Each row is a time‑stamped observation; for routing we use the *unique* "
    "latitude‑longitude pairs as graph nodes. Multiple rows sharing the same "
    "coordinates (or the same well ID) map to a single spatial node."
)

# ------------------------------------------------------------
# 6️⃣ Output as pretty‑printed JSON (UTF‑8, ensure_ascii=False)
# ------------------------------------------------------------
print(json.dumps(report, indent=2, ensure_ascii=False))
