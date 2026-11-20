"""
AQUAGUARD AI – COMPLETE MACHINE LEARNING CLASSIFICATION PIPELINE
PART 2: Groundwater Resource Risk Classification & Water Quality Potability Classification

Author: Sakshi (Member 2)
Module: Groundwater Risk Classification & Water Quality Classification
Project: AI-Based Groundwater Level Prediction and Geographical Risk Assessment Using Machine Learning
"""

import sys
import io
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Scikit-Learn Imports
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    balanced_accuracy_score, roc_auc_score, confusion_matrix, classification_report
)

# XGBoost Import
from xgboost import XGBClassifier

# Set UTF-8 encoding for standard output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

# Set visual style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

# Ensure output directories exist
os.makedirs('models', exist_ok=True)
os.makedirs('reports/figures', exist_ok=True)

print("=" * 80)
print("AQUAGUARD AI – FULL MACHINE LEARNING CLASSIFICATION PIPELINE")
print("=" * 80)

# ==============================================================================
# MODULE 1: GROUNDWATER RESOURCE RISK CLASSIFICATION (CGWB MH 2025)
# ==============================================================================
print("\n" + "#" * 80)
print(">>> MODULE 1: GROUNDWATER RESOURCE RISK CLASSIFICATION (MAHARASHTRA DISTRICTS)")
print("#" * 80)

# Load data
df_res_raw = pd.read_csv('data/raw/mh_gw_2025.csv')
# Filter out non-district summary rows (Total rows)
df_res = df_res_raw[df_res_raw['Name of District'].notnull()].copy()
df_res = df_res[~df_res['Name of District'].astype(str).str.contains('Total', case=False, na=False)].reset_index(drop=True)

print(f"Loaded {len(df_res)} valid Maharashtra district records.")

# Target Variable Construction (CGWB Official Guidelines)
# Safe: Stage of GW extraction <= 70%
# Semi-Critical: 70% < Stage <= 90%
# Critical: 90% < Stage <= 100%
# Over-Exploited: Stage > 100%
stage_col = 'Stage of GW extraction (%)'
df_res['Risk_Label'] = df_res[stage_col].apply(
    lambda x: 'Semi-Critical' if x > 70.0 else 'Safe'
)
df_res['Target'] = (df_res['Risk_Label'] == 'Semi-Critical').astype(int)

class_dist = df_res['Risk_Label'].value_counts()
print(f"Target Distribution:\n{class_dist}")
print("Note: In 2025 CGWB Maharashtra assessment, 31 districts are 'Safe' and 5 are 'Semi-Critical'.")

# Feature Matrix X and Target y
# TARGET LEAKAGE PREVENTION: Drop 'Stage of GW extraction (%)', 'Name of District', 'Sr. No.', and target labels
drop_cols = ['Sr. No.', 'Name of District', stage_col, 'Risk_Label', 'Target']
feature_cols_res = [c for c in df_res.columns if c not in drop_cols]
X_res = df_res[feature_cols_res].copy()
y_res = df_res['Target'].copy()

# Ensure all features are numeric
for c in feature_cols_res:
    X_res[c] = pd.to_numeric(X_res[c], errors='coerce')

print(f"\nResource Feature Set ({len(feature_cols_res)} features):")
for idx, col in enumerate(feature_cols_res, 1):
    print(f"  {idx:02d}. {col}")

# Train / Test Split (Stratified 80/20)
X_train_res, X_test_res, y_train_res, y_test_res = train_test_split(
    X_res, y_res, test_size=0.20, random_state=42, stratify=y_res
)
print(f"\nTrain size: {len(X_train_res)} (Safe: {(y_train_res==0).sum()}, Semi-Critical: {(y_train_res==1).sum()})")
print(f"Test size:  {len(X_test_res)} (Safe: {(y_test_res==0).sum()}, Semi-Critical: {(y_test_res==1).sum()})")

# Define Models to Compare
models_res = {
    'Dummy Baseline': DummyClassifier(strategy='stratified', random_state=42),
    'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=3),
    'Decision Tree': DecisionTreeClassifier(max_depth=4, random_state=42),
    'Gaussian Naive Bayes': GaussianNB(),
    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=4, random_state=42, class_weight='balanced'),
    'XGBoost': XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42, eval_metric='logloss')
}

res_results = []
cv_strat_res = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for name, clf in models_res.items():
    pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('classifier', clf)
    ])
    
    # 5-Fold Stratified Cross-Validation
    scoring = ['accuracy', 'precision', 'recall', 'f1', 'balanced_accuracy']
    cv_out = cross_validate(pipe, X_train_res, y_train_res, cv=cv_strat_res, scoring=scoring, error_score=0)
    
    # Fit on full train set and evaluate on test set
    pipe.fit(X_train_res, y_train_res)
    y_pred = pipe.predict(X_test_res)
    
    acc = accuracy_score(y_test_res, y_pred)
    prec = precision_score(y_test_res, y_pred, zero_division=0)
    rec = recall_score(y_test_res, y_pred, zero_division=0)
    f1 = f1_score(y_test_res, y_pred, zero_division=0)
    bal_acc = balanced_accuracy_score(y_test_res, y_pred)
    
    res_results.append({
        'Model': name,
        'CV_Accuracy_Mean': cv_out['test_accuracy'].mean(),
        'CV_Accuracy_Std': cv_out['test_accuracy'].std(),
        'Test_Accuracy': acc,
        'Test_Precision': prec,
        'Test_Recall': rec,
        'Test_F1': f1,
        'Test_Balanced_Acc': bal_acc
    })

df_res_eval = pd.DataFrame(res_results)
print("\n--- GROUNDWATER RESOURCE MODEL COMPARISON TABLE ---")
print(df_res_eval.to_string(index=False))

# Hyperparameter Tuning for Best Resource Model (Random Forest)
print("\n>>> Hyperparameter Tuning for Resource Model (Random Forest)...")
rf_param_grid = {
    'classifier__n_estimators': [50, 100, 150],
    'classifier__max_depth': [2, 3, 4, None],
    'classifier__min_samples_split': [2, 4],
    'classifier__class_weight': ['balanced', None]
}
pipe_rf_res = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(random_state=42))
])
grid_rf_res = GridSearchCV(pipe_rf_res, rf_param_grid, cv=cv_strat_res, scoring='f1', n_jobs=-1)
grid_rf_res.fit(X_train_res, y_train_res)
print(f"Best RF Params: {grid_rf_res.best_params_}")
best_res_model = grid_rf_res.best_estimator_

# Final Test Evaluation of Best Resource Model
y_pred_best_res = best_res_model.predict(X_test_res)
print("\nBest Resource Model Test Report:")
print(classification_report(y_test_res, y_pred_best_res, target_names=['Safe', 'Semi-Critical'], zero_division=0))

# Save Resource Model
joblib.dump({
    'pipeline': best_res_model,
    'features': feature_cols_res,
    'target_mapping': {0: 'Safe', 1: 'Semi-Critical'},
    'cgwb_rules': "Safe: <=70%, Semi-Critical: 70-90%, Critical: 90-100%, Over-Exploited: >100%"
}, 'models/groundwater_risk_model.pkl')
print("[Saved] models/groundwater_risk_model.pkl")


# ==============================================================================
# MODULE 2: GROUNDWATER QUALITY CLASSIFICATION (BIS IS 10500:2012)
# ==============================================================================
print("\n" + "#" * 80)
print(">>> MODULE 2: GROUNDWATER QUALITY POTABILITY CLASSIFICATION (CGWB 1961-2025)")
print("#" * 80)

# Load data
df_q_raw = pd.read_csv('data/raw/gwq_chemical_parameter_manual_cgwb_an_1961_2025.csv')
print(f"Loaded {len(df_q_raw)} water quality records.")

# Clean & Prepare Core Chemical Parameters
# Standard hydrogeological relation: TDS ~ 0.64 * EC if direct TDS is missing
ec_col = 'Electric Conductivity (μS/cm)'
tds_col = 'Total Dissolved Solids (mg/L)'
ph_col = 'Potential of Hydrogen (pH)'
th_col = 'Total Hardness (mgCaCO3/L)'
ca_col = 'Calcium (mg/L)'
mg_col = 'Magnesium (mg/L)'
cl_col = 'Chloride (mg/L)'
so4_col = 'Sulphate (mg/L)'
fe_col = 'Iron(mg/L)'
bicarb_col = 'Bicarbonate (mg/L)'
na_col = 'Sodium (mg/L)'

df_q = df_q_raw.copy()
for col in [ec_col, tds_col, ph_col, th_col, ca_col, mg_col, cl_col, so4_col, fe_col, bicarb_col, na_col]:
    df_q[col] = pd.to_numeric(df_q[col], errors='coerce')

# Fill missing TDS from EC
df_q['TDS_Filled'] = df_q[tds_col].fillna(df_q[ec_col] * 0.64)

# Derive Target Variable using BIS IS 10500:2012 Drinking Water Specification
# 0 = Non-Potable (Exceeds acceptable limit), 1 = Potable (Safe drinking water)
is_non_potable = (
    (df_q[ph_col] < 6.5) | (df_q[ph_col] > 8.5) |
    (df_q['TDS_Filled'] > 500.0) |
    (df_q[th_col] > 200.0) |
    (df_q[ca_col] > 75.0) |
    (df_q[mg_col] > 30.0) |
    (df_q[cl_col] > 250.0) |
    (df_q[so4_col] > 200.0) |
    (df_q[fe_col] > 1.0)
)

df_q['Potability_Label'] = np.where(is_non_potable, 'Non-Potable', 'Potable')
df_q['Target'] = np.where(is_non_potable, 0, 1)

print("\nWater Quality Target Distribution (BIS IS 10500:2012):")
print(df_q['Potability_Label'].value_counts())
print(f"Potable (1): {(df_q['Target']==1).sum()} ({((df_q['Target']==1).mean()*100):.1f}%)")
print(f"Non-Potable (0): {(df_q['Target']==0).sum()} ({((df_q['Target']==0).mean()*100):.1f}%)")

# Feature selection for quality model
feature_cols_q = [
    ph_col, ec_col, 'TDS_Filled', th_col, ca_col, mg_col, cl_col, so4_col, fe_col, bicarb_col, na_col
]
X_q = df_q[feature_cols_q].copy()
y_q = df_q['Target'].copy()

# Rename feature columns for cleaner scikit-learn / XGBoost compatibility
feature_rename_map = {
    ph_col: 'pH',
    ec_col: 'Electrical_Conductivity',
    'TDS_Filled': 'TDS',
    th_col: 'Total_Hardness',
    ca_col: 'Calcium',
    mg_col: 'Magnesium',
    cl_col: 'Chloride',
    so4_col: 'Sulphate',
    fe_col: 'Iron',
    bicarb_col: 'Bicarbonate',
    na_col: 'Sodium'
}
X_q = X_q.rename(columns=feature_rename_map)
clean_features_q = list(feature_rename_map.values())

print(f"\nQuality Predictive Features ({len(clean_features_q)} features): {clean_features_q}")

# Train / Test Split (Stratified 80/20)
X_train_q, X_test_q, y_train_q, y_test_q = train_test_split(
    X_q, y_q, test_size=0.20, random_state=42, stratify=y_q
)
print(f"\nTrain size: {len(X_train_q)} (Potable: {(y_train_q==1).sum()}, Non-Potable: {(y_train_q==0).sum()})")
print(f"Test size:  {len(X_test_q)} (Potable: {(y_test_q==1).sum()}, Non-Potable: {(y_test_q==0).sum()})")

# Define Models to Compare
models_q = {
    'Dummy Baseline': DummyClassifier(strategy='stratified', random_state=42),
    'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5),
    'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
    'Gaussian Naive Bayes': GaussianNB(),
    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42),
    'XGBoost': XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42, eval_metric='logloss')
}

q_results = []
cv_strat_q = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

fitted_pipes_q = {}

for name, clf in models_q.items():
    pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('classifier', clf)
    ])
    
    scoring = ['accuracy', 'precision', 'recall', 'f1', 'balanced_accuracy']
    cv_out = cross_validate(pipe, X_train_q, y_train_q, cv=cv_strat_q, scoring=scoring)
    
    pipe.fit(X_train_q, y_train_q)
    fitted_pipes_q[name] = pipe
    y_pred = pipe.predict(X_test_q)
    
    acc = accuracy_score(y_test_q, y_pred)
    prec = precision_score(y_test_q, y_pred, zero_division=0)
    rec = recall_score(y_test_q, y_pred, zero_division=0)
    f1 = f1_score(y_test_q, y_pred, zero_division=0)
    bal_acc = balanced_accuracy_score(y_test_q, y_pred)
    
    # Non-potable recall (high risk detection)
    cm = confusion_matrix(y_test_q, y_pred)
    tn, fp, fn, tp = cm.ravel()
    rec_non_potable = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    q_results.append({
        'Model': name,
        'CV_Accuracy_Mean': cv_out['test_accuracy'].mean(),
        'CV_Accuracy_Std': cv_out['test_accuracy'].std(),
        'Test_Accuracy': acc,
        'Test_Precision': prec,
        'Test_Recall_Potable': rec,
        'Test_Recall_NonPotable': rec_non_potable,
        'Test_F1': f1,
        'Test_Balanced_Acc': bal_acc
    })

df_q_eval = pd.DataFrame(q_results)
print("\n--- WATER QUALITY MODEL COMPARISON TABLE ---")
print(df_q_eval.to_string(index=False))

# Hyperparameter Tuning for Random Forest & XGBoost
print("\n>>> Hyperparameter Tuning for Water Quality Models...")
xgb_param_grid = {
    'classifier__n_estimators': [50, 100, 150],
    'classifier__max_depth': [3, 4, 6],
    'classifier__learning_rate': [0.03, 0.1, 0.2],
    'classifier__subsample': [0.8, 1.0]
}
pipe_xgb_q = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('classifier', XGBClassifier(random_state=42, eval_metric='logloss'))
])
grid_xgb_q = GridSearchCV(pipe_xgb_q, xgb_param_grid, cv=cv_strat_q, scoring='accuracy', n_jobs=-1)
grid_xgb_q.fit(X_train_q, y_train_q)
print(f"Best XGBoost Params: {grid_xgb_q.best_params_}")
best_q_model = grid_xgb_q.best_estimator_

# Final Test Evaluation of Best Quality Model
y_pred_best_q = best_q_model.predict(X_test_q)
print("\nBest Water Quality Model Test Report:")
print(classification_report(y_test_q, y_pred_best_q, target_names=['Non-Potable', 'Potable'], digits=4))

# Save Water Quality Model Pipeline
joblib.dump({
    'pipeline': best_q_model,
    'features': clean_features_q,
    'target_mapping': {0: 'Non-Potable', 1: 'Potable'},
    'bis_standards': "BIS IS 10500:2012 Drinking Water Specification"
}, 'models/water_quality_model.pkl')
print("[Saved] models/water_quality_model.pkl")

# Save Combined Evaluation Results to CSV
df_q_eval.to_csv('reports/model_comparison.csv', index=False)
df_res_eval.to_csv('reports/evaluation_results.csv', index=False)
print("[Saved] reports/model_comparison.csv and reports/evaluation_results.csv")


# ==============================================================================
# FEATURE IMPORTANCE VISUALIZATION
# ==============================================================================
print("\n>>> Generating Feature Importance & Confusion Matrix Figures...")

# Extract Feature Importances from Tuned XGBoost Quality Model
xgb_clf = best_q_model.named_steps['classifier']
importances_q = xgb_clf.feature_importances_
feat_imp_df = pd.DataFrame({
    'Feature': clean_features_q,
    'Importance': importances_q
}).sort_values(by='Importance', ascending=True)

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Left Plot: Feature Importance Horizontal Bar Plot
axes[0].barh(feat_imp_df['Feature'], feat_imp_df['Importance'], color='#1f77b4', edgecolor='black', alpha=0.85)
axes[0].set_title('Water Quality Potability: Feature Importance (XGBoost)', fontsize=12, fontweight='bold', pad=12)
axes[0].set_xlabel('Relative Importance (Gain / Weight)', fontsize=11, labelpad=8)
axes[0].set_ylabel('Hydrochemical Features', fontsize=11, labelpad=8)
for i, v in enumerate(feat_imp_df['Importance']):
    axes[0].text(v + 0.005, i, f"{v:.3f}", va='center', fontsize=9, fontweight='bold')

# Right Plot: Test Set Confusion Matrix Heatmap
cm_q = confusion_matrix(y_test_q, y_pred_best_q)
sns.heatmap(cm_q, annot=True, fmt='d', cmap='Blues', cbar=False, ax=axes[1],
            xticklabels=['Non-Potable', 'Potable'], yticklabels=['Non-Potable', 'Potable'],
            annot_kws={'size': 14, 'weight': 'bold'})
axes[1].set_title('Test Set Confusion Matrix (Best Tuned XGBoost)', fontsize=12, fontweight='bold', pad=12)
axes[1].set_xlabel('Predicted Potability Class', fontsize=11, labelpad=8)
axes[1].set_ylabel('True BIS Ground Truth Class', fontsize=11, labelpad=8)

plt.tight_layout()
feat_imp_path = 'reports/figures/feature_importance.png'
plt.savefig(feat_imp_path, dpi=300)
plt.close()
print(f"[Saved] {feat_imp_path}")


# ==============================================================================
# GEOGRAPHICAL PREDICTION OUTPUTS FOR SAKSHI & TEAM INTEGRATION
# ==============================================================================
print("\n>>> Generating District & Station Risk Assessment Tables for Team...")

# Resource Assessment Predictions for all 36 Districts
df_res_preds = df_res[['Name of District', stage_col, 'Risk_Label']].copy()
df_res_preds['Predicted_Risk'] = best_res_model.predict(X_res)
df_res_preds['Predicted_Risk_Label'] = df_res_preds['Predicted_Risk'].map({0: 'Safe', 1: 'Semi-Critical'})
prob_res = best_res_model.predict_proba(X_res)[:, 1]
df_res_preds['Semi_Critical_Probability'] = np.round(prob_res, 4)
df_res_preds.to_csv('reports/district_groundwater_risk_predictions.csv', index=False)
print("[Saved] reports/district_groundwater_risk_predictions.csv")

# Quality Station Predictions
df_q_preds = df_q[['District', 'Station', 'Latitude', 'Longitude', 'Potability_Label']].copy()
df_q_preds['Predicted_Potable'] = best_q_model.predict(X_q)
df_q_preds['Predicted_Potability_Label'] = df_q_preds['Predicted_Potable'].map({0: 'Non-Potable', 1: 'Potable'})
prob_q = best_q_model.predict_proba(X_q)[:, 1]
df_q_preds['Potability_Probability'] = np.round(prob_q, 4)
df_q_preds.to_csv('reports/water_quality_station_predictions.csv', index=False)
print("[Saved] reports/water_quality_station_predictions.csv")

print("\n" + "=" * 80)
print("ALL CLASSIFICATION MODULE TASKS COMPLETED SUCCESSFULLY!")
print("=" * 80)
