import pandas as pd
import numpy as np

gw_path = "ground_water_level_manual_quarterly_maharashtra_1970_2025.csv"
rf_path = "rainfall_manual_daily_maharashtra_sw_mh_2021_2025.csv"

df_gw = pd.read_csv(gw_path, encoding='latin1', low_memory=False)
df_gw.columns = [c.strip() for c in df_gw.columns]
df_gw['Date'] = pd.to_datetime(df_gw['Date of Monitoring'], format='mixed', dayfirst=True)

df_rf = pd.read_csv(rf_path, encoding='utf-8', low_memory=False)
df_rf['Date'] = pd.to_datetime(df_rf['Data Acquisition Time'], format='mixed', dayfirst=True)

print("="*60)
print("DEEP AUDIT: DISTRICT MATCHING")
print("="*60)
gw_districts = set(df_gw['District Name'].dropna().str.strip().str.upper())
rf_districts = set(df_rf['District'].dropna().str.strip().str.upper())

print(f"Unique GW districts ({len(gw_districts)}):", sorted(list(gw_districts)))
print(f"Unique RF districts ({len(rf_districts)}):", sorted(list(rf_districts)))

diff_gw_rf = gw_districts - rf_districts
diff_rf_gw = rf_districts - gw_districts
print(f"Districts in GW but not in RF: {diff_gw_rf}")
print(f"Districts in RF but not in GW: {diff_rf_gw}")

print("\n" + "="*60)
print("DEEP AUDIT: GROUNDWATER OBSERVATION FREQUENCY & MONITORING MONTHS")
print("="*60)
df_gw['Year'] = df_gw['Date'].dt.year
df_gw['Month'] = df_gw['Date'].dt.month
print("Records by Month in Groundwater:")
print(df_gw['Month'].value_counts().sort_index())

print("\nYearly record counts (last 10 years):")
print(df_gw['Year'].value_counts().sort_index().tail(10))

print("\n" + "="*60)
print("DEEP AUDIT: RAINFALL DATE RANGE & FREQUENCY")
print("="*60)
print(f"Rainfall Min Date: {df_rf['Date'].min()}, Max Date: {df_rf['Date'].max()}")
df_rf['Year'] = df_rf['Date'].dt.year
df_rf['Month'] = df_rf['Date'].dt.month
print("Rainfall records by Year:")
print(df_rf['Year'].value_counts().sort_index())
print("\nRainfall records by Month:")
print(df_rf['Month'].value_counts().sort_index())

print("\n" + "="*60)
print("DEEP AUDIT: CONFLICTING WELL-DATE GROUPS")
print("="*60)
df_gw_no_exact = df_gw.drop_duplicates()
well_date_dupes = df_gw_no_exact.duplicated(subset=['Well ID', 'Date of Monitoring'], keep=False)
conflicts = df_gw_no_exact[well_date_dupes].groupby(['Well ID', 'Date of Monitoring']).filter(lambda g: g['Water Level, m bgl'].nunique() > 1)

print(f"Number of rows in conflicting groups: {len(conflicts)}")
sample_wells = conflicts['Well ID'].unique()[:5]
for w in sample_wells:
    w_conf = conflicts[conflicts['Well ID'] == w]
    print(f"\nConflict for Well {w}:")
    print(w_conf[['Well ID', 'District Name', 'Date of Monitoring', 'Water Level, m bgl', 'Agency', 'Well Depth, m']])

print("\nTarget difference in conflicting pairs (summary):")
diffs = []
for _, grp in conflicts.groupby(['Well ID', 'Date of Monitoring']):
    vals = grp['Water Level, m bgl'].dropna().values
    if len(vals) >= 2:
        diffs.append(abs(vals[0] - vals[1]))
diffs = pd.Series(diffs)
print(diffs.describe())

print("\n" + "="*60)
print("DEEP AUDIT: OVERLAPPING PERIOD (2021 - 2025)")
print("="*60)
gw_overlap = df_gw[df_gw['Year'] >= 2021]
print(f"Groundwater records 2021+: {len(gw_overlap):,}")
print(f"GW 2021+ unique wells: {gw_overlap['Well ID'].nunique():,}")
print(f"GW 2021+ unique districts: {gw_overlap['District Name'].nunique():,}")
print(f"GW 2021+ date range: {gw_overlap['Date'].min()} to {gw_overlap['Date'].max()}")
