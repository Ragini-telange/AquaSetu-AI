import os
import sys
import time
import pandas as pd
import numpy as np

print("=" * 70)
print("AQUAGUARD SYSTEM AUDIT: AUTOMATED EXECUTION & VERIFICATION TEST")
print("=" * 70)

# -------------------------------------------------------------
# 1. RAGINI REGRESSION MODULE AUDIT TESTS
# -------------------------------------------------------------
print("\n[1/3] AUDITING RAGINI'S REGRESSION MODULE...")
import sklearn.compose._column_transformer as ct
class _RemainderColsList(list): pass
ct._RemainderColsList = _RemainderColsList

import joblib

reg_dir = r"D:\AquaGuard\audit\ragini_regression\01_Ragini_Regression\models"
models_to_test = [
    "best_model_experiment_a_groundwater_only.joblib",
    "best_model_experiment_b_groundwater_rainfall.joblib",
    "alternative_model_experiment_b_xgboost.joblib",
    "alternative_model_experiment_b_polynomial_ridge.joblib"
]

for mname in models_to_test:
    fpath = os.path.join(reg_dir, mname)
    if os.path.exists(fpath):
        t0 = time.time()
        artifact = joblib.load(fpath)
        t1 = time.time()
        print(f"  [PASS] {mname} loaded in {t1-t0:.2f}s | Model: {artifact.get('model_name')}")
    else:
        print(f"  [FAIL] Model file missing: {mname}")

# Test Prediction on KNN (Exp B Winner)
m_b = joblib.load(os.path.join(reg_dir, "best_model_experiment_b_groundwater_rainfall.joblib"))
pipe_b = m_b['pipeline']
sample_in_b = pd.DataFrame([{
    'Lag_1': 3.5,
    'Lag_2': 4.2,
    'Lag_4': 3.8,
    'Past_Rolling_Mean_3': 3.85,
    'Past_Rolling_Std_3': 0.35,
    'Rain_Prior_30d': 150.0,
    'Rain_Prior_60d': 320.0,
    'Rain_Prior_90d': 450.0,
    'Rain_Prior_180d': 500.0,
    'Well Depth, m': 12.0,
    'Latitude': 18.5204,
    'Longitude': 73.8567,
    'Month_Sin': np.sin(2 * np.pi * 10 / 12),
    'Month_Cos': np.cos(2 * np.pi * 10 / 12),
    'Season': 'Post-Monsoon',
    'District Name': 'Pune'
}])
pred_b = pipe_b.predict(sample_in_b)[0]
print(f"  [PASS] Experiment B KNN Live Prediction for Pune: {pred_b:.2f} m bgl")

# -------------------------------------------------------------
# 2. SAKSHI CLASSIFICATION MODULE AUDIT TESTS
# -------------------------------------------------------------
print("\n[2/3] AUDITING SAKSHI'S CLASSIFICATION MODULE...")
sakshi_dir = r"D:\AquaGuard\audit\sakshi_classification\project_aiml"
sys.path.append(os.path.join(sakshi_dir, "src"))

try:
    gw_risk_artifact = joblib.load(os.path.join(sakshi_dir, "models", "groundwater_risk_model.pkl"))
    print(f"  [PASS] groundwater_risk_model.pkl loaded | Features: {len(gw_risk_artifact['features'])}")
    if 'Sl. No' in gw_risk_artifact['features']:
        print("  [WARNING] 'Sl. No' detected in training feature set! This is an arbitrary index leak.")
except Exception as e:
    print(f"  [FAIL] Failed loading groundwater_risk_model.pkl: {e}")

try:
    wq_artifact = joblib.load(os.path.join(sakshi_dir, "models", "water_quality_model.pkl"))
    print(f"  [PASS] water_quality_model.pkl loaded | Features: {len(wq_artifact['features'])}")
except Exception as e:
    print(f"  [FAIL] Failed loading water_quality_model.pkl: {e}")

# Test Water Quality Potability Prediction
pipe_wq = wq_artifact['pipeline']
sample_chem_df = pd.DataFrame([{
    'pH': 7.2,
    'Electrical_Conductivity': 600.0,
    'TDS': 384.0,
    'Total_Hardness': 180.0,
    'Calcium': 50.0,
    'Magnesium': 25.0,
    'Chloride': 150.0,
    'Sulphate': 90.0,
    'Iron': 0.1,
    'Bicarbonate': 200.0,
    'Sodium': 45.0
}])
pred_wq = pipe_wq.predict(sample_chem_df)[0]
prob_wq = pipe_wq.predict_proba(sample_chem_df)[0]
print(f"  [PASS] Water Quality Potability Prediction: {'Potable' if pred_wq == 1 else 'Non-Potable'} (Prob: {prob_wq[1]:.2%})")

# -------------------------------------------------------------
# 3. VEDANGI GEOGRAPHICAL SEARCH MODULE AUDIT TESTS
# -------------------------------------------------------------
print("\n[3/3] AUDITING VEDANGI'S GEOGRAPHICAL SEARCH MODULE...")
vedangi_dir = r"D:\AquaGuard\audit\vedangi_geographical_search\AquaGuard_AI1\vedangi_search_module"
gw_loc_path = os.path.join(vedangi_dir, "processed_data", "groundwater_locations.csv")
snap_path = os.path.join(vedangi_dir, "processed_data", "pune_location_node_snap.csv")
graph_path = os.path.join(vedangi_dir, "pune_road_network.graphml")

if os.path.exists(gw_loc_path):
    df_loc = pd.read_csv(gw_loc_path)
    print(f"  [PASS] groundwater_locations.csv loaded: {len(df_loc)} locations across {df_loc['districts'].nunique()} districts")
else:
    print("  [FAIL] groundwater_locations.csv missing")

if os.path.exists(snap_path):
    df_snap = pd.read_csv(snap_path)
    print(f"  [PASS] pune_location_node_snap.csv loaded: {len(df_snap)} snapped nodes")
else:
    print("  [FAIL] pune_location_node_snap.csv missing")

print(f"  [INFO] Road network graph file size: {os.path.getsize(graph_path)/(1024*1024):.1f} MB")
print("=" * 70)
print("AUDIT EXECUTION TEST COMPLETED.")
print("=" * 70)
