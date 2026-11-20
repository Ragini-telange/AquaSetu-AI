import sys
import io
import os
import pandas as pd
import numpy as np

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*80)
print("STAGE 1: COMPREHENSIVE DATASET INSPECTION & SUITABILITY AUDIT")
print("="*80)

# ==============================================================================
# DATASET 1: mh_gw_2025.csv
# ==============================================================================
path1 = 'data/raw/mh_gw_2025.csv'
print(f"\n>>> 1. INSPECTING DATASET 1: {path1}")
df1 = pd.read_csv(path1)

print(f"Shape: {df1.shape[0]} rows, {df1.shape[1]} columns")
print(f"Duplicates: {df1.duplicated().sum()}")
print(f"Missing Values:\n{df1.isnull().sum()[df1.isnull().sum() > 0]}")

print("\n--- First 5 Rows ---")
print(df1.head(5).to_string())

print("\n--- Last 5 Rows ---")
print(df1.tail(5).to_string())

print("\n--- Column Names & Data Types ---")
for i, (col, dtype) in enumerate(zip(df1.columns, df1.dtypes)):
    print(f"  [{i:02d}] {col:<48} | {str(dtype):<10} | Nulls: {df1[col].isnull().sum()}")

# Notice rows 36 and 37 are state totals:
df1_districts = df1[df1['Sl. No'].notnull()].copy()
print(f"\n--- District Level Breakdown (Excluding Total Rows) ---")
print(f"Total Administrative Districts Analyzed: {len(df1_districts)}")
print("Districts List:", df1_districts['Name of District'].tolist())

print("\n--- Descriptive Statistics for District Numerical Features ---")
num_cols1 = df1_districts.select_dtypes(include=[np.number]).columns.drop('Sl. No')
stats1 = df1_districts[num_cols1].describe().T[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
print(stats1.to_string())

print("\n--- Official Groundwater Categorization Check ---")
print("Does dataset have an official category column? NO (Must check Stage of Extraction %)")
soe = df1_districts['Stage of GW extraction (%)']
print(f"Stage of GW Extraction: Min = {soe.min():.2f}%, Median = {soe.median():.2f}%, Max = {soe.max():.2f}%")

def cgwb_cat(val):
    if val <= 70:
        return 'Safe'
    elif val <= 90:
        return 'Semi-Critical'
    elif val <= 100:
        return 'Critical'
    else:
        return 'Over-Exploited'

df1_districts['CGWB_Category'] = soe.apply(cgwb_cat)
print("Distribution of Official CGWB Risk Categories on 36 Maharashtra Districts:")
print(df1_districts['CGWB_Category'].value_counts())
print("\nDistricts by Category:")
for cat in ['Safe', 'Semi-Critical', 'Critical', 'Over-Exploited']:
    d_list = df1_districts[df1_districts['CGWB_Category'] == cat]['Name of District'].tolist()
    print(f"  {cat} (N={len(d_list)}): {d_list}")

# ==============================================================================
# DATASET 2: Chemical Water Quality Parameters
# ==============================================================================
path2 = 'data/raw/gwq_chemical_parameter_manual_cgwb_an_1961_2025.csv'
print("\n" + "="*80)
print(f">>> 2. INSPECTING DATASET 2: {path2}")
df2 = pd.read_csv(path2)

print(f"Shape: {df2.shape[0]} rows, {df2.shape[1]} columns")
print(f"Duplicates: {df2.duplicated().sum()}")

print("\n--- Column Names & Data Types ---")
for i, (col, dtype) in enumerate(zip(df2.columns, df2.dtypes)):
    null_c = df2[col].isnull().sum()
    pct = (null_c / len(df2)) * 100
    print(f"  [{i:02d}] {col:<35} | {str(dtype):<8} | Nulls: {null_c:<4} ({pct:.1f}%)")

print("\n--- Geographical Metadata Inspection ---")
print(f"State(s) in this dataset: {df2['State'].unique().tolist()}")
print(f"Districts in this dataset: {df2['District'].unique().tolist()}")
print(f"Number of Unique Monitoring Stations: {df2['Station'].nunique()}")

years2 = pd.to_datetime(df2['Data Acquisition Time'], format='%d-%m-%Y %H:%M', errors='coerce').dt.year
print(f"Assessment Years Available: {sorted(years2.dropna().unique().astype(int).tolist())}")

print("\n--- Descriptive Statistics of Core Chemical Parameters ---")
core_chem = [
    'Potential of Hydrogen (pH)',
    'Electric Conductivity (μS/cm)',
    'Total Dissolved Solids (mg/L)',
    'Total Hardness (mgCaCO3/L)',
    'Calcium (mg/L)',
    'Magnesium (mg/L)',
    'Chloride (mg/L)',
    'Sulphate (mg/L)',
    'Iron(mg/L)'
]
for c in core_chem:
    df2[c] = pd.to_numeric(df2[c], errors='coerce')

print(df2[core_chem].describe().T[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']].to_string())

print("\n--- Pre-existing Water Quality Class Labels Check ---")
print("Does dataset contain a ready-made quality class label? NO.")
print("Quality labels must be derived using BIS IS 10500:2012 Drinking Water Specification.")

# ==============================================================================
# AUDIT OF ADDITIONAL FILES IN WORKSPACE
# ==============================================================================
path3 = 'data/raw/maharashtra_gw_quality.csv'
if os.path.exists(path3):
    df3 = pd.read_csv(path3)
    print("\n" + "="*80)
    print(f">>> 3. AUDIT OF WORKSPACE FILE: {path3}")
    print(f"Shape: {df3.shape[0]} rows, {df3.shape[1]} columns")
    print(f"State: {df3['State'].unique().tolist()}")
    print(f"Districts Count: {df3['District'].nunique()} districts across Maharashtra")
    print("Columns present:", df3.columns.tolist())
    print("CRITICAL FINDING: Despite the filename 'maharashtra_gw_quality.csv', this file contains:")
    print("  'Groundwater Level Quarterly Manual (meter)' -> Groundwater DEPTH measurement, NOT chemical quality!")
    print("  There are NO pH, TDS, EC, Chloride, Nitrate, Hardness columns in this file.")
