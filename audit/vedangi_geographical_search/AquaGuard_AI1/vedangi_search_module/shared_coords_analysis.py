import pandas as pd, json, os, sys

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
# 3️⃣ Basic safety checks
# ------------------------------------------------------------
WELL_ID_COL = "Well ID"
LAT_COL = "Latitude "
LON_COL = "Longitude "

for col in (WELL_ID_COL, LAT_COL, LON_COL):
    if col not in df.columns:
        sys.stderr.write(f"ERROR: Expected column '{col}' missing.\n")
        sys.exit(1)

# Drop rows that lack a Well ID – they cannot be linked to a location.
df = df.dropna(subset=[WELL_ID_COL])

# ------------------------------------------------------------
# 4️⃣ Round coordinates to 6 decimal places (removes noise)
# ------------------------------------------------------------
coords_rounded = df[[LAT_COL, LON_COL]].round(6)
df["lat_rounded"] = coords_rounded[LAT_COL]
df["lon_rounded"] = coords_rounded[LON_COL]

# ------------------------------------------------------------
# 5️⃣ Find coordinate groups shared by >1 distinct Well ID
# ------------------------------------------------------------
# Group by the rounded lat/lon pair
grouped = (
    df.groupby(["lat_rounded", "lon_rounded"])
    .agg(
        well_ids=(WELL_ID_COL, lambda ids: list(sorted(set(ids)))),
        districts=("District Name ", lambda x: list(sorted(set(x.dropna())))),
        blocks=("Block Name ", lambda x: list(sorted(set(x.dropna())))),
        villages=("Village ", lambda x: list(sorted(set(x.dropna())))),
    )
    .reset_index()
)

# Keep only groups where at least two *different* wells share the same point
shared = grouped[grouped["well_ids"].apply(len) > 1].copy()

# ------------------------------------------------------------
# 6️⃣ Summary statistics
# ------------------------------------------------------------
# a) Number of distinct Well IDs that appear in any shared coordinate
distinct_well_ids = set()
for ids in shared["well_ids"]:
    distinct_well_ids.update(ids)
num_distinct_well_ids = len(distinct_well_ids)

# b) How many shared groups have all wells in the *same* village?
same_village_cnt = 0
different_village_cnt = 0
for villages in shared["villages"]:
    if len(villages) == 1:
        same_village_cnt += 1
    else:
        different_village_cnt += 1

# ------------------------------------------------------------
# 7️⃣ Build the report (JSON)
# ------------------------------------------------------------
report = {
    "distinct_well_ids_sharing_coordinates": num_distinct_well_ids,
    "total_shared_coordinate_groups": int(shared.shape[0]),  # should be 184
    "shared_coordinate_examples": [],  # up to 20 examples
    "shared_groups_same_village": same_village_cnt,
    "shared_groups_multiple_villages": different_village_cnt,
    "explanation": (
        "Each entry below shows a latitude‑longitude pair that is linked to "
        "more than one Well ID.  For every group we list the unique Well IDs "
        "and the distinct districts/blocks/villages that appear at that spot. "
        "If the 'villages' list has length 1 the wells belong to the same "
        "village; otherwise they span different villages."
    ),
}

# Add up to 20 examples (sorted by latitude just for deterministic output)
example_subset = shared.head(20)
for _, row in example_subset.iterrows():
    report["shared_coordinate_examples"].append(
        {
            "latitude": row["lat_rounded"],
            "longitude": row["lon_rounded"],
            "well_ids": row["well_ids"],
            "districts": row["districts"],
            "blocks": row["blocks"],
            "villages": row["villages"],
        }
    )

# ------------------------------------------------------------
# 8️⃣ Print JSON (stdout) – read‑only, no file writes
# ------------------------------------------------------------
print(json.dumps(report, indent=2, ensure_ascii=False))
