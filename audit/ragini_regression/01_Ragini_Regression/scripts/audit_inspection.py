import sys
import pandas as pd
import numpy as np

print("="*60)
print("TESTING ENCODING AND AUDITING GROUNDWATER DATASET")
print("="*60)

gw_path = "ground_water_level_manual_quarterly_maharashtra_1970_2025.csv"

# Test reading with latin1 or cp1252
for enc in ['latin1', 'cp1252', 'iso-8859-1']:
    try:
        print(f"Trying encoding: {enc}...")
        df_gw = pd.read_csv(gw_path, encoding=enc, low_memory=False)
        print(f"Success reading with encoding: {enc}!")
        gw_encoding = enc
        break
    except Exception as e:
        print(f"Failed with {enc}: {e}")

print(f"\nGroundwater Shape: {df_gw.shape[0]:,} rows x {df_gw.shape[1]} columns")

print("\nGroundwater Columns (cleaned of trailing whitespace for display):")
for orig_col in df_gw.columns:
    print(f" - {repr(orig_col)} -> stripped: {repr(orig_col.strip())}")

print("\nData types, Missing Values, and Unique Counts:")
for col in df_gw.columns:
    missing = df_gw[col].isna().sum()
    dtype = df_gw[col].dtype
    n_unique = df_gw[col].nunique()
    print(f"  {col.strip():<35} | Type: {str(dtype):<10} | Missing: {missing:>7,} ({missing/len(df_gw)*100:5.2f}%) | Unique: {n_unique:>6,}")

# Exact duplicates
exact_dupes = df_gw.duplicated().sum()
print(f"\nExact duplicate rows: {exact_dupes:,}")

# Clean column names in temporary view for easier inspection
df_gw_clean_cols = df_gw.copy()
df_gw_clean_cols.columns = [c.strip() for c in df_gw.columns]

# Target column: 'Water Level, m bgl'
target_col = 'Water Level, m bgl'
print(f"\nTarget column: '{target_col}'")
print(f"Target dtype: {df_gw_clean_cols[target_col].dtype}")
print("Target summary stats:")
print(df_gw_clean_cols[target_col].describe())

# Check negative or unusual values
neg_count = (df_gw_clean_cols[target_col] < 0).sum()
zero_count = (df_gw_clean_cols[target_col] == 0).sum()
nan_count = df_gw_clean_cols[target_col].isna().sum()
print(f"Negative values in target (< 0): {neg_count:,}")
print(f"Zero values in target (== 0): {zero_count:,}")
print(f"NaN in target: {nan_count:,}")

# Inspect some negative values
if neg_count > 0:
    print("\nSample negative target values:")
    print(df_gw_clean_cols[df_gw_clean_cols[target_col] < 0][[
        'Well ID', 'District Name', 'Date of Monitoring', target_col
    ]].head(10))

# Date parsing inspection
date_col = 'Date of Monitoring'
print(f"\nDate column: '{date_col}' sample values:")
print(df_gw_clean_cols[date_col].head(10))
print("Parsing dates...")
# Convert to datetime
dates = pd.to_datetime(df_gw_clean_cols[date_col], format='mixed', dayfirst=True, errors='coerce')
nat_count = dates.isna().sum()
print(f"Failed to parse dates (NaT): {nat_count:,}")
print(f"Min date: {dates.min()}, Max date: {dates.max()}")

# Well + Date duplicates and conflicts
# First check duplicates after removing exact duplicates
df_gw_no_exact = df_gw_clean_cols.drop_duplicates()
print(f"\nRows after removing {exact_dupes:,} exact duplicates: {len(df_gw_no_exact):,}")

well_date_dupes = df_gw_no_exact.duplicated(subset=['Well ID', 'Date of Monitoring'], keep=False)
dupe_groups = df_gw_no_exact[well_date_dupes].groupby(['Well ID', 'Date of Monitoring'])
n_conflicting_groups = 0
n_conflicting_records = 0
n_identical_target_groups = 0

for (well, dt), grp in dupe_groups:
    if grp[target_col].nunique() > 1:
        n_conflicting_groups += 1
        n_conflicting_records += len(grp)
    else:
        n_identical_target_groups += 1

print(f"Total repeated well-date groups (after exact dupe removal): {dupe_groups.ngroups:,}")
print(f"Conflicting well-date groups (different water level): {n_conflicting_groups:,} (containing {n_conflicting_records:,} records)")
print(f"Repeated well-date groups with identical water level: {n_identical_target_groups:,}")

# Sample conflicting records
if n_conflicting_groups > 0:
    print("\nSample conflicting well-date groups:")
    count = 0
    for (well, dt), grp in dupe_groups:
        if grp[target_col].nunique() > 1:
            print(f"--- Well: {well}, Date: {dt} ---")
            print(grp[['Well ID', 'District Name', 'Date of Monitoring', 'Water Level, m bgl', 'Agency', 'Well Depth, m']])
            count += 1
            if count >= 3:
                break

print("\n" + "="*60)
print("AUDITING RAINFALL DATASET")
print("="*60)

rf_path = "rainfall_manual_daily_maharashtra_sw_mh_2021_2025.csv"
for enc in ['utf-8', 'latin1', 'cp1252']:
    try:
        df_rf = pd.read_csv(rf_path, encoding=enc, low_memory=False)
        print(f"Success reading rainfall with encoding: {enc}!")
        rf_encoding = enc
        break
    except Exception as e:
        print(f"Failed rainfall with {enc}: {e}")

print(f"Rainfall Shape: {df_rf.shape[0]:,} rows x {df_rf.shape[1]} columns")
print("\nRainfall Columns:")
for c in df_rf.columns:
    print(f" - {repr(c)}")

print("\nRainfall Data types, Missing Values, Unique Counts:")
for col in df_rf.columns:
    missing = df_rf[col].isna().sum()
    dtype = df_rf[col].dtype
    n_unique = df_rf[col].nunique()
    print(f"  {col:<35} | Type: {str(dtype):<10} | Missing: {missing:>7,} ({missing/len(df_rf)*100:5.2f}%) | Unique: {n_unique:>6,}")

exact_dupes_rf = df_rf.duplicated().sum()
print(f"\nExact duplicate rows in rainfall: {exact_dupes_rf:,}")

print("\nRainfall head (5 rows):")
print(df_rf.head())

print("\nAudit completed successfully.")
