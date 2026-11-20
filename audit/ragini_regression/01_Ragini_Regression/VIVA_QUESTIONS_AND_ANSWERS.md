# AquaGuard AI – Viva Questions and Answers
### Module: Groundwater Level Regression (Part 1)
**Student:** Ragini (Third-Year B.Tech Computer Engineering)  
**Topic:** Machine Learning for Groundwater Level Prediction in Maharashtra, India  

---

### Q1. What is the core problem and objective of your module?
**Answer:**  
In Maharashtra, groundwater depletion poses severe risks to agriculture and drinking water security. The objective of my module is to build and evaluate a machine learning regression pipeline that predicts future groundwater level (`Water Level, m bgl`) at monitoring wells across Maharashtra using historical groundwater measurements, past lag dynamics, seasonal features, and antecedent rainfall.

---

### Q2. What does the target unit `m bgl` mean? Why is a larger value not a higher water level?
**Answer:**  
* `m bgl` stands for **Metres Below Ground Level**. It measures the vertical depth from the land surface down to the water table.
* **Hydrological meaning:**
  * A **larger positive number** (e.g., $12.5\text{ m bgl}$) means the water table has dropped deeper into the ground, indicating **water scarcity / depletion**.
  * A **smaller number** (e.g., $2.5\text{ m bgl}$) means the water table is near the surface, indicating **recharge**.
  * A **negative number** (e.g., $-0.8\text{ m bgl}$) represents artesian pressure or water standing above the local surface datum.
* *Viva Tip:* Emphasize that in groundwater hydrology, depth and water volume are inversely related.

---

### Q3. Why did you conduct two separate experiments (Experiment A and Experiment B)?
**Answer:**  
* **Experiment A (Groundwater-Only Historical):** Covers the entire historical timeline from **1973 to October 2025** (**627,415 rows**). It models long-term autoregressive dynamics, seasonal oscillations, and spatial well characteristics across five decades.
* **Experiment B (Groundwater + Rainfall Overlap):** Covers only the period where daily rainfall data was actually available (**2021 to July 2025**, **65,738 rows**).
* **Why keep them separate?** The rainfall CSV only began in 2021. If we forced a single combined model on the entire dataset, we would have had to discard 50 years of groundwater records or fabricate rainfall from 1970–2020 by filling with zero (which would distort physical reality). Keeping them separate allows fair, scientifically sound modeling.

---

### Q4. How did you resolve the 1,929 duplicates and the 539 conflicting well-date groups?
**Answer:**  
* **1,929 Exact Duplicates:** Identical across all 14 columns. They were redundant multi-logged rows and were removed.
* **539 Conflicting Groups (1,078 records):** Occurred when two different water levels were recorded for the exact same well on the exact same date (mean discrepancy: $2.48\text{ m}$).
  * *Investigation:* We analyzed well depths and found 115 records matched well depth (dry well markers) and 8 records exceeded well depth.
  * *Decision:* We did not average them (averaging creates synthetic, fabricated numbers that neither technician measured). We preserved all 1,078 records in [`conflicting_records_audit.csv`](clean_data/conflicting_records_audit.csv) and isolated them from ML training so as not to inject contradictory target labels into the loss function.
* **44 Pairs with [Numeric, NaN]:** We prioritized valid numeric observations over missing values, successfully recovering all 44 valid measurements.

---

### Q5. Why is a standard random `train_test_split` completely invalid for this project?
**Answer:**  
Random shuffling causes severe **temporal data leakage**. In time series, future observations are auto-correlated with past observations. If we randomly shuffle:
1. The model is trained on future data and tested on past data (predicting the past using the future).
2. The test performance appears unrealistically high in the lab, but the model fails completely when deployed in the real world to forecast genuine future quarters.
* **Our Solution:** We used strict **chronological splitting** (Train on historical data up to a cutoff date, and test on untouched subsequent dates).

---

### Q6. How does expanding-window `TimeSeriesSplit` work, and why is it preferred over K-Fold CV?
**Answer:**  
In standard K-Fold CV, random folds contain future observations in the training split.  
In **expanding-window `TimeSeriesSplit`**:
* **Fold 1:** Train on $[t_0 \dots t_1]$, validate on $[t_1 \dots t_2]$.
* **Fold 2:** Train on $[t_0 \dots t_2]$, validate on $[t_2 \dots t_3]$.
* **Fold 3:** Train on $[t_0 \dots t_3]$, validate on $[t_3 \dots t_4]$.
At every fold, the training window expands forward in time, and the validation set is **always chronologically in the future relative to the training set**. This faithfully mimics how the model operates in production without future leakage.

---

### Q7. What is the fundamental rule of Model Selection in machine learning?
**Answer:**  
**Model selection and hyperparameter tuning must be decided strictly on training-set cross-validation performance, NEVER on the test set.**  
The test set must remain completely unseen and untouched until the final model is selected. If an engineer uses test-set scores to choose which model wins, information from the test set leaks into the selection process, creating **selection bias / test-set overfitting**.

---

### Q8. Which 10 models were evaluated, and how do they differ?
**Answer:**  
1. **Baseline Model:** Predicts previous observation (`Lag_1`) or training mean (persistence benchmark).
2. **Simple Linear Regression:** Fits a straight line using only `Lag_1`.
3. **Multiple Linear Regression:** Fits an unregularized hyper-plane over all features.
4. **Polynomial Regression (Degree 2):** Adds quadratic interaction terms with Ridge penalty to capture non-linear curvature.
5. **Ridge Regression ($L_2$):** Penalizes sum of squared weights ($\sum w^2$), handling multicollinearity among lags.
6. **Lasso Regression ($L_1$):** Penalizes sum of absolute weights ($\sum |w|$), performing automatic feature sparsity.
7. **KNN Regressor:** Distance-weighted average of the $k=7$ nearest historical hydrological states.
8. **Decision Tree Regressor:** Non-linear recursive binary partitioning based on variance reduction.
9. **Random Forest Regressor:** Bagging ensemble of 100 de-correlated decision trees with feature subsampling.
10. **XGBoost Regressor:** Sequential gradient-boosted decision trees that iteratively minimize pseudo-residuals using second-order Taylor expansion.

---

### Q9. What do MAE, RMSE, and $R^2$ tell us in this domain?
**Answer:**  
* **MAE (Mean Absolute Error):** Average magnitude of errors in metres. E.g., MAE = $1.08\text{ m}$ means predictions are on average within $1.08\text{ metres}$ of the true water table depth.
* **RMSE (Root Mean Squared Error):** Gives higher weight to large outliers because errors are squared before averaging. E.g., RMSE = $1.57\text{ m}$. A low RMSE indicates that the model avoids disastrous large forecasting errors during unpredicted droughts or cloudbursts.
* **$R^2$ (Coefficient of Determination):** The fraction of total groundwater variance explained by the model. E.g., $R^2 = 0.85$ means our features explain 85% of the variance across 4,500+ diverse wells.

---

### Q10. Why was XGBoost selected as the winner for Experiment A?
**Answer:**  
In Experiment A (567,137 training rows over 50 years):
* **Cross-Validation Winner:** XGBoost achieved the best CV metrics (CV RMSE: **$1.8840\text{ m}$**, CV $R^2$: **$0.8284$**).
* **Test Performance:** On the untouched 2022–2025 test set, it confirmed its dominance with a Test RMSE of **$1.5729\text{ m}$** and Test $R^2$ of **$0.8508$**.
* **Deployment Efficiency:** XGBoost trained in **$4.8\text{ seconds}$**, compared to Random Forest which took **$105.0\text{ seconds}$** (over 20 times faster!).

---

### Q11. Why did KNN Regressor win the primary selection in Experiment B over XGBoost and Polynomial Ridge?
**Answer:**  
When evaluating the full training-set cross-validation evidence across all 5 expanding chronological folds:
* **Decisive CV Metrics:**
  * **KNN Regressor ($k=7$)**: CV RMSE = **$1.9066\text{ m}$** ($\sigma = 0.8294$), CV MAE = **$1.3630\text{ m}$**, CV $R^2$ = **$0.7110$**.
  * **XGBoost Regressor**: CV RMSE = $2.1282\text{ m}$ ($\sigma = 1.3702$), CV MAE = $1.4930\text{ m}$, CV $R^2$ = $0.5714$.
  * **Polynomial Ridge**: CV RMSE = $2.2669\text{ m}$ ($\sigma = 1.6742$), CV MAE = $1.7349\text{ m}$, CV $R^2$ = $0.4743$.
* **Hydrological Reason for KNN's Victory:**  
  In Fold 1 (training on dry pre-monsoon and validating on sudden heavy southwest monsoon recharge), gradient boosted trees and polynomial models extrapolated into negative or exaggerated depths because they had never seen monsoonal rainfall in the training window. In contrast, **KNN is a distance-weighted neighborhood interpolator**: it is physically bounded within scaled feature space and cannot predict outside the range of observed hydrological soundings. This gave KNN superior stability ($\sigma = 0.83$ vs $1.37$ for XGBoost).
* **Role of Alternatives:** On the final untouched 2024–2025 test set (where full 2021–2023 history was present), XGBoost and Polynomial Ridge performed well (Test MAE 1.25m, Test RMSE 1.83m–1.85m), so they are preserved and documented as strong alternatives.

---

### Q12. How does rainfall matching work, and what is its main limitation?
**Answer:**  
* **Matching Methodology:** Daily rainfall from 658 stations was aggregated by district to produce daily district-average precipitation. For each groundwater observation on date $T$, antecedent cumulative rainfall was calculated for 30, 60, 90, and 180 days prior to $T$.
* **Limitation:** This is a **district-level spatial approximation**. Groundwater wells and rainfall gauges do not share identical latitude/longitude coordinates; a heavy localized shower in one corner of a large district may not recharge a monitoring well 40 kilometres away.

---

### Q13. How does your module integrate with Sakshi and Vedangi's work?
**Answer:**  
* **Handover to Sakshi (Classification Module):** My model predicts exact continuous water level in `m bgl`. Sakshi's classifier predicts categorical risk stages (Safe, Semi-Critical, Critical, Over-Exploited). Sakshi can use my numerical predictions as independent validation to verify whether her predicted risk categories align with physical water table depths.
* **Handover to Vedangi (Search Algorithms Module):** My pipeline outputs geo-referenced groundwater stress predictions. Wells with the deepest predicted water tables (highest risk of drying out) serve as high-priority goal nodes for Vedangi's graph search algorithms (BFS, DFS, Greedy, A*, IDDFS, Bidirectional Search) to compute optimal inspection routes from district monitoring offices.
