"""
Phase 0 — Hands-on practice script.

This walks through the exact workflow you'll use for real in Phase 2,
but on a small SYNTHETIC dataset that mimics MSME alternate-data features.
Run it top to bottom, then go back and change things — that's how this
actually sticks. This can also be opened as a notebook in VS Code /
Jupyter using the "# %%" cell markers below.

Run with:  python 00_phase0_python_basics.py
"""

# %% 1. Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix

# %% 2. Generate a synthetic MSME-style dataset
# In Phase 1 you'll design this properly based on real report patterns.
# For now, this just gives you real data-shaped data to practice on.
np.random.seed(42)
n = 800

gst_filing_regularity = np.random.beta(5, 2, n)          # 0-1, higher = more regular
upi_txn_volume = np.random.lognormal(mean=9, sigma=1, size=n)  # monthly INR volume
upi_txn_volatility = np.random.beta(2, 5, n)              # 0-1, higher = more volatile
epfo_consistency = np.random.beta(3, 3, n)                # 0-1
months_in_business = np.random.randint(3, 180, n)

# Simulate a "true" underlying risk relationship so the model has
# something real to learn (this is what makes it a useful practice set)
risk_score = (
    -3
    + (1 - gst_filing_regularity) * 4
    + upi_txn_volatility * 3
    - epfo_consistency * 2
    - np.log1p(months_in_business) * 0.3
    + np.random.normal(0, 0.5, n)
)
default_prob = 1 / (1 + np.exp(-risk_score))
defaulted = np.random.binomial(1, default_prob)

df = pd.DataFrame({
    "gst_filing_regularity": gst_filing_regularity,
    "upi_txn_volume": upi_txn_volume,
    "upi_txn_volatility": upi_txn_volatility,
    "epfo_consistency": epfo_consistency,
    "months_in_business": months_in_business,
    "defaulted": defaulted,
})

print("Dataset shape:", df.shape)
print("\nDefault rate:", df["defaulted"].mean().round(3), "  <-- notice this is low: class imbalance in action")

# %% 3. Basic EDA — always look at your data before modeling
print("\n--- describe() ---")
print(df.describe())

print("\n--- missing values ---")
print(df.isnull().sum())

df.hist(figsize=(10, 6))
plt.tight_layout()
plt.savefig("phase0_feature_distributions.png")
print("\nSaved feature distribution plots to phase0_feature_distributions.png")

# %% 4. Train/test split
X = df.drop(columns=["defaulted"])
y = df["defaulted"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")

# %% 5. Baseline model — Logistic Regression
log_reg = LogisticRegression(max_iter=1000, class_weight="balanced")
log_reg.fit(X_train, y_train)

log_reg_probs = log_reg.predict_proba(X_test)[:, 1]
log_reg_auc = roc_auc_score(y_test, log_reg_probs)
print(f"\nLogistic Regression AUC-ROC: {log_reg_auc:.3f}")

# %% 6. Stronger model — Random Forest
rf = RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42)
rf.fit(X_train, y_train)

rf_probs = rf.predict_proba(X_test)[:, 1]
rf_auc = roc_auc_score(y_test, rf_probs)
print(f"Random Forest AUC-ROC: {rf_auc:.3f}")

# %% 7. A closer look at Random Forest performance
rf_preds = rf.predict(X_test)
print("\n--- Classification report (Random Forest) ---")
print(classification_report(y_test, rf_preds))

print("--- Confusion matrix ---")
print(confusion_matrix(y_test, rf_preds))

# %% 8. Feature importance — an early taste of "explainability"
importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\n--- Feature importances (Random Forest) ---")
print(importances)

# %% 9. Next steps (for you, not the computer)
# - Try changing class_weight, n_estimators, or the synthetic data's noise level
#   and see how AUC-ROC moves. Build intuition for what helps and what doesn't.
# - Once comfortable, move to Phase 1: replace this synthetic generator with
#   a more carefully designed dataset based on real RBI/SIDBI report patterns.
# - Later (Phase 3), swap feature_importances_ for SHAP values — same idea,
#   much more rigorous and per-prediction explainable.
