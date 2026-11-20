# AquaGuard AI – Groundwater Level Regression Module

**Project Title:** AquaGuard AI – AI-Based Groundwater Level Prediction and Geographical Risk Assessment Using Machine Learning  
**Geographic Focus:** Maharashtra, India  
**Author:** Ragini (Third-Year B.Tech Computer Engineering)  
**Module:** Part 1 – Regression (Groundwater Level Forecasting)  
**Collaborators:** Sakshi (Part 2 – Classification), Vedangi (Part 3 – Search Algorithms)  

---

## 1. Module Ownership & Boundaries
As defined in the project specification (AquaGuard AI Work Guides):
* **Ragini (Me)**: Solely responsible for the **Regression Module** (predicting numerical future groundwater level in `m bgl`, comparing 10 regression models, cross-validation, evaluation, and exporting the trained prediction pipeline).
* **Sakshi**: Responsible for the **Classification Module** (groundwater risk categorization).
* **Vedangi**: Responsible for the **Search Algorithms Module** (graph routing between monitoring stations).

---

## 2. Target Variable & Unit Definition
* **Target Column:** `Water Level, m bgl`
* **Unit:** **Metres Below Ground Level (m bgl)**
* **Hydrological Interpretation:**
  * `m bgl` measures the vertical distance from the ground surface down to the water table.
  * **Larger positive value** = **Deeper water table** (water is depleted / farther from surface).
  * **Smaller positive value** = **Shallower water table** (water is recharged / closer to surface).
  * **Zero (`0.0 m bgl`)** = Water table is exactly at the ground surface.
  * **Negative value (`< 0 m bgl`)** = Artesian conditions (groundwater head rises above surface datum under confined pressure).

---

## 3. Datasets Used

| Dataset | File Name | Date Coverage | Dimensions | Primary Use |
| :--- | :--- | :--- | :--- | :--- |
| **Groundwater Levels** | `ground_water_level_manual_quarterly_maharashtra_1970_2025.csv` | 1970 – 2025 | 636,605 rows × 14 cols | Primary target & autoregressive features across 4,558 wells in 33 districts. |
| **Rainfall Data** | `rainfall_manual_daily_maharashtra_sw_mh_2021_2025.csv` | 2021 – Jul 2025 | 121,904 rows × 20 cols | Antecedent precipitation features across 658 stations in 33 districts. |

*Note: The historical 1961–1990 rainfall dataset was strictly excluded as instructed.*

---

## 4. Complete Data Cleaning & Row-Count Accounting

```
Raw Groundwater Records:                                  636,605
 - Exact Duplicate Rows (Identical across all 14 cols):   - 1,929
 = Unique Physical Records Remaining:                     634,676

Inside the 634,676 Unique Records:
 1. Non-Repeated Records (Unique Well-Date combinations): 633,510
    ├─ Valid numeric target (Water Level, m bgl):         631,929
    └─ Missing target (NaN):                                1,581

 2. Repeated Records (583 groups of 2 records each):        1,166
    ├─ 539 groups where BOTH records have numeric targets:  1,078  (Conflicting values)
    └─ 44 groups where ONE record is numeric & ONE is NaN:     88  (44 numeric + 44 NaN)

Final Cleaned Dataset Rows: 634,676 - 1,078 - 1,625 = 631,973
```

### Key Cleaning Decisions:
1. **539 Conflicting Groups (1,078 records)**: Both readings were preserved with audit notes in [`clean_data/conflicting_records_audit.csv`](clean_data/conflicting_records_audit.csv). They were isolated from the training set to prevent contradictory target values from degrading regression model convergence.
2. **44 Repeated Groups with [Numeric, NaN]**: All 44 valid numeric readings were strictly preserved by prioritizing valid measurements over missing values.
3. **Well Depth Validation**: 28,236 records (4.45%) where `Water Level == Well Depth` represent dry wells and were preserved. 122 records (0.019%) where `Water Level > Well Depth` were logged in [`clean_data/well_depth_exceedance_audit.csv`](clean_data/well_depth_exceedance_audit.csv).
4. **Negative & Zero Values**: 16 negative readings (-0.05 to -1.25 m bgl) and 171 zero readings were preserved as genuine hydrological events (artesian pressure and surface saturation).
5. **Rainfall Standardization**: Standardized district names (mapped `AHMADNAGAR` to `AHMEDNAGAR`), achieving 32 common districts between datasets.

---

## 5. Feature Engineering (Strictly Past-Only)

All features were engineered to prevent future-data leakage:
* **Autoregressive Lags:** `Lag_1` ($t-1$), `Lag_2` ($t-2$), `Lag_4` ($t-4$ ~ 1 year prior).
* **Past Rolling Statistics:** `Past_Rolling_Mean_3`, `Past_Rolling_Std_3` (shifted by 1 period so current observation $t$ is strictly excluded).
* **Cyclical Time:** `Month_Sin`, `Month_Cos` ($\sin(2\pi \cdot m / 12)$, $\cos(2\pi \cdot m / 12)$).
* **Seasonality:** CGWB Hydrological Seasons (`Pre-Monsoon`, `Monsoon`, `Post-Monsoon`, `Winter`).
* **Antecedent Rainfall:** Preceding cumulative district precipitation strictly prior to date $T$: `Rain_Prior_30d`, `Rain_Prior_60d`, `Rain_Prior_90d`, `Rain_Prior_180d`.
* **Static Well Metadata:** `Well Depth, m`, `Latitude`, `Longitude`, `District Name`.

---

## 6. Two Separate Experiments

1. **Experiment A (Groundwater-Only Historical)**:
   * **Dataset:** 627,415 records spanning **1973 to October 2025**.
   * **Train Set:** 567,137 rows (1973–2021).
   * **Untouched Test Set:** 60,278 rows (2022–2025).
2. **Experiment B (Groundwater + Rainfall Overlap)**:
   * **Dataset:** 65,738 records spanning **2021 to July 2025**.
   * **Train Set:** 40,484 rows (2021–2023).
   * **Untouched Test Set:** 25,254 rows (2024–2025).

---

## 7. Model Comparison & Cross-Validation Results

Following rigorous machine learning methodology, **model selection was decided strictly on the basis of training-set cross-validation evidence**. The 2024–2025 test set was kept strictly untouched during model tuning and selection, serving solely as an out-of-sample benchmark.

### Experiment A: Groundwater-Only (1973–2025)
*Training-set TimeSeriesSplit CV (5 Folds) + Untouched Test (60,278 rows: 2022–2025)*

| Model Name | CV RMSE (m) | CV MAE (m) | CV $R^2$ | Test RMSE (m) | Test MAE (m) | Test $R^2$ | Train Time | Selection Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **10. XGBoost Regressor** | **1.8840** | **1.2669** | **0.8284** | **1.5729** | **1.0818** | **0.8508** | **4.8 s** | **Selected Winner (Best CV & Test)** |
| 9. Random Forest Regressor | 1.8903 | 1.2632 | 0.8271 | 1.5850 | 1.0716 | 0.8485 | 105.0 s | Close competitor (22x slower) |
| 4. Polynomial Reg (Deg 2) | 1.9945 | 1.4030 | 0.8076 | 1.7115 | 1.2189 | 0.8233 | 7.3 s | Non-linear parametric baseline |
| 7. KNN Regressor | 2.0523 | 1.4355 | 0.7965 | 1.7714 | 1.2531 | 0.8107 | 9.5 s | Non-parametric neighbor model |
| 3. Multiple Linear Regression | 2.0480 | 1.4519 | 0.7970 | 1.8097 | 1.3033 | 0.8025 | 10.6 s | Linear baseline |
| 5. Ridge Regression ($L_2$) | 2.0480 | 1.4519 | 0.7970 | 1.8097 | 1.3033 | 0.8025 | 5.4 s | Regularized linear baseline |
| 6. Lasso Regression ($L_1$) | 2.0652 | 1.4650 | 0.7935 | 1.8180 | 1.3095 | 0.8006 | 32.4 s | Sparse linear baseline |
| 8. Decision Tree Regressor | 2.1146 | 1.3994 | 0.7837 | 1.6508 | 1.1039 | 0.8356 | 31.6 s | Single tree baseline |
| 2. Simple Linear Regression | 3.1547 | 2.2935 | 0.5173 | 3.3057 | 2.4107 | 0.3409 | 0.5 s | Single feature (`Lag_1`) |
| 1. Baseline (Persistence) | 3.3816 | 2.3024 | 0.4443 | 3.6498 | 2.6546 | 0.1964 | 0.2 s | Persistence benchmark |

---

### Experiment B: Detailed Cross-Validation Audit (2021–2023 Training Set)
*Expanding-Window TimeSeriesSplit (5 Folds) with Preprocessing Pipelines Isolated per Fold*

#### Complete Cross-Validation Summary Table:
| Model Name | CV RMSE Mean (m) | CV RMSE Std | CV MAE Mean (m) | CV MAE Std | CV $R^2$ Mean | CV $R^2$ Std | Selection Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **7. KNN Regressor (k=7)** | **1.9066** | **0.8294** | **1.3630** | **0.7011** | **0.7110** | **0.2847** | **PRIMARY WINNER (Decisive CV Leader)** |
| 6. Lasso Regression ($L_1$) | 2.0447 | 1.0953 | 1.4720 | 0.7954 | 0.6401 | 0.4377 | Strong linear regularization |
| **10. XGBoost Regressor** | **2.1282** | **1.3702** | **1.4930** | **1.1556** | **0.5714** | **0.6033** | **DOCUMENTED ALTERNATIVE (Ensemble)** |
| 9. Random Forest Regressor | 2.1761 | 1.4627 | 1.5243 | 1.2355 | 0.5408 | 0.6683 | Bagging ensemble competitor |
| **4. Polynomial Reg (Deg 2 Ridge)** | **2.2669** | **1.6742** | **1.7349** | **1.5341** | **0.4743** | **0.8236** | **DOCUMENTED ALTERNATIVE (Parametric)** |
| 5. Ridge Regression ($L_2$) | 2.6331 | 2.2658 | 2.0204 | 1.9116 | 0.2061 | 1.3796 | High variance on Fold 1 |

#### Fold-by-Fold Performance Breakdown:
| Fold | Training Window | Validation Window | KNN RMSE | XGBoost RMSE | Poly Ridge RMSE | Fold Hydrological Context |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Fold 1** | Feb 2021 – May 2021 (6.7k rows) | Jun 2021 – Jan 2022 (6.7k rows) | **3.2628** | 4.5109 | 5.1982 | Early monsoon shock; parametric & tree models extrapolated; KNN remained bounded. |
| **Fold 2** | Feb 2021 – Jan 2022 (13.5k rows) | Feb 2022 – May 2022 (6.7k rows) | 1.4577 | **1.2347** | 1.3627 | Summer depletion period; all models stable. |
| **Fold 3** | Feb 2021 – May 2022 (20.2k rows) | Jun 2022 – Jan 2023 (6.7k rows) | 1.4438 | 1.7963 | **1.4275** | Monsoon recharge period; KNN and Poly Ridge accurate. |
| **Fold 4** | Feb 2021 – Jan 2023 (27.0k rows) | Feb 2023 – May 2023 (6.7k rows) | 1.2384 | **1.1933** | 1.2304 | Summer pre-monsoon; high precision across all models. |
| **Fold 5** | Feb 2021 – May 2023 (33.7k rows) | Jun 2023 – Dec 2023 (6.7k rows) | 2.1304 | **1.9057** | 2.1157 | Erratic monsoon recharge; XGBoost accurate. |

#### Untouched Test Set Evaluation (25,254 rows: 2024–2025):
* **KNN Regressor (Primary Winner)**: Test MAE = **$1.3333\text{ m}$**, Test RMSE = **$1.9391\text{ m}$**, Test $R^2$ = **$0.7743$**.
* **XGBoost Regressor (Alternative)**: Test MAE = **$1.2462\text{ m}$**, Test RMSE = **$1.8470\text{ m}$**, Test $R^2$ = **$0.7953$**.
* **Polynomial Ridge (Alternative)**: Test MAE = **$1.2715\text{ m}$**, Test RMSE = **$1.8306\text{ m}$**, Test $R^2$ = **$0.7989$**.

### Scientific Defense for Model Selection in Experiment B:
1. **Why KNN is Crowned Primary Winner**:  
   Across all 5 cross-validation folds, KNN is the **decisive leader on every single CV metric**: it has the lowest mean RMSE ($1.9066\text{ m}$), lowest MAE ($1.3630\text{ m}$), highest $R^2$ ($0.7110$), and lowest fold variance ($\sigma = 0.8294$).  
   *Hydrological explanation:* In expanding time series with sharp monsoon shifts, tree models and linear models extrapolate into unstable predictions when rainfall conditions shift between folds. KNN, being a distance-weighted neighborhood interpolator in scaled hydrological space, is physically bounded and cannot extrapolate outside the convex hull of known water levels.
2. **Why XGBoost and Polynomial Ridge are Retained as Alternatives**:  
   On the final 2024–2025 test set, once the entire 2021–2023 training history is available, XGBoost achieves the lowest MAE ($1.2462\text{ m}$) and Polynomial Ridge achieves the lowest RMSE ($1.8306\text{ m}$). Both pipelines are fully saved and available for comparison.

---

## 8. Saved Production Pipelines & Live Prediction

All models encapsulate full preprocessing (imputation, scaling, one-hot encoding) and the trained estimators:
* **Primary Model A (Groundwater-Only):** [`models/best_model_experiment_a_groundwater_only.joblib`](models/best_model_experiment_a_groundwater_only.joblib) (XGBoost)
* **Primary Model B (Groundwater + Rainfall):** [`models/best_model_experiment_b_groundwater_rainfall.joblib`](models/best_model_experiment_b_groundwater_rainfall.joblib) (KNN Regressor – Selected on CV)
* **Alternative Model B (XGBoost):** [`models/alternative_model_experiment_b_xgboost.joblib`](models/alternative_model_experiment_b_xgboost.joblib) (XGBoost)
* **Alternative Model B (Polynomial Ridge):** [`models/alternative_model_experiment_b_polynomial_ridge.joblib`](models/alternative_model_experiment_b_polynomial_ridge.joblib) (Polynomial Ridge)

### Python Live Prediction Code:
```python
import joblib
import pandas as pd
import numpy as np

# 1. Load Primary Production Pipeline for Experiment B (KNN Regressor)
model_data = joblib.load("models/best_model_experiment_b_groundwater_rainfall.joblib")
pipeline = model_data['pipeline']

# 2. Input features for a monitoring well in Nashik
input_df = pd.DataFrame([{
    'Lag_1': 2.80,              # Previous water level (m bgl)
    'Lag_2': 4.50,              # Water level 2 periods ago (m bgl)
    'Lag_4': 3.10,              # Water level ~1 year ago (m bgl)
    'Past_Rolling_Mean_3': 3.60,# Past 3-period rolling mean (m bgl)
    'Past_Rolling_Std_3': 0.85, # Past 3-period rolling std (m)
    'Rain_Prior_30d': 120.5,    # Prior 30-day cumulative rainfall (mm)
    'Rain_Prior_60d': 260.0,    # Prior 60-day cumulative rainfall (mm)
    'Rain_Prior_90d': 380.0,    # Prior 90-day cumulative rainfall (mm)
    'Rain_Prior_180d': 450.0,   # Prior 180-day cumulative rainfall (mm)
    'Well Depth, m': 10.0,      # Total drilled depth of well (m)
    'Latitude': 19.9975,        # Latitude (°N)
    'Longitude': 73.7898,       # Longitude (°E)
    'Month_Sin': np.sin(2 * np.pi * 10 / 12),  # October
    'Month_Cos': np.cos(2 * np.pi * 10 / 12),
    'Season': 'Post-Monsoon',   # Hydrological season
    'District Name': 'Nashik'   # District name
}])

# 3. Predict future groundwater level
prediction = pipeline.predict(input_df)[0]
print(f"Predicted Groundwater Level (KNN): {prediction:.2f} m bgl")
# Output: Predicted Groundwater Level (KNN): 2.76 m bgl
```

---

## 9. Integration Handover for Team Members

As specified in Page 8 of the AquaGuard AI Project Guide:
1. **Handover to Sakshi (Classification Module):**
   * Output provided: Well ID, Location coordinates (Latitude, Longitude), Date of prediction, and predicted numerical depth in `m bgl`.
   * Sakshi's classification model can use these continuous predictions to cross-check official groundwater development/risk stages (Safe, Semi-Critical, Critical, Over-Exploited).
2. **Handover to Vedangi (Search Algorithms Module):**
   * Output provided: Geo-referenced monitoring locations with predicted groundwater stress levels.
   * Vedangi's search graph can use stressed wells (deepest `m bgl`) as destination nodes (goals) for shortest-path inspection route planning from district GSDA headquarters.

---

## 10. Software Environment & Dependencies
* Python: `3.13`
* `scikit-learn`: `1.6.1`
* `pandas`: `2.2.3`
* `numpy`: `2.2.4`
* `xgboost`: `3.3.0`
* `matplotlib`: `3.10.1`
* `joblib`: `1.4.2`

---

## 11. Assumptions & Limitations
1. **District-Level Rainfall Approximation**: Daily rainfall is measured at rain stations and averaged to district-level antecedent totals because rainfall stations and groundwater wells do not share identical geographic coordinate pairs.
2. **Manual Monitoring Frequency**: Ground measurements are taken 4 times a year (quarterly). Sudden intra-quarter extreme weather events (e.g., a 2-day cloudburst) may take several weeks to reflect in deep unconfined aquifers.
3. **Pumping Data Absence**: Unrecorded local agricultural borehole pumping is not captured directly in the dataset; its effects are inferred indirectly via past water table lags.
