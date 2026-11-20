import sys
import io
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set UTF-8 encoding for standard output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set aesthetic visualization style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

os.makedirs('reports/figures', exist_ok=True)

print("="*80)
print("STAGE 2: STATISTICAL ANALYSIS & EXPLORATORY DATA ANALYSIS (EDA)")
print("="*80)

# ==============================================================================
# PART A: STATISTICAL ANALYSIS - DATASET 1 (mh_gw_2025.csv)
# ==============================================================================
df_gw = pd.read_csv('data/raw/mh_gw_2025.csv')
# Filter out the 2 aggregate summary rows
df_dist = df_gw[df_gw['Sl. No'].notnull()].copy()

print("\n>>> 1. STATISTICAL METRICS: MAHARASHTRA GROUNDWATER RESOURCES (N=36 Districts)")
key_resource_cols = [
    'Annual Extractable Groundwater Resource',
    'Irrigation - Annual extraction',
    'Domestic - Annual Extraction',
    'Total Annual Extraction',
    'Net GW availability for future',
    'Stage of GW extraction (%)'
]

stats_resource = pd.DataFrame(index=key_resource_cols)
stats_resource['Mean'] = df_dist[key_resource_cols].mean()
stats_resource['Median'] = df_dist[key_resource_cols].median()
stats_resource['Std_Dev'] = df_dist[key_resource_cols].std()
stats_resource['Min'] = df_dist[key_resource_cols].min()
stats_resource['Q1_25%'] = df_dist[key_resource_cols].quantile(0.25)
stats_resource['Q2_50%'] = df_dist[key_resource_cols].quantile(0.50)
stats_resource['Q3_75%'] = df_dist[key_resource_cols].quantile(0.75)
stats_resource['IQR'] = stats_resource['Q3_75%'] - stats_resource['Q1_25%']
stats_resource['Max'] = df_dist[key_resource_cols].max()

print(stats_resource.round(2).to_string())

# Correlation analysis for Groundwater Resource Variables
print("\n--- Correlation Analysis: Groundwater Resources vs. Stage of Extraction ---")
corr_matrix_resource = df_dist[key_resource_cols].corr()
print(corr_matrix_resource.round(3).to_string())

# ==============================================================================
# PART B: STATISTICAL ANALYSIS - DATASET 2 (Chemical Water Quality)
# ==============================================================================
df_wq = pd.read_csv('data/raw/gwq_chemical_parameter_manual_cgwb_an_1961_2025.csv')

key_chem_cols = [
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

for col in key_chem_cols:
    df_wq[col] = pd.to_numeric(df_wq[col], errors='coerce')

# Complete TDS where missing using standard hydrogeological conversion (TDS ≈ 0.64 * EC)
df_wq['TDS_Filled (mg/L)'] = df_wq['Total Dissolved Solids (mg/L)'].fillna(df_wq['Electric Conductivity (μS/cm)'] * 0.64)

all_stat_chem = key_chem_cols + ['TDS_Filled (mg/L)']

print("\n>>> 2. STATISTICAL METRICS: GROUNDWATER QUALITY CHEMICAL PARAMETERS (N=634)")
stats_chem = pd.DataFrame(index=all_stat_chem)
stats_chem['Valid_Count'] = df_wq[all_stat_chem].count()
stats_chem['Mean'] = df_wq[all_stat_chem].mean()
stats_chem['Median'] = df_wq[all_stat_chem].median()
stats_chem['Std_Dev'] = df_wq[all_stat_chem].std()
stats_chem['Min'] = df_wq[all_stat_chem].min()
stats_chem['Q1_25%'] = df_wq[all_stat_chem].quantile(0.25)
stats_chem['Q2_50%'] = df_wq[all_stat_chem].quantile(0.50)
stats_chem['Q3_75%'] = df_wq[all_stat_chem].quantile(0.75)
stats_chem['IQR'] = stats_chem['Q3_75%'] - stats_chem['Q1_25%']
stats_chem['Max'] = df_wq[all_stat_chem].max()

print(stats_chem.round(2).to_string())

# Correlation analysis among chemical parameters
print("\n--- Correlation Analysis: Core Chemical Parameters ---")
chem_corr_cols = ['Potential of Hydrogen (pH)', 'Electric Conductivity (μS/cm)', 'TDS_Filled (mg/L)', 'Total Hardness (mgCaCO3/L)', 'Calcium (mg/L)', 'Magnesium (mg/L)', 'Chloride (mg/L)', 'Sulphate (mg/L)']
corr_matrix_chem = df_wq[chem_corr_cols].corr()
print(corr_matrix_chem.round(3).to_string())

# ==============================================================================
# PART C: EXPLORATORY DATA ANALYSIS (EDA) - 7 VISUALIZATIONS
# ==============================================================================
print("\n>>> 3. GENERATING 7 PUBLICATION-QUALITY VISUALIZATIONS...")

# Assign official CGWB Category for plotting
def get_cat(soe):
    if soe <= 70: return 'Safe'
    elif soe <= 90: return 'Semi-Critical'
    elif soe <= 100: return 'Critical'
    else: return 'Over-Exploited'

df_dist['CGWB_Category'] = df_dist['Stage of GW extraction (%)'].apply(get_cat)

# ------------------------------------------------------------------------------
# Visualization 1: Distribution of Groundwater Extraction Percentages
# ------------------------------------------------------------------------------
plt.figure(figsize=(10, 6))
sns.histplot(df_dist['Stage of GW extraction (%)'], kde=True, bins=12, color='#2b5c8f', edgecolor='black', alpha=0.7)
plt.axvline(70, color='orange', linestyle='--', linewidth=2, label='CGWB Safe / Semi-Critical Threshold (70%)')
plt.axvline(90, color='red', linestyle='--', linewidth=2, label='CGWB Semi-Critical / Critical Threshold (90%)')
plt.axvline(df_dist['Stage of GW extraction (%)'].mean(), color='green', linestyle=':', linewidth=2, label=f'State Mean ({df_dist["Stage of GW extraction (%)"].mean():.1f}%)')
plt.axvline(df_dist['Stage of GW extraction (%)'].median(), color='purple', linestyle='-.', linewidth=2, label=f'State Median ({df_dist["Stage of GW extraction (%)"].median():.1f}%)')

plt.title('Visualization 1: Distribution of Stage of Groundwater Extraction across Maharashtra Districts', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Stage of Groundwater Extraction (%)', fontsize=11, fontweight='bold')
plt.ylabel('Number of Districts (Frequency)', fontsize=11, fontweight='bold')
plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper right')
plt.tight_layout()
fig1_path = 'reports/figures/01_stage_of_extraction_distribution.png'
plt.savefig(fig1_path, dpi=300)
plt.close()
print(f"  [Saved] {fig1_path}")

# ------------------------------------------------------------------------------
# Visualization 2: District-wise Groundwater Resource Comparison (Top vs Bottom Extraction)
# ------------------------------------------------------------------------------
df_sorted = df_dist.sort_values(by='Stage of GW extraction (%)', ascending=True)

plt.figure(figsize=(12, 11))
colors = ['#d95f02' if cat == 'Semi-Critical' else '#2b83ba' for cat in df_sorted['CGWB_Category']]
bars = plt.barh(df_sorted['Name of District'], df_sorted['Stage of GW extraction (%)'], color=colors, edgecolor='grey', height=0.65)
plt.axvline(70, color='orange', linestyle='--', linewidth=2, label='Safe Threshold (70%)')

# Annotate values
for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.8, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', va='center', ha='left', fontsize=8, color='black', fontweight='semibold')

# Custom legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#d95f02', edgecolor='grey', label='Semi-Critical (70% - 90%) - 5 Districts'),
    Patch(facecolor='#2b83ba', edgecolor='grey', label='Safe (≤ 70%) - 31 Districts'),
    plt.Line2D([0], [0], color='orange', linestyle='--', linewidth=2, label='Threshold (70%)')
]
plt.legend(handles=legend_elements, loc='lower right', frameon=True, facecolor='white', framealpha=0.9)

plt.title('Visualization 2: District-wise Stage of Groundwater Extraction in Maharashtra (CGWB 2025)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Stage of Groundwater Extraction (%)', fontsize=11, fontweight='bold')
plt.ylabel('Name of District', fontsize=11, fontweight='bold')
plt.xlim(0, 95)
plt.tight_layout()
fig2_path = 'reports/figures/02_district_groundwater_resource_comparison.png'
plt.savefig(fig2_path, dpi=300)
plt.close()
print(f"  [Saved] {fig2_path}")

# ------------------------------------------------------------------------------
# Visualization 3: Correlation Heatmap of Groundwater Resource Variables
# ------------------------------------------------------------------------------
plt.figure(figsize=(10, 8))
res_features_full = [
    'Monsoon season recharge from rainfall (bcm)',
    'Monsoon season recharge from other sources',
    'Non-monsoon season recharge from other sources',
    'Total annual groundwater recharge',
    'Total Natural Discharges',
    'Annual Extractable Groundwater Resource',
    'Irrigation - Annual extraction',
    'Domestic - Annual Extraction',
    'Total Annual Extraction',
    'Net GW availability for future',
    'Stage of GW extraction (%)'
]
short_labels = [
    'Monsoon Rain Rech.',
    'Monsoon Other Rech.',
    'Non-Monsoon Other Rech.',
    'Total Annual Rech.',
    'Natural Discharges',
    'Extractable Resource',
    'Irrigation Extraction',
    'Domestic Extraction',
    'Total Extraction',
    'Net Future Avail.',
    'Stage of Extraction (%)'
]

corr_full = df_dist[res_features_full].corr()
corr_full.columns = short_labels
corr_full.index = short_labels

mask = np.triu(np.ones_like(corr_full, dtype=bool))
cmap = sns.diverging_palette(230, 20, as_cmap=True)

sns.heatmap(corr_full, mask=mask, cmap=cmap, vmin=-1, vmax=1, annot=True, fmt=".2f", linewidths=0.5, cbar_kws={"shrink": 0.8})
plt.title('Visualization 3: Pearson Correlation Heatmap of Groundwater Resource Attributes', fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
fig3_path = 'reports/figures/03_groundwater_resource_correlation_heatmap.png'
plt.savefig(fig3_path, dpi=300)
plt.close()
print(f"  [Saved] {fig3_path}")

# ------------------------------------------------------------------------------
# Visualization 4: Distribution of pH Values in Groundwater Quality Dataset
# ------------------------------------------------------------------------------
plt.figure(figsize=(10, 6))
sns.histplot(df_wq['Potential of Hydrogen (pH)'].dropna(), kde=True, bins=25, color='#1b9e77', edgecolor='black', alpha=0.7)
plt.axvline(6.5, color='red', linestyle='--', linewidth=2, label='BIS Lower Acceptable Limit (pH 6.5)')
plt.axvline(8.5, color='crimson', linestyle='--', linewidth=2, label='BIS Upper Acceptable Limit (pH 8.5)')
mean_ph = df_wq['Potential of Hydrogen (pH)'].mean()
median_ph = df_wq['Potential of Hydrogen (pH)'].median()
plt.axvline(mean_ph, color='darkblue', linestyle=':', linewidth=2, label=f'Sample Mean pH ({mean_ph:.2f})')
plt.axvline(median_ph, color='purple', linestyle='-.', linewidth=2, label=f'Sample Median pH ({median_ph:.2f})')

# Shaded desirable zone
plt.axvspan(6.5, 8.5, color='green', alpha=0.1, label='BIS Potable Zone (6.5 - 8.5)')

plt.title('Visualization 4: Frequency Distribution of Groundwater pH Values (BIS IS 10500:2012 Compliance)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Potential of Hydrogen (pH Units)', fontsize=11, fontweight='bold')
plt.ylabel('Number of Groundwater Samples', fontsize=11, fontweight='bold')
plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')
plt.tight_layout()
fig4_path = 'reports/figures/04_water_quality_ph_distribution.png'
plt.savefig(fig4_path, dpi=300)
plt.close()
print(f"  [Saved] {fig4_path}")

# ------------------------------------------------------------------------------
# Visualization 5: Bivariate Distribution of TDS vs Electrical Conductivity
# ------------------------------------------------------------------------------
plt.figure(figsize=(10, 6))
# Filter extreme outlier in EC (>10000) for visual clarity of regression line
df_plot_ec = df_wq[df_wq['Electric Conductivity (μS/cm)'] < 10000].copy()

sns.scatterplot(
    data=df_plot_ec, 
    x='Electric Conductivity (μS/cm)', 
    y='TDS_Filled (mg/L)', 
    alpha=0.6, 
    color='#386cb0',
    edgecolor='w',
    s=45
)
# Add regression trendline
sns.regplot(
    data=df_plot_ec,
    x='Electric Conductivity (μS/cm)', 
    y='TDS_Filled (mg/L)',
    scatter=False,
    color='red',
    line_kws={'linestyle': '--', 'linewidth': 1.5, 'label': 'Hydrogeological Fit (TDS ≈ 0.64 · EC)'}
)

plt.axhline(500, color='green', linestyle=':', linewidth=1.5, label='BIS Desirable Limit (TDS 500 mg/L)')
plt.axhline(2000, color='darkorange', linestyle=':', linewidth=1.5, label='BIS Maximum Permissible Limit (TDS 2000 mg/L)')

plt.title('Visualization 5: Bivariate Relationship Between Electrical Conductivity (EC) and Total Dissolved Solids (TDS)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Electrical Conductivity (μS/cm at 25°C)', fontsize=11, fontweight='bold')
plt.ylabel('Total Dissolved Solids (mg/L)', fontsize=11, fontweight='bold')
plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')
plt.tight_layout()
fig5_path = 'reports/figures/05_tds_ec_bivariate_distribution.png'
plt.savefig(fig5_path, dpi=300)
plt.close()
print(f"  [Saved] {fig5_path}")

# ------------------------------------------------------------------------------
# Visualization 6: Boxplots of Major Chemical Parameters (Log Scale)
# ------------------------------------------------------------------------------
plt.figure(figsize=(12, 7))
box_cols = ['Calcium (mg/L)', 'Magnesium (mg/L)', 'Total Hardness (mgCaCO3/L)', 'Chloride (mg/L)', 'Sulphate (mg/L)']
box_short = ['Calcium\n(Ca²⁺)', 'Magnesium\n(Mg²⁺)', 'Total Hardness\n(as CaCO₃)', 'Chloride\n(Cl⁻)', 'Sulphate\n(SO₄²⁻)']

df_melt = df_wq[box_cols].melt(var_name='Chemical Parameter', value_name='Concentration (mg/L)')
df_melt['Chemical Parameter'] = df_melt['Chemical Parameter'].replace(dict(zip(box_cols, box_short)))

sns.boxplot(x='Chemical Parameter', y='Concentration (mg/L)', data=df_melt, palette='Set2', showmeans=True, meanprops={"marker":"o", "markerfacecolor":"red", "markeredgecolor":"black", "markersize":"6"})
plt.yscale('log')
plt.title('Visualization 6: Concentration Distributions of Core Anions & Cations (Logarithmic Scale)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Chemical Parameter (mg/L)', fontsize=11, fontweight='bold')
plt.ylabel('Concentration in mg/L (Log Scale)', fontsize=11, fontweight='bold')
# Annotate red dot in legend
from matplotlib.lines import Line2D
legend_el = [Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markeredgecolor='black', markersize=8, label='Parametric Mean')]
plt.legend(handles=legend_el, loc='upper right', frameon=True, facecolor='white')

plt.tight_layout()
fig6_path = 'reports/figures/06_chemical_parameters_boxplots.png'
plt.savefig(fig6_path, dpi=300)
plt.close()
print(f"  [Saved] {fig6_path}")

# ------------------------------------------------------------------------------
# Visualization 7: District-wise Groundwater Quality Compliance with BIS Standards
# ------------------------------------------------------------------------------
# Define BIS Desirable / Acceptable Compliance
ph_ok = (df_wq['Potential of Hydrogen (pH)'] >= 6.5) & (df_wq['Potential of Hydrogen (pH)'] <= 8.5)
tds_ok = df_wq['TDS_Filled (mg/L)'] <= 500
th_ok = df_wq['Total Hardness (mgCaCO3/L)'].isna() | (df_wq['Total Hardness (mgCaCO3/L)'] <= 200)
cl_ok = df_wq['Chloride (mg/L)'].isna() | (df_wq['Chloride (mg/L)'] <= 250)
so4_ok = df_wq['Sulphate (mg/L)'].isna() | (df_wq['Sulphate (mg/L)'] <= 200)

df_wq['BIS_Compliant'] = ph_ok & tds_ok & th_ok & cl_ok & so4_ok

compliance_summary = df_wq.groupby('District')['BIS_Compliant'].value_counts(normalize=True).unstack().fillna(0) * 100
compliance_summary.columns = ['Exceeds Desirable Limits', 'Potable (Desirable)']

plt.figure(figsize=(9, 6))
compliance_summary.plot(kind='bar', stacked=True, color=['#e7298a', '#1b9e77'], edgecolor='black', figsize=(9, 6))
plt.title('Visualization 7: Groundwater Potability Compliance Rate by Monitoring District (BIS IS 10500:2012)', fontsize=12, fontweight='bold', pad=15)
plt.xlabel('Monitoring District', fontsize=11, fontweight='bold')
plt.ylabel('Percentage of Samples (%)', fontsize=11, fontweight='bold')
plt.xticks(rotation=0, fontweight='semibold')
plt.ylim(0, 100)
plt.legend(title='Water Quality Status', frameon=True, facecolor='white', loc='lower right')
plt.tight_layout()
fig7_path = 'reports/figures/07_water_quality_compliance_by_district.png'
plt.savefig(fig7_path, dpi=300)
plt.close()
print(f"  [Saved] {fig7_path}")

print("\nSTAGE 2 STATISTICAL ANALYSIS & EDA COMPLETED SUCCESSFULLY!")
