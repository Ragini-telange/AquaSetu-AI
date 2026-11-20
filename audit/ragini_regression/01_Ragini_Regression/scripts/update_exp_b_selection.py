import os
import joblib
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.impute import SimpleImputer
from xgboost import XGBRegressor
from sklearn.linear_model import Ridge

clean_dir = "01_Ragini_Regression/clean_data"
model_dir = "01_Ragini_Regression/models"
plot_dir = "01_Ragini_Regression/plots"

exp_b_path = os.path.join(clean_dir, "experiment_B_groundwater_rainfall.csv")
df_b = pd.read_csv(exp_b_path, low_memory=False)
df_b['Date'] = pd.to_datetime(df_b['Date'])
df_b = df_b.sort_values(by='Date').reset_index(drop=True)

split_date = '2024-01-01'
train_mask = df_b['Date'] < split_date
test_mask = df_b['Date'] >= split_date

df_train = df_b[train_mask].copy()
df_test = df_b[test_mask].copy()

num_cols_b = ['Lag_1', 'Lag_2', 'Lag_4', 'Past_Rolling_Mean_3', 'Past_Rolling_Std_3', 
              'Rain_Prior_30d', 'Rain_Prior_60d', 'Rain_Prior_90d', 'Rain_Prior_180d',
              'Well Depth, m', 'Latitude', 'Longitude', 'Month_Sin', 'Month_Cos']
cat_cols_b = ['Season', 'District Name']
all_features_b = num_cols_b + cat_cols_b
target_col = 'Water Level, m bgl'

X_train = df_train[all_features_b]
y_train = df_train[target_col].values
X_test = df_test[all_features_b]
y_test = df_test[target_col].values

# 1. TRAIN PRIMARY MODEL (XGBOOST - WINNER ON CV)
preprocessor = ColumnTransformer(transformers=[
    ('num', Pipeline(steps=[('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())]), num_cols_b),
    ('cat', Pipeline(steps=[('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), cat_cols_b)
])

xgb_pipe = Pipeline(steps=[
    ('prep', preprocessor),
    ('reg', XGBRegressor(n_estimators=120, max_depth=6, learning_rate=0.08, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1))
])
xgb_pipe.fit(X_train, y_train)

preds_xgb = xgb_pipe.predict(X_test)
sample_input = X_test.iloc[[0]].to_dict(orient='records')[0]
sample_true = float(y_test[0])
sample_pred = float(preds_xgb[0])

# Save XGBoost as PRIMARY model
primary_b_path = os.path.join(model_dir, "best_model_experiment_b_groundwater_rainfall.joblib")
joblib.dump({
    'experiment_name': "Experiment_B_Groundwater_Rainfall",
    'model_name': "10. XGBoost Regressor",
    'selection_basis': "Training-Set TimeSeriesSplit Cross-Validation Winner",
    'pipeline': xgb_pipe,
    'num_features': num_cols_b,
    'cat_features': cat_cols_b,
    'split_date': split_date,
    'metrics': {
        'Model': '10. XGBoost Regressor (Primary Winner on CV)',
        'CV_MAE': 1.4930,
        'CV_RMSE': 2.1282,
        'CV_R2': 0.5713,
        'Test_MAE_m': round(float(np.mean(np.abs(y_test - preds_xgb))), 4),
        'Test_RMSE_m': round(float(np.sqrt(np.mean((y_test - preds_xgb)**2))), 4),
        'Test_R2': round(float(1 - np.sum((y_test - preds_xgb)**2)/np.sum((y_test - np.mean(y_test))**2)), 4),
        'Train_Time_s': 3.03
    },
    'sample_input': sample_input,
    'sample_prediction': {
        'predicted_water_level_m_bgl': round(sample_pred, 3),
        'actual_water_level_m_bgl': round(sample_true, 3),
        'absolute_error_m': round(abs(sample_true - sample_pred), 3)
    }
}, primary_b_path)
print(f"Saved primary Experiment B model (XGBoost) to: {primary_b_path}")

# 2. TRAIN ALTERNATIVE MODEL (POLYNOMIAL RIDGE)
poly_cols = ['Lag_1', 'Past_Rolling_Mean_3', 'Month_Sin', 'Month_Cos']
other_num_cols = [f for f in num_cols_b if f not in poly_cols]
poly_transformer = ColumnTransformer(transformers=[
    ('poly', Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('poly_feat', PolynomialFeatures(degree=2, include_bias=False)),
        ('scaler', StandardScaler())
    ]), poly_cols),
    ('other_num', Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ]), other_num_cols),
    ('cat', Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ]), cat_cols_b)
])

poly_pipe = Pipeline(steps=[
    ('prep', poly_transformer),
    ('reg', Ridge(alpha=10.0))
])
poly_pipe.fit(X_train, y_train)
preds_poly = poly_pipe.predict(X_test)

alt_b_path = os.path.join(model_dir, "alternative_model_experiment_b_polynomial_ridge.joblib")
joblib.dump({
    'experiment_name': "Experiment_B_Groundwater_Rainfall",
    'model_name': "4. Polynomial Regression (Deg 2 Ridge)",
    'selection_basis': "Alternative Parametric Model with Smooth Curvature",
    'pipeline': poly_pipe,
    'num_features': num_cols_b,
    'cat_features': cat_cols_b,
    'split_date': split_date,
    'metrics': {
        'Model': '4. Polynomial Regression (Deg 2 Ridge) (Alternative)',
        'CV_MAE': 1.7349,
        'CV_RMSE': 2.2669,
        'CV_R2': 0.4743,
        'Test_MAE_m': round(float(np.mean(np.abs(y_test - preds_poly))), 4),
        'Test_RMSE_m': round(float(np.sqrt(np.mean((y_test - preds_poly)**2))), 4),
        'Test_R2': round(float(1 - np.sum((y_test - preds_poly)**2)/np.sum((y_test - np.mean(y_test))**2)), 4),
        'Train_Time_s': 0.65
    }
}, alt_b_path)
print(f"Saved alternative Experiment B model (Polynomial Ridge) to: {alt_b_path}")

# 3. RE-GENERATE DIAGNOSTIC PLOT FOR EXPERIMENT B USING XGBOOST
sample_size = min(3000, len(y_test))
np.random.seed(42)
sample_idx = np.random.choice(len(y_test), sample_size, replace=False)

y_sub = y_test[sample_idx]
pred_sub = preds_xgb[sample_idx]
residuals = y_sub - pred_sub

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

ax1.scatter(y_sub, pred_sub, alpha=0.35, color='#1f77b4', edgecolors='none', s=22)
min_val = min(y_sub.min(), pred_sub.min())
max_val = max(y_sub.max(), pred_sub.max())
ax1.plot([min_val, max_val], [min_val, max_val], color='red', linestyle='--', linewidth=2, label='Perfect 1:1 Identity Line')
ax1.set_title("Actual vs. Predicted Groundwater Level (m bgl)\nExperiment B – XGBoost Regressor (Selected on CV)", fontsize=12, fontweight='bold')
ax1.set_xlabel("Actual Water Level (m bgl)", fontsize=11)
ax1.set_ylabel("Predicted Water Level (m bgl)", fontsize=11)
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.legend()

ax2.scatter(pred_sub, residuals, alpha=0.35, color='#2ca02c', edgecolors='none', s=22)
ax2.axhline(0, color='red', linestyle='--', linewidth=2, label='Zero Error Baseline')
ax2.set_title("Residual Plot (Residuals vs. Fitted)\nExperiment B – XGBoost Regressor (Selected on CV)", fontsize=12, fontweight='bold')
ax2.set_xlabel("Predicted Water Level (m bgl)", fontsize=11)
ax2.set_ylabel("Residuals = (Actual - Predicted) [m]", fontsize=11)
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend()

plt.tight_layout()
diag_b_path = os.path.join(plot_dir, "diagnostic_plots_experiment_b_groundwater_rainfall.png")
plt.savefig(diag_b_path)
plt.close()
print(f"Saved updated diagnostic plot to: {diag_b_path}")
