# LOCATION: backend/common.py  (next to manage.py and ml_models/)
"""Shared loader. Run the tools from the backend folder (the one containing ml_models/)."""
import joblib
import numpy as np
from pathlib import Path

MODEL_DIR = Path("ml_models")
RF_WEIGHT, XGB_WEIGHT = 0.45, 0.55       # same weights as evaluate_models.py / services.py


def load_models():
    rf = joblib.load(MODEL_DIR / "random_forest.pkl")
    xgb = joblib.load(MODEL_DIR / "xgboost.pkl")
    return rf, xgb


def ensemble_proba(rf, xgb, X):
    return RF_WEIGHT * rf.predict_proba(X) + XGB_WEIGHT * xgb.predict_proba(X)


def load_test():
    return joblib.load(MODEL_DIR / "X_test_scaled.pkl"), joblib.load(MODEL_DIR / "y_test.pkl")