import pandas as pd
import os
import sys
from pathlib import Path

# ------------------------------------------------------------
# 1️⃣ Load the original groundwater CSV (read‑only)
# ------------------------------------------------------------
CSV_PATH = (
    r"C:\Users\Vedangi\Documents\AquaGuard_AI1\datasets"
    r"\ground_water_level_manual_quarterly_maharashtra_1970_2025.csv"
)
if not os.path.isfile(CSV_PATH):
    sys.stderr.write(f"ERROR: CSV not found at {CSV_PATH}\n")
    sys.exit(1)

# Use latin‑1 encoding to handle any special characters in the source file.
# low_memory=False ensures consistent dtype inference for this large file.
try:
    df = pd.read_csv(CSV_PATH, encoding="latin1", low_memory=False)
except Exception as exc:  # pragma: no cover
    sys.stderr.write(f"ERROR while reading CSV: {exc}\n")
    sys.exit(1)

# ------------------------------------------------------------
# 2️⃣ Basic safety checks – required columns
# ------------------------------------------------------------
WELL_ID_COL = "Well ID"
LAT_COL = "Latitude "
LON_COL = "Longitude "
VILLAGE_COL = "Village "
BLOCK_COL = "Block Name "
DISTRICT_COL = "District Name "

required_cols = [WELL_ID_COL, LAT_COL, LON_COL, VILLAGE_COL, BLOCK_COL, DISTRICT_COL]
for col in required_cols:
    if col not in df.columns:
        sys.stderr.write(f"ERROR: Expected column '{col}' missing in CSV.\n")
        sys.exit(1)

# ------------------------------------------------------------
# 3️⃣ Preserve all original Well IDs – drop rows that lack a Well ID (they cannot be linked).
# ------------------------------------------------------------
# Missing Well IDs are considered data‑quality issues; we remove them from the
# grouping but will report them in the validation step.
initial_row_count = df.shape[0]
df = df.dropna(subset=[WELL_ID_COL])
unique_well_ids = df[WELL_ID_COL].nunique()

# ------------------------------------------------------------
# 4️⃣ Group by *exact* original latitude‑longitude (no rounding).
# ------------------------------------------------------------
# Some rows may have missing coordinates – we keep them separate for reporting
# but they are excluded from the location grouping.
has_coords = df[LAT_COL].notna() & df[LON_COL].notna()
coord_groups = (
    df[has_coords]
      .groupby([LAT_COL, LON_COL])
      .agg(
          well_ids=(WELL_ID_COL, lambda ids: sorted(set(ids))),
          villages=(VILLAGE_COL, lambda vals: sorted(set(v for v in vals if pd.notna(v)))),
          blocks=(BLOCK_COL, lambda vals: sorted(set(b for b in vals if pd.notna(b)))),
          districts=(DISTRICT_COL, lambda vals: sorted(set(d for d in vals if pd.notna(d)))),
      )
      .reset_index()
)

# Assign a deterministic unique location_id (starting from 1).
coord_groups.insert(0, "location_id", range(1, len(coord_groups) + 1))

# ------------------------------------------------------------
# 5️⃣ Build the geographical locations dataset
# ------------------------------------------------------------
# Convert list columns to a pipe‑separated string for CSV friendliness.
loc_df = coord_groups.copy()
loc_df["well_ids"] = loc_df["well_ids"].apply(lambda lst: "|".join(lst))
loc_df["villages"] = loc_df["villages"].apply(lambda lst: "|".join(lst))
loc_df["blocks"] = loc_df["blocks"].apply(lambda lst: "|".join(lst))
loc_df["districts"] = loc_df["districts"].apply(lambda lst: "|".join(lst))
loc_df["num_well_ids"] = loc_df["well_ids"].apply(lambda s: len(s.split("|")))

# ------------------------------------------------------------
# 6️⃣ Build the well‑to‑location mapping dataset (one row per unique Well ID)
# ------------------------------------------------------------
# First, detect any Well IDs that have more than one distinct (lat, lon) pair.
# We'll keep a dict of conflicts to report later.
# Exclude rows with missing coordinates from the conflict check.
coords_present = df[LAT_COL].notna() & df[LON_COL].notna()
well_coord_groups = (
    df[coords_present]
      .groupby(WELL_ID_COL)
      .apply(lambda g: set(zip(g[LAT_COL], g[LON_COL])))
)
conflict_well_ids = {wid: pairs for wid, pairs in well_coord_groups.items() if len(pairs) > 1}

# For Well IDs without conflicts, pick the first available record (they all share the same coordinates).
# We'll also keep the first non‑missing metadata for village, block, district.
valid_well_ids = set(df[WELL_ID_COL].unique()) - set(conflict_well_ids.keys())
valid_records = (
    df[df[WELL_ID_COL].isin(valid_well_ids)]
      .sort_values([WELL_ID_COL, "Date of Monitoring"], na_position="last")
)
# Drop duplicate Well IDs, keeping the first occurrence (which now represents the unique coordinate/metadata).
well_unique = valid_records.drop_duplicates(subset=[WELL_ID_COL])

# Merge location_id for the valid wells (those with coordinates).
well_mapping_df = well_unique.merge(
    coord_groups[[LAT_COL, LON_COL, "location_id"]],
    on=[LAT_COL, LON_COL],
    how="left",
)
# Rename columns for the output file.
well_mapping_df = well_mapping_df[[WELL_ID_COL, LAT_COL, LON_COL, "location_id", VILLAGE_COL, BLOCK_COL, DISTRICT_COL]].copy()
well_mapping_df.rename(columns={
    WELL_ID_COL: "well_id",
    LAT_COL: "latitude",
    LON_COL: "longitude",
    VILLAGE_COL: "village",
    BLOCK_COL: "block",
    DISTRICT_COL: "district",
}, inplace=True)

# ------------------------------------------------------------
# 9️⃣ Validation report – printed to stdout when the script runs
# ------------------------------------------------------------
# Original counts (before dropping rows without Well ID)
original_rows = initial_row_count
# Unique Well IDs in the source (after dropping missing IDs)
unique_well_ids_source = df[WELL_ID_COL].nunique()
# Rows in the mapping file (should equal number of unique well IDs without conflicts)
rows_in_mapping = well_mapping_df.shape[0]
# Unique Well IDs present in the mapping file
unique_well_ids_mapping = well_mapping_df["well_id"].nunique()
# Detect missing Well IDs (source IDs not present in mapping)
missing_well_ids = unique_well_ids_source - unique_well_ids_mapping
# Number of geographical locations (same as earlier)
num_locations = loc_df.shape[0]
# Conflicting Well IDs report (if any)
conflict_report = (
    f"Conflicting Well IDs: {len(conflict_well_ids)}"
    if conflict_well_ids else "No conflicting Well IDs detected."
)

report = (
    "\n=== Validation Report ===\n"
    f"Original CSV row count: {original_rows}\n"
    f"Unique Well ID count in source: {unique_well_ids_source}\n"
    f"Rows in well_location_mapping.csv: {rows_in_mapping}\n"
    f"Unique Well IDs in mapping file: {unique_well_ids_mapping}\n"
    f"Well IDs missing from mapping? {'No' if missing_well_ids == 0 else f'Yes ({missing_well_ids} missing)'}\n"
    f"{conflict_report}\n"
    f"Number of geographical locations: {num_locations}\n"
    "==========================\n"
)
print(report)

# ------------------------------------------------------------
# 7️⃣ Prepare output directory
# ------------------------------------------------------------
output_dir = Path(__file__).parent / "processed_data"
output_dir.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# 8️⃣ Write CSV files (do not alter the source CSV)
# ------------------------------------------------------------
loc_output_path = output_dir / "groundwater_locations.csv"
well_output_path = output_dir / "well_location_mapping.csv"

loc_df.to_csv(loc_output_path, index=False)
well_mapping_df.to_csv(well_output_path, index=False)

# ------------------------------------------------------------
# 9️⃣ Validation report – printed to stdout when the script runs
# ------------------------------------------------------------
# Original counts (before dropping rows without Well ID)
original_rows = initial_row_count
# Unique Well IDs after dropping missing IDs
unique_well_ids_after = well_mapping_df["well_id"].nunique()
# Unique exact coordinate pairs (including only rows that have both lat & lon)
unique_coord_pairs = df[has_coords][[LAT_COL, LON_COL]].drop_duplicates().shape[0]
# Number of output geographical locations
num_locations = loc_df.shape[0]
# Number of Well IDs in the mapping file
num_well_ids_in_mapping = well_mapping_df.shape[0]
# Check for lost Well IDs (should be zero)
lost_well_ids = unique_well_ids - unique_well_ids_after
# Check for any missing coordinates in the original data
missing_coords = df[~has_coords].shape[0]

report = (
    "\n=== Validation Report ===\n"
    f"Original CSV row count: {original_rows}\n"
    f"Unique Well ID count (after dropping missing IDs): {unique_well_ids_after}\n"
    f"Unique exact latitude‑longitude pair count: {unique_coord_pairs}\n"
    f"Number of output geographical locations: {num_locations}\n"
    f"Number of Well IDs in the mapping file: {num_well_ids_in_mapping}\n"
    f"Any Well IDs lost? {'No' if lost_well_ids == 0 else f'Yes ({lost_well_ids} missing)'}\n"
    f"Any rows with missing coordinates? {'No' if missing_coords == 0 else f'Yes ({missing_coords} rows)'}\n"
    "==========================\n"
)
print(report)
