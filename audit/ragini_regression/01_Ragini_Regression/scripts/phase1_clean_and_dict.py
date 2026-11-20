import os
import pandas as pd
import numpy as np

print("="*70)
print("PHASE 1: DATA CLEANING, AUDITING, AND DATA DICTIONARY GENERATION")
print("="*70)

# Paths
gw_raw_path = "ground_water_level_manual_quarterly_maharashtra_1970_2025.csv"
rf_raw_path = "rainfall_manual_daily_maharashtra_sw_mh_2021_2025.csv"

out_clean_dir = "01_Ragini_Regression/clean_data"
out_dict_dir = "00_Source_Datasets_and_Data_Dictionary"
os.makedirs(out_clean_dir, exist_ok=True)
os.makedirs(out_dict_dir, exist_ok=True)

# -------------------------------------------------------------
# 1. GROUNDWATER CLEANING & CONFLICT AUDIT
# -------------------------------------------------------------
print("\n[Step 1.1] Loading raw groundwater dataset...")
df_gw = pd.read_csv(gw_raw_path, encoding='latin1', low_memory=False)
raw_row_count = len(df_gw)
print(f"Raw Groundwater Rows: {raw_row_count:,}, Columns: {df_gw.shape[1]}")

# Strip column names
df_gw.columns = [c.strip() for c in df_gw.columns]

# Standardize text columns (strip whitespace)
text_cols = df_gw.select_dtypes(include='object').columns
for col in text_cols:
    df_gw[col] = df_gw[col].astype(str).str.strip()

# Parse date
df_gw['Date'] = pd.to_datetime(df_gw['Date of Monitoring'], format='mixed', dayfirst=True)

# Check exact duplicates
exact_dupes_mask = df_gw.duplicated(subset=[c for c in df_gw.columns if c != 'Date'], keep='first')
n_exact_dupes = exact_dupes_mask.sum()
print(f"[Step 1.2] Exact duplicate rows identified: {n_exact_dupes:,}")

# Remove exact duplicates
df_gw_no_exact = df_gw[~exact_dupes_mask].copy()
print(f"Rows after removing exact duplicates: {len(df_gw_no_exact):,}")

# -------------------------------------------------------------
# 2. REPEATED WELL-DATE GROUPS AUDIT
# -------------------------------------------------------------
print("\n[Step 1.3] Auditing repeated well-date groups...")
well_date_dupes_mask = df_gw_no_exact.duplicated(subset=['Well ID', 'Date of Monitoring'], keep=False)
df_repeated = df_gw_no_exact[well_date_dupes_mask].copy()

grouped_repeated = df_repeated.groupby(['Well ID', 'Date of Monitoring'])
total_repeated_groups = grouped_repeated.ngroups
total_repeated_records = len(df_repeated)
print(f"Total repeated well-date groups: {total_repeated_groups:,} (containing {total_repeated_records:,} records)")

conflicting_groups_list = []
identical_groups_list = []

for (well_id, dt_str), group in grouped_repeated:
    n_distinct_targets = group['Water Level, m bgl'].nunique()
    if n_distinct_targets > 1:
        conflicting_groups_list.append((well_id, dt_str, group))
    else:
        identical_groups_list.append((well_id, dt_str, group))

n_conflicting_groups = len(conflicting_groups_list)
n_identical_groups = len(identical_groups_list)
print(f" - Repeated groups with IDENTICAL water level: {n_identical_groups} ({n_identical_groups*2} records)")
print(f" - Repeated groups with CONFLICTING water level: {n_conflicting_groups} ({n_conflicting_groups*2} records)")

# Build detailed audit dataframe for conflicting records
conflict_audit_rows = []
for group_id, (well_id, dt_str, group) in enumerate(conflicting_groups_list, 1):
    vals = group['Water Level, m bgl'].values
    depths = group['Well Depth, m'].values
    val_diff = abs(vals[0] - vals[1]) if len(vals) == 2 else np.nan
    
    for rank, (idx, row) in enumerate(group.iterrows(), 1):
        wl = row['Water Level, m bgl']
        depth = row['Well Depth, m']
        
        eq_depth = bool(pd.notna(wl) and pd.notna(depth) and wl == depth)
        gt_depth = bool(pd.notna(wl) and pd.notna(depth) and wl > depth)
        
        # Determine specific reason
        reason = []
        if eq_depth:
            reason.append("Reading equals well depth (possible dry well indicator)")
        if gt_depth:
            reason.append("Reading exceeds well depth (physically questionable sounding)")
        if not eq_depth and not gt_depth:
            reason.append("Plausible physical reading within well depth")
            
        conflict_audit_rows.append({
            'Conflict_Group_ID': f"CONF_{group_id:04d}",
            'Row_Index': idx,
            'Well ID': row['Well ID'],
            'District Name': row['District Name'],
            'Block Name': row['Block Name'],
            'Village': row['Village'],
            'Latitude': row['Latitude'],
            'Longitude': row['Longitude'],
            'Well Depth, m': depth,
            'Date of Monitoring': row['Date of Monitoring'],
            'Parsed_Date': row['Date'],
            'Water Level, m bgl': wl,
            'Reading_Rank_In_Group': rank,
            'Group_Target_Difference_m': val_diff,
            'Equals_Well_Depth': eq_depth,
            'Exceeds_Well_Depth': gt_depth,
            'Audit_Note': "; ".join(reason) if reason else "Standard conflict"
        })

df_conflict_audit = pd.DataFrame(conflict_audit_rows)
conflict_audit_csv_path = os.path.join(out_clean_dir, "conflicting_records_audit.csv")
df_conflict_audit.to_csv(conflict_audit_csv_path, index=False)
print(f"Saved detailed conflict audit to: {conflict_audit_csv_path}")

# Summary of conflicting records
print("\nConflict Audit Analysis:")
print(f" - Records where Water Level == Well Depth: {df_conflict_audit['Equals_Well_Depth'].sum()}")
print(f" - Records where Water Level > Well Depth: {df_conflict_audit['Exceeds_Well_Depth'].sum()}")
print(f" - Average target difference in conflicting groups: {df_conflict_audit['Group_Target_Difference_m'].mean():.2f} m")
print(f" - Median target difference in conflicting groups: {df_conflict_audit['Group_Target_Difference_m'].median():.2f} m")

# -------------------------------------------------------------
# 3. WELL DEPTH VALIDATION ACROSS ENTIRE DATASET
# -------------------------------------------------------------
print("\n[Step 1.4] Well depth validation across entire dataset...")
has_both = df_gw_no_exact['Water Level, m bgl'].notna() & df_gw_no_exact['Well Depth, m'].notna()
wl_gt_depth_all = (df_gw_no_exact['Water Level, m bgl'] > df_gw_no_exact['Well Depth, m']) & has_both
wl_eq_depth_all = (df_gw_no_exact['Water Level, m bgl'] == df_gw_no_exact['Well Depth, m']) & has_both

print(f"Total records where Water Level > Well Depth: {wl_gt_depth_all.sum():,} ({wl_gt_depth_all.sum()/len(df_gw_no_exact)*100:.3f}%)")
print(f"Total records where Water Level == Well Depth (dry well): {wl_eq_depth_all.sum():,} ({wl_eq_depth_all.sum()/len(df_gw_no_exact)*100:.3f}%)")

# Save sample of wl > depth records for documentation
df_depth_exceed = df_gw_no_exact[wl_gt_depth_all].copy()
depth_exceed_csv = os.path.join(out_clean_dir, "well_depth_exceedance_audit.csv")
df_depth_exceed.to_csv(depth_exceed_csv, index=False)
print(f"Saved well depth exceedance audit ({len(df_depth_exceed):,} rows) to: {depth_exceed_csv}")

# -------------------------------------------------------------
# 4. NEGATIVE AND ZERO READINGS AUDIT
# -------------------------------------------------------------
print("\n[Step 1.5] Negative and Zero Readings Audit...")
neg_mask = df_gw_no_exact['Water Level, m bgl'] < 0
zero_mask = df_gw_no_exact['Water Level, m bgl'] == 0
nan_mask = df_gw_no_exact['Water Level, m bgl'].isna()

print(f"Negative readings (< 0 m bgl): {neg_mask.sum():,}")
print(f"Zero readings (== 0 m bgl): {zero_mask.sum():,}")
print(f"Missing target readings (NaN): {nan_mask.sum():,}")

df_negatives = df_gw_no_exact[neg_mask].copy()
negatives_csv = os.path.join(out_clean_dir, "negative_readings_audit.csv")
df_negatives.to_csv(negatives_csv, index=False)
print(f"Saved negative readings audit ({len(df_negatives)} rows) to: {negatives_csv}")
print("Negative readings summary (m bgl):")
print(df_negatives['Water Level, m bgl'].describe())

# -------------------------------------------------------------
# 5. DEFINE CONFLICT RESOLUTION & CLEANED DATASET CREATION
# -------------------------------------------------------------
print("\n[Step 1.6] Creating Cleaned Groundwater Dataset...")

# Step A: Remove exact duplicates (done above)
# Step B: For 44 identical groups, keep the first record
# Step C: For 539 conflicting groups, do not fabricate synthetic average.
# In statistical regression, injecting conflicting readings for identical (well, date) features creates
# contradictory training labels. In our cleaned dataset, we exclude the conflicting well-date pairs
# from training data, while keeping all original rows in the audit file.
# Step D: Keep negative and zero readings as valid hydrological observations.
# Step E: Flag or exclude NaN targets for supervised modeling.

# Set of conflicting (Well ID, Date of Monitoring)
conflicting_keys = set(zip(df_conflict_audit['Well ID'], df_conflict_audit['Date of Monitoring']))

# Function to tag rows
clean_df = df_gw_no_exact.copy()

# Deduplicate identical groups by dropping duplicate (Well ID, Date of Monitoring) where target is identical
# Group by Well ID and Date of Monitoring, if not conflicting, keep first
non_conflicting_mask = ~clean_df.apply(lambda r: (r['Well ID'], r['Date of Monitoring']) in conflicting_keys, axis=1)

# Inside non-conflicting, drop duplicate (Well ID, Date of Monitoring) to resolve the 44 identical groups
clean_non_conflicting = clean_df[non_conflicting_mask].drop_duplicates(subset=['Well ID', 'Date of Monitoring'])

# For conflicting groups, we create two versions:
# 1) Cleaned version for ML: excludes the 539 unresolvable conflicting pairs (1,078 records) to prevent label contradiction.
# 2) Full cleaned version with audit flag: keeps all, tagging them.
clean_non_conflicting['Data_Quality_Flag'] = 'Clean'

# Also examine missing targets:
clean_valid_target = clean_non_conflicting[clean_non_conflicting['Water Level, m bgl'].notna()].copy()
print(f"Final Cleaned Groundwater Dataset (valid target, resolved duplicates, no label conflict):")
print(f"Total Rows: {len(clean_valid_target):,}")

# Save cleaned groundwater dataset
clean_gw_csv = os.path.join(out_clean_dir, "cleaned_groundwater_level.csv")
clean_valid_target.to_csv(clean_gw_csv, index=False)
print(f"Saved Cleaned Groundwater Dataset to: {clean_gw_csv}")

# -------------------------------------------------------------
# 6. RAINFALL DATASET AUDIT & CLEANING
# -------------------------------------------------------------
print("\n[Step 1.7] Auditing and Cleaning Rainfall Dataset...")
df_rf = pd.read_csv(rf_raw_path, encoding='utf-8', low_memory=False)
print(f"Raw Rainfall Rows: {len(df_rf):,}, Columns: {df_rf.shape[1]}")

df_rf.columns = [c.strip() for c in df_rf.columns]
for col in df_rf.select_dtypes(include='object').columns:
    df_rf[col] = df_rf[col].astype(str).str.strip()

df_rf['Date'] = pd.to_datetime(df_rf['Data Acquisition Time'], format='mixed', dayfirst=True)

# Standardize District names in Rainfall
# Mapping documented:
district_name_map = {
    'AHMADNAGAR': 'AHMEDNAGAR'
}
df_rf['District_Standardized'] = df_rf['District'].str.upper().replace(district_name_map)
clean_valid_target['District_Standardized'] = clean_valid_target['District Name'].str.upper()

# Verify district alignment
gw_dists = set(clean_valid_target['District_Standardized'].unique())
rf_dists = set(df_rf['District_Standardized'].unique())
common_dists = gw_dists.intersection(rf_dists)
print(f"Standardized Common Districts between GW and RF: {len(common_dists)} of 33")
print(f"Groundwater districts not in Rainfall: {gw_dists - rf_dists}")
print(f"Rainfall districts not in Groundwater: {rf_dists - gw_dists}")

# Save cleaned daily rainfall
clean_rf_csv = os.path.join(out_clean_dir, "cleaned_rainfall_daily.csv")
df_rf.to_csv(clean_rf_csv, index=False)
print(f"Saved Cleaned Rainfall Dataset to: {clean_rf_csv}")

# -------------------------------------------------------------
# 7. GENERATE COMPREHENSIVE DATA DICTIONARIES
# -------------------------------------------------------------
print("\n[Step 1.8] Generating Data Dictionaries...")

gw_dict_data = [
    {"Column Name": "Well ID", "Data Type": "String (Categorical)", "Unit": "Alphanumeric Code", "Description": "Unique identifier assigned to each monitoring well by CGWB/GSDA."},
    {"Column Name": "State Name", "Data Type": "String (Categorical)", "Unit": "Name", "Description": "State where the monitoring station is located (Maharashtra)."},
    {"Column Name": "District Name", "Data Type": "String (Categorical)", "Unit": "Name", "Description": "Administrative district in Maharashtra (33 districts)."},
    {"Column Name": "Block Name", "Data Type": "String (Categorical)", "Unit": "Name", "Description": "Sub-district / Taluka / Block administrative division."},
    {"Column Name": "Village", "Data Type": "String (Categorical)", "Unit": "Name", "Description": "Village or locality where the monitoring well is situated."},
    {"Column Name": "Site Name (If any)", "Data Type": "String (Categorical)", "Unit": "Name", "Description": "Specific site or landmark designation."},
    {"Column Name": "Aquifer Tapped", "Data Type": "String (Categorical)", "Unit": "Classification", "Description": "Geological aquifer type (primarily Unconfined in this dataset)."},
    {"Column Name": "Agency", "Data Type": "String (Categorical)", "Unit": "Organization", "Description": "Data collecting government agency (GSDA-Maharashtra)."},
    {"Column Name": "Latitude", "Data Type": "Float (Numeric)", "Unit": "Decimal Degrees (°N)", "Description": "Geographic latitude coordinate of the well."},
    {"Column Name": "Longitude", "Data Type": "Float (Numeric)", "Unit": "Decimal Degrees (°E)", "Description": "Geographic longitude coordinate of the well."},
    {"Column Name": "Well Type", "Data Type": "String (Categorical)", "Unit": "Classification", "Description": "Type of well infrastructure (Dug Well, Piezometer)."},
    {"Column Name": "Well Depth, m", "Data Type": "Float (Numeric)", "Unit": "Metres (m)", "Description": "Total drilled depth of the well below the surface."},
    {"Column Name": "Date of Monitoring", "Data Type": "String / Date", "Unit": "DD-MM-YYYY", "Description": "Observation date of the manual water level reading."},
    {"Column Name": "Water Level, m bgl", "Data Type": "Float (Numeric - TARGET)", "Unit": "Metres Below Ground Level (m bgl)", "Description": "Depth from ground surface to water table. A LARGER positive number denotes a DEEPER water table (less water). Negative numbers indicate artesian head above datum."}
]

df_gw_dict = pd.DataFrame(gw_dict_data)
df_gw_dict.to_csv(os.path.join(out_dict_dir, "groundwater_data_dictionary.csv"), index=False)

rf_dict_data = [
    {"Column Name": "SlNo", "Data Type": "Integer", "Unit": "Index", "Description": "Sequential row identifier."},
    {"Column Name": "Station", "Data Type": "String (Categorical)", "Unit": "Name", "Description": "Rainfall gauge station name."},
    {"Column Name": "Agency", "Data Type": "String (Categorical)", "Unit": "Organization", "Description": "Reporting agency."},
    {"Column Name": "State LGD Code", "Data Type": "Integer", "Unit": "LGD Code", "Description": "Local Government Directory code for Maharashtra."},
    {"Column Name": "State", "Data Type": "String (Categorical)", "Unit": "Name", "Description": "State name (Maharashtra)."},
    {"Column Name": "District LGD Code", "Data Type": "Integer", "Unit": "LGD Code", "Description": "Local Government Directory code for District."},
    {"Column Name": "District", "Data Type": "String (Categorical)", "Unit": "Name", "Description": "District name where the rain gauge is situated."},
    {"Column Name": "Tehsil", "Data Type": "String (Categorical)", "Unit": "Name", "Description": "Tehsil administrative area."},
    {"Column Name": "Block", "Data Type": "String (Categorical)", "Unit": "Name", "Description": "Block administrative division."},
    {"Column Name": "Village", "Data Type": "String (Categorical)", "Unit": "Name", "Description": "Village where station is located."},
    {"Column Name": "River / Basin", "Data Type": "String (Categorical)", "Unit": "Hydrography", "Description": "Hydrological river basin and drainage hierarchy."},
    {"Column Name": "Latitude", "Data Type": "Float (Numeric)", "Unit": "Decimal Degrees (°N)", "Description": "Geographic latitude coordinate of the rain gauge."},
    {"Column Name": "Longitude", "Data Type": "Float (Numeric)", "Unit": "Decimal Degrees (°E)", "Description": "Geographic longitude coordinate of the rain gauge."},
    {"Column Name": "Data Acquisition Time", "Data Type": "String / Datetime", "Unit": "DD-MM-YYYY HH:MM", "Description": "Timestamp of manual rainfall acquisition (standard 08:30 AM)."},
    {"Column Name": "Manual Daily Rainfall (mm)", "Data Type": "Float (Numeric)", "Unit": "Millimetres (mm)", "Description": "Measured precipitation accumulated over 24 hours."}
]

df_rf_dict = pd.DataFrame(rf_dict_data)
df_rf_dict.to_csv(os.path.join(out_dict_dir, "rainfall_data_dictionary.csv"), index=False)

# Also generate a markdown Data Dictionary
with open(os.path.join(out_dict_dir, "DATA_DICTIONARY.md"), "w", encoding='utf-8') as f:
    f.write("# AquaGuard AI – Master Data Dictionary & Variable Definitions\n\n")
    f.write("## 1. Groundwater Monitoring Dataset\n\n")
    f.write("| Column Name | Data Type | Unit | Description |\n")
    f.write("| :--- | :--- | :--- | :--- |\n")
    for row in gw_dict_data:
        f.write(f"| **{row['Column Name']}** | {row['Data Type']} | {row['Unit']} | {row['Description']} |\n")
    f.write("\n\n## 2. Rainfall Monitoring Dataset\n\n")
    f.write("| Column Name | Data Type | Unit | Description |\n")
    f.write("| :--- | :--- | :--- | :--- |\n")
    for row in rf_dict_data:
        f.write(f"| **{row['Column Name']}** | {row['Data Type']} | {row['Unit']} | {row['Description']} |\n")

print("Data dictionaries generated successfully.")
print("\nPhase 1 Completed Successfully!")
