import pandas as pd, json, os, sys
csv_path = r'C:\\Users\\Vedangi\\Documents\\AquaGuard_AI1\\datasets\\ground_water_level_manual_quarterly_maharashtra_1970_2025.csv'
if not os.path.exists(csv_path):
    print('CSV not found')
    sys.exit(1)
df = pd.read_csv(csv_path, encoding='latin1', low_memory=False)
report = {}
report['rows'], report['columns'] = df.shape
report['columns'] = list(df.columns)
report['dtypes'] = {col: str(dtype) for col, dtype in df.dtypes.items()}
# Identify possible columns
station_id_cols = [c for c in df.columns if 'id' in c.lower()]
station_name_cols = [c for c in df.columns if 'name' in c.lower()]
district_cols = [c for c in df.columns if 'district' in c.lower()]
lat_cols = [c for c in df.columns if 'lat' in c.lower()]
lon_cols = [c for c in df.columns if 'lon' in c.lower() or 'lng' in c.lower()]
report['station_id_columns'] = station_id_cols
report['station_name_columns'] = station_name_cols
report['district_columns'] = district_cols
report['latitude_columns'] = lat_cols
report['longitude_columns'] = lon_cols
# Missing values per column
report['missing_values'] = df.isnull().sum().to_dict()
# Duplicate rows count
report['duplicate_rows'] = int(df.duplicated().sum())
# Invalid coordinates detection
invalid_rows = []
if lat_cols and lon_cols:
    lat = df[lat_cols[0]]
    lon = df[lon_cols[0]]
    invalid = (~lat.between(-90, 90)) | (~lon.between(-180, 180))
    invalid_rows = df[invalid].index.tolist()
report['invalid_coordinate_row_indices'] = invalid_rows[:10]  # show first few
print(json.dumps(report, indent=2))

