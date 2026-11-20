import json
import os

nb_path = "01_Ragini_Regression/notebooks/AquaGuard_Regression_Module.ipynb"
os.makedirs("01_Ragini_Regression/notebooks", exist_ok=True)

cells = []

def add_md(text):
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.split("\n")]
    })

def add_code(text):
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in text.split("\n")]
    })

# Title & Overview
add_md("""# AquaGuard AI – Groundwater Level Regression Module
### AI-Based Groundwater Level Prediction and Geographical Risk Assessment Using Machine Learning
**Author:** Ragini (Third-Year B.Tech Computer Engineering)  
**Module:** Part 1 – Regression (Groundwater Level Forecasting in Maharashtra, India)  
**Collaborators:** Sakshi (Classification Module), Vedangi (Search Algorithms Module)

---

### Project Overview & Objectives
Groundwater is Maharashtra's primary lifeline for agriculture and drinking water. Over-extraction and erratic monsoons have severely stressed aquifers across Maharashtra.

**Goal:**  
Develop a reliable, interpretable, and reproducible machine learning regression pipeline to predict future groundwater levels (`Water Level, m bgl` – metres below ground level) across monitoring wells in Maharashtra.

**Key Hydrological Definition:**
* **`m bgl` (Metres Below Ground Level)**: Measures the distance from the ground surface down to the water table.
* **Larger positive value** = **Deeper water table** (depleted aquifer).
* **Lower value** = **Shallower water table** (recharged aquifer).
* **Negative value** = Artesian head (water level rising above surface datum).""")

# Section 1
add_md("""## 1. Setup & Environment
We import standard data science libraries. Preprocessing and models are encapsulated inside scikit-learn `Pipeline` objects to prevent data leakage.""")

add_code("""import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.impute import SimpleImputer
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

print("Environment loaded successfully!")""")

# Section 2
add_md("""## 2. Dataset Loading & Comprehensive Data Audit
We load the two official datasets assigned:
1. `ground_water_level_manual_quarterly_maharashtra_1970_2025.csv`: Primary historical groundwater records (1970–2025).
2. `rainfall_manual_daily_maharashtra_sw_mh_2021_2025.csv`: Recent daily station rainfall (2021–2025).

*Note: The 1961–1990 historical rainfall file is strictly excluded as instructed.*""")

add_code("""gw_file = "../../ground_water_level_manual_quarterly_maharashtra_1970_2025.csv"
rf_file = "../../rainfall_manual_daily_maharashtra_sw_mh_2021_2025.csv"

# Load groundwater dataset with latin1 encoding to handle special characters
df_gw_raw = pd.read_csv(gw_file, encoding='latin1', low_memory=False)
df_gw_raw.columns = [c.strip() for c in df_gw_raw.columns]

# Load rainfall dataset with utf-8 encoding
df_rf_raw = pd.read_csv(rf_file, encoding='utf-8', low_memory=False)
df_rf_raw.columns = [c.strip() for c in df_rf_raw.columns]

print(f"Raw Groundwater Shape: {df_gw_raw.shape[0]:,} rows x {df_gw_raw.shape[1]} columns")
print(f"Raw Rainfall Shape:    {df_rf_raw.shape[0]:,} rows x {df_rf_raw.shape[1]} columns")""")

# Section 3
add_md("""## 3. Data Cleaning, Exact Duplicate Removal & Conflict Auditing
### 3.1 Duplicate Accounting
- **Raw records**: 636,605
- **Exact duplicate rows**: 1,929
- **Unique physical records**: 634,676

### 3.2 Repeated Well-Date Groups Breakdown
Out of 583 repeated well-date groups (1,166 records):
1. **539 groups (1,078 records)** contain **conflicting numeric readings**. We investigate and preserve all of them in `conflicting_records_audit.csv`, isolating them from training to avoid contradictory labels.
2. **44 groups (88 records)** contain **one numeric reading and one NaN**. We strictly preserve all 44 valid observations.
3. **1,625 missing target values (NaN)** are excluded from supervised modeling.

**Final Cleaned Dataset**: Exactly **631,973 rows** ($634,676 - 1,078 - 1,625 = 631,973$).""")

add_code("""clean_gw_path = "../clean_data/cleaned_groundwater_level.csv"
df_gw_clean = pd.read_csv(clean_gw_path, low_memory=False)
df_gw_clean['Date'] = pd.to_datetime(df_gw_clean['Date'])

print(f"Cleaned Groundwater Dataset: {len(df_gw_clean):,} records")
print(f"Unique Monitoring Wells:    {df_gw_clean['Well ID'].nunique():,}")
print(f"Unique Districts:           {df_gw_clean['District Name'].nunique()}")
print(f"Date Coverage:              {df_gw_clean['Date'].min().strftime('%d-%b-%Y')} to {df_gw_clean['Date'].max().strftime('%d-%b-%Y')}")""")

# Section 4
add_md("""## 4. Statistical Summary & Hydrological Inferences
Descriptive statistics of the target variable `Water Level, m bgl` and seasonal groundwater table depth across Maharashtra.""")

add_code("""print("--- Target Variable Summary Statistics ('Water Level, m bgl') ---")
print(df_gw_clean['Water Level, m bgl'].describe())

def get_season(m):
    if m in [3, 4, 5]: return 'Pre-Monsoon'
    elif m in [6, 7, 8, 9]: return 'Monsoon'
    elif m in [10, 11, 12]: return 'Post-Monsoon'
    else: return 'Winter'

df_gw_clean['Season'] = df_gw_clean['Date'].dt.month.apply(get_season)
season_summary = df_gw_clean.groupby('Season')['Water Level, m bgl'].agg(['count', 'mean', 'median', 'std', 'min', 'max'])
print("\\n--- Groundwater Depth by Hydrological Season (m bgl) ---")
print(season_summary)""")

# Section 5
add_md("""## 5. Visualizations & Hydrological Analysis
We display the 5 key publication visualizations generated for this project:
1. Long-Term Groundwater Trend (1970–2025).
2. Seasonal Water Table Distribution (Boxplots).
3. Probability Density Distribution of Water Table Depth.
4. Monthly Rainfall Time-Series (2021–2025).
5. Groundwater Depth vs. Antecedent 90-Day Precipitation.""")

add_code("""import matplotlib.image as mpimg

plot_files = [
    "../plots/01_groundwater_time_series_trend_1970_2025.png",
    "../plots/02_seasonal_groundwater_boxplot.png",
    "../plots/03_target_groundwater_distribution.png",
    "../plots/04_monthly_rainfall_timeseries_2021_2025.png",
    "../plots/05_groundwater_vs_prior_rainfall_scatter.png"
]

for p in plot_files:
    if os.path.exists(p):
        fig, ax = plt.subplots(figsize=(10, 5))
        img = mpimg.imread(p)
        ax.imshow(img)
        ax.axis('off')
        plt.show()""")

# Section 6
add_md("""## 6. Past-Only Feature Engineering & Preventing Data Leakage
To strictly prevent future-data leakage:
* `Lag_1`, `Lag_2`, `Lag_4`: Past measurements at periods $t-1$, $t-2$, and $t-4$ for that well.
* `Past_Rolling_Mean_3`, `Past_Rolling_Std_3`: Shifted rolling statistics over past 3 periods.
* `Month_Sin`, `Month_Cos`: Cyclical trigonometric features capturing the annual monsoon cycle.
* `Rain_Prior_30d`, `60d`, `90d`, `180d`: Antecedent cumulative precipitation strictly preceding the monitoring date.

### Two Separate Experiments:
* **Experiment A**: Groundwater-only model (**627,415 rows**, 1973–2025).
* **Experiment B**: Groundwater + rainfall overlap model (**65,738 rows**, 2021–2025).""")

add_code("""df_exp_a = pd.read_csv("../clean_data/experiment_A_groundwater_only.csv", low_memory=False)
df_exp_b = pd.read_csv("../clean_data/experiment_B_groundwater_rainfall.csv", low_memory=False)

print(f"Experiment A Dataset: {len(df_exp_a):,} rows | Cols: {df_exp_a.shape[1]}")
print(f"Experiment B Dataset: {len(df_exp_b):,} rows  | Cols: {df_exp_b.shape[1]}")""")

# Section 7
add_md("""## 7. Model Training & Evaluation: Experiment A (Groundwater-Only)
We benchmark all 10 candidate models on Experiment A:
* **Chronological Split Date**: `2022-01-01`
* **Training Period**: 1973 to 31-Dec-2021 (**567,137 rows**, strictly historical)
* **Untouched Test Period**: 01-Jan-2022 to 16-Oct-2025 (**60,278 rows**, strictly future)
* **Validation**: 5-Fold Expanding-Window `TimeSeriesSplit` on training data.
* **Selection Decision**: **XGBoost Regressor** selected as the winner on both CV (CV RMSE: 1.8840 m, CV $R^2$: 0.8284) and test set (Test RMSE: 1.5729 m, Test $R^2$: 0.8508).""")

add_code("""comp_a = pd.read_csv("../models/experiment_a_groundwater_only_comparison.csv")
print("=== EXPERIMENT A MODEL COMPARISON TABLE ===")
print(comp_a.to_string(index=False))""")

# Section 8
add_md("""## 8. Model Training & Evaluation: Experiment B (Groundwater + Rainfall Overlap)
We benchmark all candidate models on Experiment B using strictly isolated preprocessing pipelines:
* **Chronological Split Date**: `2024-01-01`
* **Training Period**: 15-Feb-2021 to 31-Dec-2023 (**40,484 rows**)
* **Untouched Test Period**: 01-Jan-2024 to 18-Jun-2025 (**25,254 rows**, strictly untouched during model selection)
* **Validation**: 5-Fold Expanding-Window `TimeSeriesSplit` on training data.

### Strict Methodological Model Selection Rule:
Model selection across algorithms was decided **strictly on the basis of training-set cross-validation evidence**:
* **Primary Winner on Complete CV Evidence**: **7. KNN Regressor (k=7)**
  * **Lowest CV RMSE Mean**: **1.9066 m** (Std: 0.8294 m)
  * **Lowest CV MAE Mean**: **1.3630 m** (Std: 0.7011 m)
  * **Highest CV $R^2$ Mean**: **0.7110** (Std: 0.2847)
  * **Lowest Variance across Folds**: Most consistent generalization.
* **Final Untouched Test Evaluation**:
  * **KNN Regressor**: Test MAE: **1.3333 m**, Test RMSE: **1.9391 m**, Test $R^2$: **0.7743**
  * **XGBoost Regressor (Alternative)**: Test MAE: **1.2462 m**, Test RMSE: **1.8470 m**, Test $R^2$: **0.7953**
  * **Polynomial Ridge (Alternative)**: Test MAE: **1.2715 m**, Test RMSE: **1.8306 m**, Test $R^2$: **0.7989**""")

add_code("""folds_b = pd.read_csv("../models/experiment_b_detailed_cv_folds.csv")
print("=== EXPERIMENT B: DETAILED FOLD-BY-FOLD CV METRICS ===")
print(folds_b.to_string(index=False))

print("\\n=== EXPERIMENT B: CROSS-VALIDATION SUMMARY TABLE ===")
summary_b = folds_b.groupby('Model').agg(
    CV_RMSE_Mean=('RMSE', 'mean'),
    CV_RMSE_Std=('RMSE', 'std'),
    CV_MAE_Mean=('MAE', 'mean'),
    CV_MAE_Std=('MAE', 'std'),
    CV_R2_Mean=('R2', 'mean'),
    CV_R2_Std=('R2', 'std')
).reset_index().sort_values(by='CV_RMSE_Mean')
print(summary_b.to_string(index=False))""")

# Section 9
add_md("""## 9. Diagnostic Plots (Actual vs. Predicted and Residuals)
Diagnostic evaluation of the selected models for Experiment A (XGBoost) and Experiment B (KNN Regressor):""")

add_code("""fig, axes = plt.subplots(1, 2, figsize=(16, 6))

img_a = mpimg.imread("../plots/diagnostic_plots_experiment_a_groundwater_only.png")
axes[0].imshow(img_a)
axes[0].set_title("Experiment A Diagnostics (XGBoost Regressor)", fontsize=13, fontweight='bold')
axes[0].axis('off')

img_b = mpimg.imread("../plots/diagnostic_plots_experiment_b_groundwater_rainfall.png")
axes[1].imshow(img_b)
axes[1].set_title("Experiment B Diagnostics (KNN Regressor - Primary Winner on CV)", fontsize=13, fontweight='bold')
axes[1].axis('off')

plt.tight_layout()
plt.show()""")

# Section 10
add_md("""## 10. Pipeline Verification & Live Prediction Demonstration
We load the saved production pipelines and demonstrate live inference on sample input schemas.""")

add_code("""# Load saved pipeline for Experiment A (XGBoost)
pipeline_a_data = joblib.load("../models/best_model_experiment_a_groundwater_only.joblib")
pipe_a = pipeline_a_data['pipeline']

sample_a_df = pd.DataFrame([{
    'Lag_1': 4.2,
    'Lag_2': 5.1,
    'Lag_4': 4.0,
    'Past_Rolling_Mean_3': 4.8,
    'Past_Rolling_Std_3': 0.55,
    'Well Depth, m': 12.5,
    'Latitude': 18.52,
    'Longitude': 73.85,
    'Month_Sin': np.sin(2 * np.pi * 10 / 12),
    'Month_Cos': np.cos(2 * np.pi * 10 / 12),
    'Season': 'Post-Monsoon',
    'District Name': 'Pune'
}])

pred_a = pipe_a.predict(sample_a_df)[0]
print(f"Predicted Groundwater Level (Experiment A - XGBoost): {pred_a:.2f} m bgl")

# Load saved PRIMARY pipeline for Experiment B (KNN - Winner on CV)
pipeline_b_data = joblib.load("../models/best_model_experiment_b_groundwater_rainfall.joblib")
pipe_b = pipeline_b_data['pipeline']

sample_b_df = pd.DataFrame([{
    'Lag_1': 2.8,
    'Lag_2': 4.5,
    'Lag_4': 3.1,
    'Past_Rolling_Mean_3': 3.6,
    'Past_Rolling_Std_3': 0.85,
    'Rain_Prior_30d': 120.5,
    'Rain_Prior_60d': 260.0,
    'Rain_Prior_90d': 380.0,
    'Rain_Prior_180d': 450.0,
    'Well Depth, m': 10.0,
    'Latitude': 19.99,
    'Longitude': 73.78,
    'Month_Sin': np.sin(2 * np.pi * 10 / 12),
    'Month_Cos': np.cos(2 * np.pi * 10 / 12),
    'Season': 'Post-Monsoon',
    'District Name': 'Nashik'
}])

pred_b = pipe_b.predict(sample_b_df)[0]
print(f"Predicted Groundwater Level (Experiment B - KNN Regressor [Primary Winner on CV]): {pred_b:.2f} m bgl")

# Also demonstrate alternative models
pipe_b_xgb = joblib.load("../models/alternative_model_experiment_b_xgboost.joblib")['pipeline']
pred_b_xgb = pipe_b_xgb.predict(sample_b_df)[0]
print(f"Predicted Groundwater Level (Experiment B - XGBoost [Alternative]): {pred_b_xgb:.2f} m bgl")

pipe_b_poly = joblib.load("../models/alternative_model_experiment_b_polynomial_ridge.joblib")['pipeline']
pred_b_poly = pipe_b_poly.predict(sample_b_df)[0]
print(f"Predicted Groundwater Level (Experiment B - Polynomial Ridge [Alternative]): {pred_b_poly:.2f} m bgl")

print("\\nRegression Module Execution Complete & Verified!")""")

notebook_dict = {
    "cells": cells,
    "metadata": {
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(notebook_dict, f, indent=2)

print(f"Saved complete updated notebook to: {nb_path}")
