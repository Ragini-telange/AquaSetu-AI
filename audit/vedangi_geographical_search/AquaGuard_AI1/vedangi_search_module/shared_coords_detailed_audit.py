import pandas as pd, json, os, sys
from collections import defaultdict

# ------------------------------------------------------------
# 1️⃣ Verify CSV path (read‑only)
# ------------------------------------------------------------
CSV_PATH = (
    r"C:\Users\Vedangi\Documents\AquaGuard_AI1\datasets"
    r"\ground_water_level_manual_quarterly_maharashtra_1970_2025.csv"
)
if not os.path.isfile(CSV_PATH):
    sys.stderr.write(f"ERROR: CSV not found at {CSV_PATH}\n")
    sys.exit(1)

# ------------------------------------------------------------
# 2️⃣ Load dataset (latin‑1 encoding, low_memory=False)
# ------------------------------------------------------------
try:
    df = pd.read_csv(CSV_PATH, encoding="latin1", low_memory=False)
except Exception as exc:                     # pragma: no cover
    sys.stderr.write(f"ERROR while reading CSV: {exc}\n")
    sys.exit(1)

# ------------------------------------------------------------
# 3️⃣ Basic safety checks – required columns
# ------------------------------------------------------------
WELL_ID_COL = "Well ID"
LAT_COL = "Latitude "
LON_COL = "Longitude "
for col in (WELL_ID_COL, LAT_COL, LON_COL):
    if col not in df.columns:
        sys.stderr.write(f"ERROR: Expected column '{col}' missing.\n")
        sys.exit(1)

# Drop rows without a Well ID – they cannot be linked to a location.
# (We keep rows that may have missing lat/lon because we need the original values for the audit.)
df = df.dropna(subset=[WELL_ID_COL])

# ------------------------------------------------------------
# 4️⃣ Preserve original coordinates and also create rounded versions
# ------------------------------------------------------------
# Keep the raw (unrounded) values in separate columns for later audit.
df["orig_lat"] = df[LAT_COL]
df["orig_lon"] = df[LON_COL]
# Rounded coordinates (6 decimal places) for grouping.
# Using round() on NaN leaves NaN untouched.
df["lat_rounded"] = df[LAT_COL].round(6)
df["lon_rounded"] = df[LON_COL].round(6)

# ------------------------------------------------------------
# 5️⃣ Group by rounded coordinates, collecting needed aggregates
# ------------------------------------------------------------
def aggregate_group(g):
    return {
        "well_ids": list(sorted(set(g[WELL_ID_COL]))),
        "districts": list(sorted(set(g["District Name "].dropna()))),
        "blocks": list(sorted(set(g["Block Name "].dropna()))),
        "villages": list(sorted(set(g["Village "].dropna()))),
        "records": g[[WELL_ID_COL, "orig_lat", "orig_lon", "District Name ", "Block Name ", "Village "]]
                     .to_dict(orient="records"),
    }

grouped = (
    df.groupby(["lat_rounded", "lon_rounded"]).apply(aggregate_group)
      .reset_index(name="info")
)

# ------------------------------------------------------------
# 6️⃣ Keep only groups with multiple distinct villages (the 77 groups)
# ------------------------------------------------------------
multi_village = grouped[grouped["info"].apply(lambda i: len(i["villages"]) > 1)].copy()

# ------------------------------------------------------------
# 7️⃣ Detect exact‑original‑coordinate sharing across different wells
# ------------------------------------------------------------
def identical_original_coords(info):
    """Return True only when ≥2 different Well IDs share the *exact* original lat/lon.
    `info` contains a list of original records under the key "records".
    """
    coord_to_wells = defaultdict(set)
    for rec in info["records"]:
        wid = rec[WELL_ID_COL]
        coord = (rec["orig_lat"], rec["orig_lon"])
        coord_to_wells[coord].add(wid)
    return any(len(wids) > 1 for wids in coord_to_wells.values())

# Add the flag to each group
multi_village["info"] = multi_village["info"].apply(
    lambda i: {**i, "identical_original_coords": identical_original_coords(i)}
)

# ------------------------------------------------------------
# 8️⃣ Build concise per‑group summaries (no raw observation rows)
# ------------------------------------------------------------
per_group_summaries = []
for _, row in multi_village.iterrows():
    lat = row["lat_rounded"]
    lon = row["lon_rounded"]
    info = row["info"]
    per_group_summaries.append({
        "latitude_rounded": lat,
        "longitude_rounded": lon,
        "well_ids": info["well_ids"],
        "districts": info["districts"],
        "blocks": info["blocks"],
        "villages": info["villages"],
        "num_distinct_well_ids": len(info["well_ids"]),
        "identical_original_coords": info["identical_original_coords"],
    })

# ------------------------------------------------------------
# 9️⃣ Compute overall totals
# ------------------------------------------------------------
# Total number of multi‑village coordinate groups (should be 77)
total_multi_village_groups = int(multi_village.shape[0])
# Groups where different Well IDs share IDENTICAL original coordinates
groups_with_exact_match = int(
    multi_village["info"].apply(lambda i: i["identical_original_coords"]).sum()
)
# Groups where the match occurs ONLY after rounding
groups_rounding_only = total_multi_village_groups - groups_with_exact_match
# Total distinct Well IDs involved across all groups
all_well_ids = set()
for info in multi_village["info"]:
    all_well_ids.update(info["well_ids"])
total_distinct_well_ids = len(all_well_ids)
# Total groups involving multiple village names (same as total_multi_village_groups)
total_groups_multiple_villages = total_multi_village_groups
# Total groups involving multiple blocks (more than one distinct block in the group)
total_groups_multiple_blocks = int(
    multi_village["info"].apply(lambda i: len(i["blocks"]) > 1).sum()
)


# ------------------------------------------------------------
# 10️⃣ Print concise summary and per‑group details (JSON)
# ------------------------------------------------------------
summary = (
    f"Audited {total_multi_village_groups} coordinate groups audited.\n"
    f"- Groups where different Well IDs have exactly identical original latitude and longitude: {groups_with_exact_match}\n"
    f"- Groups that match only after rounding: {groups_rounding_only}\n"
    f"- Total number of distinct Well IDs involved: {total_distinct_well_ids}\n"
    f"- Total number of groups involving multiple village names: {total_groups_multiple_villages}\n"
    f"- Total number of groups involving multiple blocks: {total_groups_multiple_blocks}\n"
)
print(summary)
print("--- PER‑GROUP SUMMARY (JSON) START ---")
print(json.dumps(per_group_summaries, indent=2, ensure_ascii=False))
print("--- PER‑GROUP SUMMARY (JSON) END ---")
# ------------------------------------------------------------
# FINAL TOTALS (concise)
# ------------------------------------------------------------
final_totals = (
    f"FINAL TOTALS:\n"
    f"1. Total coordinate groups audited: {total_multi_village_groups}\n"
    f"2. Groups where different Well IDs have exactly identical original latitude and longitude: {groups_with_exact_match}\n"
    f"3. Groups that match only after rounding: {groups_rounding_only}\n"
    f"4. Total distinct Well IDs involved: {total_distinct_well_ids}\n"
    f"5. Number of groups involving multiple village names: {total_groups_multiple_villages}\n"
    f"6. Number of groups involving multiple blocks: {total_groups_multiple_blocks}"
)
print(final_totals)
