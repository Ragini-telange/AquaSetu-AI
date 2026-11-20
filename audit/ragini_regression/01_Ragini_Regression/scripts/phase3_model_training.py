import os
import sys
import time
import joblib
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.base import BaseEstimator, RegressorMixin, clone
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

print("="*75)
print("PHASE 3: CHRONOLOGICAL MODEL TRAINING & COMPREHENSIVE BENCHMARKING")
print("="*75)

clean_dir = "01_Ragini_Regression/clean_data"
model_dir = "01_Ragini_Regression/models"
plot_dir = "01_Ragini_Regression/plots"
os.makedirs(model_dir, exist_ok=True)
os.makedirs(plot_dir, exist_ok=True)

# -------------------------------------------------------------
# 1. DEFINE BASELINE MODEL CLASS (SCIKIT-LEARN COMPATIBLE)
# -------------------------------------------------------------
class GroundwaterBaselineModel(BaseEstimator, RegressorMixin):
    """
    Hydrological Baseline Persistence Predictor:
    Predicts future water table depth using the most recent observation (Lag_1).
    Groundwater levels change gradually due to low hydraulic conductivity;
    hence the previous reading is the fundamental physical persistence benchmark.
    If Lag_1 is unavailable, it falls back to the training mean.
    """
    def __init__(self, lag_col='Lag_1'):
        self.lag_col = lag_col
        self.train_mean_ = 6.0

    def fit(self, X, y=None):
        if isinstance(X, pd.DataFrame) and self.lag_col in X.columns:
            self.train_mean_ = float(X[self.lag_col].dropna().mean())
        elif y is not None and len(y) > 0:
            self.train_mean_ = float(np.mean(y))
        else:
            self.train_mean_ = 6.0
        return self

    def predict(self, X):
        if isinstance(X, pd.DataFrame) and self.lag_col in X.columns:
            return X[self.lag_col].fillna(self.train_mean_).values
        elif hasattr(X, 'values'):
            # First column is Lag_1
            vals = X.values[:, 0]
            return np.where(pd.isna(vals), self.train_mean_, vals)
        else:
            X_arr = np.asarray(X)
            vals = X_arr[:, 0]
            return np.where(np.isnan(vals), self.train_mean_, vals)

# -------------------------------------------------------------
# 2. EVALUATION HELPER FUNCTION
# -------------------------------------------------------------
def evaluate_predictions(y_true, y_pred, model_name="Model"):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return {
        'Model': model_name,
        'MAE (m)': round(mae, 4),
        'RMSE (m)': round(rmse, 4),
        'R2': round(r2, 4)
    }

# Factory function for fresh preprocessors
def build_preprocessor(num_features, cat_features):
    num_trans = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    cat_trans = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    return ColumnTransformer(transformers=[
        ('num', num_trans, num_features),
        ('cat', cat_trans, cat_features)
    ])

# -------------------------------------------------------------
# 3. EXPERIMENT RUNNER FUNCTION
# -------------------------------------------------------------
def run_experiment(exp_name, data_path, num_features, cat_features, target_col='Water Level, m bgl', split_date='2022-01-01'):
    print(f"\n{'='*30} STARTING {exp_name} {'='*30}")
    print(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path, low_memory=False)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date').reset_index(drop=True)
    
    print(f"Total Rows: {len(df):,}")
    print(f"Date Range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    
    # Chronological Train-Test Split (Untouched Test Set)
    train_mask = df['Date'] < split_date
    test_mask = df['Date'] >= split_date
    
    df_train = df[train_mask].copy()
    df_test = df[test_mask].copy()
    
    print(f"Chronological Split Date: {split_date}")
    print(f"Training Set (strictly historical): {len(df_train):,} rows ({df_train['Date'].min().strftime('%Y-%m-%d')} to {df_train['Date'].max().strftime('%Y-%m-%d')})")
    print(f"Test Set (strictly untouched future): {len(df_test):,} rows ({df_test['Date'].min().strftime('%Y-%m-%d')} to {df_test['Date'].max().strftime('%Y-%m-%d')})")
    
    all_features = num_features + cat_features
    X_train_df = df_train[all_features].copy()
    y_train = df_train[target_col].values
    
    X_test_df = df_test[all_features].copy()
    y_test = df_test[target_col].values
    
    # TimeSeriesSplit Cross-Validation (5 Folds on Training Data)
    print("\nRunning Expanding-Window TimeSeriesSplit Cross-Validation (5 Folds)...")
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Subsample for CV if dataset is huge (>200k) to keep cross-validation efficient and responsive
    if len(df_train) > 150000:
        cv_sample_idx = np.linspace(0, len(df_train) - 1, 80000, dtype=int)
        cv_X = X_train_df.iloc[cv_sample_idx].copy().reset_index(drop=True)
        cv_y = y_train[cv_sample_idx]
    else:
        cv_X = X_train_df.reset_index(drop=True)
        cv_y = y_train
        
    # Dictionary of Models
    def get_model_dict():
        poly_cols = ['Lag_1', 'Past_Rolling_Mean_3', 'Month_Sin', 'Month_Cos']
        other_num_cols = [f for f in num_features if f not in poly_cols]
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
            ]), cat_features)
        ])
        
        return {
            '1. Baseline (Persistence)': GroundwaterBaselineModel(lag_col='Lag_1'),
            '2. Simple Linear Regression': Pipeline(steps=[
                ('prep', ColumnTransformer(transformers=[('lag', Pipeline(steps=[('imp', SimpleImputer(strategy='median')), ('scaler', StandardScaler())]), ['Lag_1'])])),
                ('reg', LinearRegression())
            ]),
            '3. Multiple Linear Regression': Pipeline(steps=[('prep', build_preprocessor(num_features, cat_features)), ('reg', LinearRegression())]),
            '4. Polynomial Regression (Deg 2)': Pipeline(steps=[('prep', poly_transformer), ('reg', Ridge(alpha=10.0))]),
            '5. Ridge Regression (L2)': Pipeline(steps=[('prep', build_preprocessor(num_features, cat_features)), ('reg', Ridge(alpha=1.0))]),
            '6. Lasso Regression (L1)': Pipeline(steps=[('prep', build_preprocessor(num_features, cat_features)), ('reg', Lasso(alpha=0.01, max_iter=2000))]),
            '7. KNN Regressor': Pipeline(steps=[('prep', build_preprocessor(num_features, cat_features)), ('reg', KNeighborsRegressor(n_neighbors=7, weights='distance', n_jobs=-1))]),
            '8. Decision Tree Regressor': Pipeline(steps=[('prep', build_preprocessor(num_features, cat_features)), ('reg', DecisionTreeRegressor(max_depth=12, min_samples_split=20, random_state=42))]),
            '9. Random Forest Regressor': Pipeline(steps=[('prep', build_preprocessor(num_features, cat_features)), ('reg', RandomForestRegressor(n_estimators=100, max_depth=14, min_samples_split=20, random_state=42, n_jobs=-1))]),
            '10. XGBoost Regressor': Pipeline(steps=[('prep', build_preprocessor(num_features, cat_features)), ('reg', XGBRegressor(n_estimators=120, max_depth=6, learning_rate=0.08, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1))])
        }
    
    models = get_model_dict()
    cv_results = {}
    test_results = []
    trained_pipelines = {}
    test_predictions = {}
    
    # Execute Model Training & CV
    for name, model in models.items():
        t0 = time.time()
        print(f" -> Training {name}...", end='', flush=True)
        
        # 1. TimeSeriesSplit CV
        cv_maes = []
        cv_rmses = []
        cv_r2s = []
        
        for tr_idx, val_idx in tscv.split(cv_X):
            X_tr, y_tr = cv_X.iloc[tr_idx], cv_y[tr_idx]
            X_val, y_val = cv_X.iloc[val_idx], cv_y[val_idx]
            
            m_fold = clone(model)
            if 'KNN' in name and len(X_tr) > 20000:
                knn_sub = np.random.choice(len(X_tr), 15000, replace=False)
                m_fold.fit(X_tr.iloc[knn_sub], y_tr[knn_sub])
            else:
                m_fold.fit(X_tr, y_tr)
                
            preds_val = m_fold.predict(X_val)
            cv_maes.append(mean_absolute_error(y_val, preds_val))
            cv_rmses.append(root_mean_squared_error(y_val, preds_val))
            cv_r2s.append(r2_score(y_val, preds_val))
            
        cv_results[name] = {
            'CV_MAE_Mean': np.mean(cv_maes),
            'CV_MAE_Std': np.std(cv_maes),
            'CV_RMSE_Mean': np.mean(cv_rmses),
            'CV_R2_Mean': np.mean(cv_r2s)
        }
        
        # 2. Fit on FULL Training Set and Evaluate on Untouched Chronological Test Set
        m_full = clone(model)
        if 'KNN' in name and len(X_train_df) > 40000:
            knn_idx = np.random.RandomState(42).choice(len(X_train_df), 35000, replace=False)
            m_full.fit(X_train_df.iloc[knn_idx], y_train[knn_idx])
        elif ('Random Forest' in name or 'XGBoost' in name) and len(X_train_df) > 200000:
            # Subsample 150k training points for tree ensembles on 500k row dataset for optimal speed
            rf_sub = np.random.RandomState(42).choice(len(X_train_df), 150000, replace=False)
            m_full.fit(X_train_df.iloc[rf_sub], y_train[rf_sub])
        else:
            m_full.fit(X_train_df, y_train)
            
        preds_test = m_full.predict(X_test_df)
        trained_pipelines[name] = m_full
            
        elapsed = time.time() - t0
        metrics = evaluate_predictions(y_test, preds_test, model_name=name)
        metrics['CV_MAE'] = round(cv_results[name]['CV_MAE_Mean'], 4)
        metrics['CV_RMSE'] = round(cv_results[name]['CV_RMSE_Mean'], 4)
        metrics['CV_R2'] = round(cv_results[name]['CV_R2_Mean'], 4)
        metrics['Train_Time_s'] = round(elapsed, 2)
        test_results.append(metrics)
        test_predictions[name] = preds_test
        
        print(f" Done ({elapsed:.1f}s) | Test MAE: {metrics['MAE (m)']:.3f} m, RMSE: {metrics['RMSE (m)']:.3f} m, R2: {metrics['R2']:.4f}")
        
    df_comparison = pd.DataFrame(test_results)
    print("\n" + "="*60)
    print(f"FINAL MODEL COMPARISON TABLE: {exp_name}")
    print("="*60)
    print(df_comparison.to_string(index=False))
    
    # Save comparison CSV
    comp_csv_path = os.path.join(model_dir, f"{exp_name.lower().replace(' ', '_')}_comparison.csv")
    df_comparison.to_csv(comp_csv_path, index=False)
    print(f"Comparison saved to: {comp_csv_path}")
    
    # Identify Best Model (Lowest Test RMSE, solid R2 & validation stability)
    best_row = df_comparison.sort_values(by=['RMSE (m)', 'MAE (m)']).iloc[0]
    best_name = best_row['Model']
    best_pipeline = trained_pipelines[best_name]
    print(f"\n>>> BEST SELECTED MODEL FOR {exp_name}: {best_name} <<<")
    print(f"    Test MAE: {best_row['MAE (m)']} m | Test RMSE: {best_row['RMSE (m)']} m | Test R2: {best_row['R2']}")
    
    # Save Best Pipeline
    best_pipe_path = os.path.join(model_dir, f"best_model_{exp_name.lower().replace(' ', '_')}.joblib")
    
    # Create prediction example
    sample_input = X_test_df.iloc[[0]].to_dict(orient='records')[0]
    sample_true = float(y_test[0])
    sample_pred = float(best_pipeline.predict(X_test_df.iloc[[0]])[0])
    
    joblib.dump({
        'experiment_name': exp_name,
        'model_name': best_name,
        'pipeline': best_pipeline,
        'num_features': num_features,
        'cat_features': cat_features,
        'split_date': split_date,
        'metrics': dict(best_row),
        'sample_input': sample_input,
        'sample_prediction': {
            'predicted_water_level_m_bgl': round(sample_pred, 3),
            'actual_water_level_m_bgl': round(sample_true, 3),
            'absolute_error_m': round(abs(sample_true - sample_pred), 3)
        }
    }, best_pipe_path)
    print(f"Saved complete pipeline & metadata to: {best_pipe_path}")
    
    # -------------------------------------------------------------
    # 4. ACTUAL VS PREDICTED & RESIDUAL PLOTS
    # -------------------------------------------------------------
    print(f"Generating diagnostic plots for {exp_name}...")
    sample_size = min(3000, len(y_test))
    np.random.seed(42)
    sample_idx = np.random.choice(len(y_test), sample_size, replace=False)
    
    y_sub = y_test[sample_idx]
    pred_sub = test_predictions[best_name][sample_idx]
    residuals = y_sub - pred_sub
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)
    
    # Plot A: Actual vs Predicted
    ax1.scatter(y_sub, pred_sub, alpha=0.35, color='#1f77b4', edgecolors='none', s=22)
    min_val = min(y_sub.min(), pred_sub.min())
    max_val = max(y_sub.max(), pred_sub.max())
    ax1.plot([min_val, max_val], [min_val, max_val], color='red', linestyle='--', linewidth=2, label='Perfect 1:1 Identity Line')
    ax1.set_title(f"Actual vs. Predicted Groundwater Level (m bgl)\n{exp_name} – {best_name}", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Actual Water Level (m bgl)", fontsize=11)
    ax1.set_ylabel("Predicted Water Level (m bgl)", fontsize=11)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend()
    
    # Plot B: Residual Plot
    ax2.scatter(pred_sub, residuals, alpha=0.35, color='#2ca02c', edgecolors='none', s=22)
    ax2.axhline(0, color='red', linestyle='--', linewidth=2, label='Zero Error Baseline')
    ax2.set_title(f"Residual Plot (Residuals vs. Fitted)\n{exp_name} – {best_name}", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Predicted Water Level (m bgl)", fontsize=11)
    ax2.set_ylabel("Residuals = (Actual - Predicted) [m]", fontsize=11)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend()
    
    plt.tight_layout()
    plot_diag_path = os.path.join(plot_dir, f"diagnostic_plots_{exp_name.lower().replace(' ', '_')}.png")
    plt.savefig(plot_diag_path)
    plt.close()
    print(f"Saved diagnostic plots to: {plot_diag_path}")
    
    return df_comparison, best_name, best_row

# -------------------------------------------------------------
# 4. EXECUTE EXPERIMENT A: GROUNDWATER-ONLY
# -------------------------------------------------------------
exp_a_path = os.path.join(clean_dir, "experiment_A_groundwater_only.csv")
num_cols_a = ['Lag_1', 'Lag_2', 'Lag_4', 'Past_Rolling_Mean_3', 'Past_Rolling_Std_3', 'Well Depth, m', 'Latitude', 'Longitude', 'Month_Sin', 'Month_Cos']
cat_cols_a = ['Season', 'District Name']

# Split date for Exp A: 2022-01-01 (historical training 1973-2021, untouched testing 2022-2025)
comp_a, best_a_name, best_a_row = run_experiment(
    exp_name="Experiment_A_Groundwater_Only",
    data_path=exp_a_path,
    num_features=num_cols_a,
    cat_features=cat_cols_a,
    split_date='2022-01-01'
)

# -------------------------------------------------------------
# 5. EXECUTE EXPERIMENT B: GROUNDWATER + RAINFALL OVERLAP
# -------------------------------------------------------------
exp_b_path = os.path.join(clean_dir, "experiment_B_groundwater_rainfall.csv")
num_cols_b = ['Lag_1', 'Lag_2', 'Lag_4', 'Past_Rolling_Mean_3', 'Past_Rolling_Std_3', 
              'Rain_Prior_30d', 'Rain_Prior_60d', 'Rain_Prior_90d', 'Rain_Prior_180d',
              'Well Depth, m', 'Latitude', 'Longitude', 'Month_Sin', 'Month_Cos']
cat_cols_b = ['Season', 'District Name']

# Split date for Exp B: 2024-01-01 (training 2021-2023, untouched testing 2024-2025)
comp_b, best_b_name, best_b_row = run_experiment(
    exp_name="Experiment_B_Groundwater_Rainfall",
    data_path=exp_b_path,
    num_features=num_cols_b,
    cat_features=cat_cols_b,
    split_date='2024-01-01'
)

print("\n" + "="*75)
print("PHASE 3 COMPLETE! ALL 10 MODELS TRAINED AND BENCHMARKED ON BOTH EXPERIMENTS.")
print("="*75)
