"""
AQUAGUARD AI – INFERENCE & PREDICTION MODULE
PART 2: Groundwater Risk & Water Quality Potability Prediction

Author: Sakshi (Member 2)
Module: Groundwater Risk Classification & Water Quality Classification
"""

import sys
import io
import joblib
import pandas as pd
import numpy as np

# Set UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load Trained Models
try:
    gw_risk_artifact = joblib.load('models/groundwater_risk_model.pkl')
    wq_artifact = joblib.load('models/water_quality_model.pkl')
    print("[SUCCESS] Loaded both trained classification models from models/")
except Exception as e:
    print(f"[ERROR] Failed to load models: {e}")
    sys.exit(1)


def predict_groundwater_resource_risk(district_data: dict) -> dict:
    """
    Predicts groundwater resource risk category (Safe vs Semi-Critical)
    from recharge and extraction parameters according to CGWB framework.
    """
    pipeline = gw_risk_artifact['pipeline']
    features = gw_risk_artifact['features']
    
    # Format input into single-row DataFrame
    df_input = pd.DataFrame([district_data])
    
    # Check for missing features and align columns
    for f in features:
        if f not in df_input.columns:
            df_input[f] = np.nan
            
    df_input = df_input[features]
    
    pred_idx = pipeline.predict(df_input)[0]
    probabilities = pipeline.predict_proba(df_input)[0]
    
    label = "Semi-Critical" if pred_idx == 1 else "Safe"
    risk_level = "MODERATE / ATTENTION REQUIRED" if pred_idx == 1 else "NORMAL / SUSTAINABLE"
    
    return {
        "status": "success",
        "predicted_category": label,
        "risk_level": risk_level,
        "probabilities": {
            "Safe": round(float(probabilities[0]), 4),
            "Semi-Critical": round(float(probabilities[1]), 4)
        },
        "advisory": (
            "Groundwater extraction is approaching critical recharge limits (70-90%). "
            "Implement mandatory rainwater harvesting and micro-irrigation."
            if pred_idx == 1 else
            "Groundwater levels are within safe sustainable limits (<=70% extraction)."
        )
    }


def predict_water_quality_potability(chemical_data: dict) -> dict:
    """
    Predicts water potability (Potable vs Non-Potable) from hydrochemical parameters
    based on Bureau of Indian Standards (BIS IS 10500:2012).
    """
    pipeline = wq_artifact['pipeline']
    features = wq_artifact['features']
    
    # Standard relation: if TDS is missing, estimate TDS = 0.64 * EC
    if 'TDS' not in chemical_data or pd.isna(chemical_data.get('TDS')):
        ec = chemical_data.get('Electrical_Conductivity', np.nan)
        if not pd.isna(ec):
            chemical_data['TDS'] = float(ec) * 0.64
            
    df_input = pd.DataFrame([chemical_data])
    
    for f in features:
        if f not in df_input.columns:
            df_input[f] = np.nan
            
    df_input = df_input[features]
    
    pred_idx = pipeline.predict(df_input)[0]
    probabilities = pipeline.predict_proba(df_input)[0]
    
    label = "Potable" if pred_idx == 1 else "Non-Potable"
    is_safe = (pred_idx == 1)
    
    # Check specific violations against BIS IS 10500:2012
    violations = []
    if chemical_data.get('pH', 7.0) < 6.5 or chemical_data.get('pH', 7.0) > 8.5:
        violations.append(f"pH ({chemical_data.get('pH')} outside 6.5 - 8.5 range)")
    if chemical_data.get('TDS', 0) > 500.0:
        violations.append(f"TDS ({chemical_data.get('TDS')} mg/L > 500 mg/L limit)")
    if chemical_data.get('Total_Hardness', 0) > 200.0:
        violations.append(f"Hardness ({chemical_data.get('Total_Hardness')} mg/L > 200 mg/L limit)")
    if chemical_data.get('Chloride', 0) > 250.0:
        violations.append(f"Chloride ({chemical_data.get('Chloride')} mg/L > 250 mg/L limit)")
    if chemical_data.get('Calcium', 0) > 75.0:
        violations.append(f"Calcium ({chemical_data.get('Calcium')} mg/L > 75 mg/L limit)")
    if chemical_data.get('Magnesium', 0) > 30.0:
        violations.append(f"Magnesium ({chemical_data.get('Magnesium')} mg/L > 30 mg/L limit)")
        
    return {
        "status": "success",
        "potability": label,
        "is_safe_for_drinking": is_safe,
        "probabilities": {
            "Non-Potable": round(float(probabilities[0]), 4),
            "Potable": round(float(probabilities[1]), 4)
        },
        "bis_violations": violations if violations else ["None (All parameters within BIS acceptable limits)"],
        "recommendation": (
            "Water is safe for human consumption as per BIS IS 10500:2012 standards."
            if is_safe else
            "Water is NOT POTABLE. Filtration, reverse osmosis (RO), or softening required before drinking."
        )
    }


# ==============================================================================
# SAMPLE TEST INVOCATION (DEMONSTRATION FOR VIVA)
# ==============================================================================
if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("DEMO TEST 1: PREDICTING GROUNDWATER RESOURCE RISK (Jalgaon District)")
    print("=" * 70)
    jalgaon_sample = {
        'Annual Extractable Groundwater Resource': 120531.0,
        'Irrigation - Annual extraction': 88000.0,
        'Industrial - Annual extraction': 450.0,
        'Domestic - Annual Extraction': 5600.0,
        'Total Annual Extraction': 94050.0,
        'Net GW availability for future': 26481.0,
        'Total annual groundwater recharge': 130000.0,
        'Total Natural Discharges': 9469.0
    }
    res_pred = predict_groundwater_resource_risk(jalgaon_sample)
    print(f"Prediction:     {res_pred['predicted_category']}")
    print(f"Risk Level:     {res_pred['risk_level']}")
    print(f"Probabilities:  {res_pred['probabilities']}")
    print(f"Advisory:       {res_pred['advisory']}")

    print("\n" + "=" * 70)
    print("DEMO TEST 2: PREDICTING WATER QUALITY POTABILITY (Sample A: High Salinity & Hardness)")
    print("=" * 70)
    unsafe_water_sample = {
        'pH': 8.2,
        'Electrical_Conductivity': 1450.0,
        'TDS': 928.0,
        'Total_Hardness': 340.0,
        'Calcium': 92.0,
        'Magnesium': 44.0,
        'Chloride': 310.0,
        'Sulphate': 180.0,
        'Iron': 0.15,
        'Bicarbonate': 280.0,
        'Sodium': 110.0
    }
    wq_pred1 = predict_water_quality_potability(unsafe_water_sample)
    print(f"Potability:     {wq_pred1['potability']}")
    print(f"Is Safe:        {wq_pred1['is_safe_for_drinking']}")
    print(f"Probabilities:  {wq_pred1['probabilities']}")
    print(f"Violations:     {wq_pred1['bis_violations']}")
    print(f"Recommendation: {wq_pred1['recommendation']}")

    print("\n" + "=" * 70)
    print("DEMO TEST 3: PREDICTING WATER QUALITY POTABILITY (Sample B: Clean Spring Water)")
    print("=" * 70)
    clean_water_sample = {
        'pH': 7.4,
        'Electrical_Conductivity': 320.0,
        'TDS': 204.8,
        'Total_Hardness': 120.0,
        'Calcium': 35.0,
        'Magnesium': 12.0,
        'Chloride': 28.0,
        'Sulphate': 22.0,
        'Iron': 0.05,
        'Bicarbonate': 140.0,
        'Sodium': 25.0
    }
    wq_pred2 = predict_water_quality_potability(clean_water_sample)
    print(f"Potability:     {wq_pred2['potability']}")
    print(f"Is Safe:        {wq_pred2['is_safe_for_drinking']}")
    print(f"Probabilities:  {wq_pred2['probabilities']}")
    print(f"Violations:     {wq_pred2['bis_violations']}")
    print(f"Recommendation: {wq_pred2['recommendation']}")
    print("=" * 70)
