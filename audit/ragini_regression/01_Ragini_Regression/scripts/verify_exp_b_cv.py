import os
import pandas as pd
import numpy as np
from sklearn.base import clone
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

clean_dir = "01_Ragini_Regression/clean_data"
exp_b_path = os.path.join(clean_dir, "experiment_B_groundwater_rainfall.csv")
df_b = pd.read_csv(exp_b_path, low_memory=False)
df_b['Date'] = pd.to_datetime(df_b['Date'])
df_b = df_b.sort_values(by='Date').reset_index(drop=True)

split_date = '2024-01-01'
train_mask = df_b['Date'] < split_date
test_mask = df_b['Date'] >= split_date

df_train = df_b[train_mask].copy().reset_index(drop=True)
df_test = df_b[test_mask].copy().reset_index(drop=True)

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

print(f"Experiment B Training Data: {len(X_train):,} rows ({df_train['Date'].min().strftime('%Y-%m-%d')} to {df_train['Date'].max().strftime('%Y-%m-%d')})")
print(f"Experiment B Test Data:     {len(X_test):,} rows ({df_test['Date'].min().strftime('%Y-%m-%d')} to {df_test['Date'].max().strftime('%Y-%m-%d')})")

def build_preprocessor():
    return ColumnTransformer(transformers=[
        ('num', Pipeline(steps=[('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())]), num_cols_b),
        ('cat', Pipeline(steps=[('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), cat_cols_b)
    ])

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

# Define the models
models_to_check = {
    'KNN Regressor (k=7)': Pipeline(steps=[
        ('prep', build_preprocessor()),
        ('reg', KNeighborsRegressor(n_neighbors=7, weights='distance', n_jobs=-1))
    ]),
    'XGBoost Regressor': Pipeline(steps=[
        ('prep', build_preprocessor()),
        ('reg', XGBRegressor(n_estimators=120, max_depth=6, learning_rate=0.08, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1))
    ]),
    'Polynomial Regression (Deg 2 Ridge)': Pipeline(steps=[
        ('prep', poly_transformer),
        ('reg', Ridge(alpha=10.0))
    ]),
    'Random Forest Regressor': Pipeline(steps=[
        ('prep', build_preprocessor()),
        ('reg', RandomForestRegressor(n_estimators=100, max_depth=14, min_samples_split=20, random_state=42, n_jobs=-1))
    ]),
    'Ridge Regression (L2)': Pipeline(steps=[
        ('prep', build_preprocessor()),
        ('reg', Ridge(alpha=1.0))
    ]),
    'Lasso Regression (L1)': Pipeline(steps=[
        ('prep', build_preprocessor()),
        ('reg', Lasso(alpha=0.01, max_iter=2000))
    ])
}

tscv = TimeSeriesSplit(n_splits=5)

# Detailed fold-by-fold results
cv_detailed_records = []

for name, model in models_to_check.items():
    print(f"\nEvaluating {name} fold-by-fold...")
    fold = 1
    fold_rmses = []
    fold_maes = []
    fold_r2s = []
    
    for tr_idx, val_idx in tscv.split(X_train):
        X_tr, y_tr = X_train.iloc[tr_idx], y_train[tr_idx]
        X_val, y_val = X_train.iloc[val_idx], y_train[val_idx]
        
        # Clone model: creates a completely fresh, unfitted pipeline with its own preprocessor
        m_fold = clone(model)
        m_fold.fit(X_tr, y_tr)
        preds_val = m_fold.predict(X_val)
        
        mae = mean_absolute_error(y_val, preds_val)
        rmse = root_mean_squared_error(y_val, preds_val)
        r2 = r2_score(y_val, preds_val)
        
        fold_rmses.append(rmse)
        fold_maes.append(mae)
        fold_r2s.append(r2)
        
        cv_detailed_records.append({
            'Model': name,
            'Fold': fold,
            'Train_Size': len(tr_idx),
            'Val_Size': len(val_idx),
            'Val_Start_Date': df_train.iloc[val_idx]['Date'].min().strftime('%Y-%m-%d'),
            'Val_End_Date': df_train.iloc[val_idx]['Date'].max().strftime('%Y-%m-%d'),
            'MAE': round(mae, 4),
            'RMSE': round(rmse, 4),
            'R2': round(r2, 4)
        })
        print(f"  Fold {fold} (Train: {len(tr_idx):,}, Val: {len(val_idx):,} from {df_train.iloc[val_idx]['Date'].min().strftime('%Y-%m-%d')} to {df_train.iloc[val_idx]['Date'].max().strftime('%Y-%m-%d')}): MAE={mae:.4f}, RMSE={rmse:.4f}, R2={r2:.4f}")
        fold += 1
        
    print(f" -> MEAN: RMSE={np.mean(fold_rmses):.4f} (+/- {np.std(fold_rmses):.4f}), MAE={np.mean(fold_maes):.4f} (+/- {np.std(fold_maes):.4f}), R2={np.mean(fold_r2s):.4f}")

df_folds = pd.DataFrame(cv_detailed_records)
df_folds.to_csv("01_Ragini_Regression/models/experiment_b_detailed_cv_folds.csv", index=False)
print("\nFold details saved to: 01_Ragini_Regression/models/experiment_b_detailed_cv_folds.csv")

# Print Summary Table
print("\n" + "="*80)
print("EXPERIMENT B: CROSS-VALIDATION SUMMARY TABLE (ORDERED BY CV RMSE)")
print("="*80)
summary = df_folds.groupby('Model').agg(
    CV_RMSE_Mean=('RMSE', 'mean'),
    CV_RMSE_Std=('RMSE', 'std'),
    CV_MAE_Mean=('MAE', 'mean'),
    CV_MAE_Std=('MAE', 'std'),
    CV_R2_Mean=('R2', 'mean'),
    CV_R2_Std=('R2', 'std')
).reset_index().sort_values(by='CV_RMSE_Mean')

print(summary.to_string(index=False))
