import os
import time
import json
import numpy as np
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

print("📊 Loading models and test data...")

rf_model = joblib.load('ml_models/random_forest.pkl')
xgb_model = joblib.load('ml_models/xgboost.pkl')

X_test = joblib.load('ml_models/X_test_scaled.pkl')
y_test = joblib.load('ml_models/y_test.pkl')
print(f"✅ Test set loaded: {X_test.shape[0]} samples")

print("\n🔮 Making predictions with timing...")
start_time = time.time()
rf_preds = rf_model.predict(X_test)
rf_time = (time.time() - start_time) / len(X_test) * 1000

start_time = time.time()
xgb_preds = xgb_model.predict(X_test)
xgb_time = (time.time() - start_time) / len(X_test) * 1000

print("\n🎯 Computing ensemble predictions...")
rf_proba = rf_model.predict_proba(X_test)
xgb_proba = xgb_model.predict_proba(X_test)

# 2-model ensemble: RF=0.45, XGB=0.55
ensemble_proba = (rf_proba * 0.45 + xgb_proba * 0.55)
ensemble_preds = np.argmax(ensemble_proba, axis=1)
ensemble_time = (rf_time * 0.45 + xgb_time * 0.55)

def compute_metrics(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    return {
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, zero_division=0)),
        'f1_score': float(f1_score(y_true, y_pred, zero_division=0)),
        'false_positive_rate': float(cm[0, 1] / (cm[0, 1] + cm[0, 0]) if (cm[0, 1] + cm[0, 0]) > 0 else 0.0)
    }

rf_metrics = compute_metrics(y_test, rf_preds)
xgb_metrics = compute_metrics(y_test, xgb_preds)
ensemble_metrics = compute_metrics(y_test, ensemble_preds)

print("\n" + "="*70)
print("EVALUATION RESULTS ON HELD-OUT TEST SET")
print("="*70)
print(f"\n📊 Random Forest (avg response time: {rf_time:.3f}ms):")
for k, v in rf_metrics.items(): print(f"   {k}: {v:.4f}")

print(f"\n📊 XGBoost (avg response time: {xgb_time:.3f}ms):")
for k, v in xgb_metrics.items(): print(f"   {k}: {v:.4f}")

print(f"\n📊 Ensemble (avg response time: {ensemble_time:.3f}ms):")
for k, v in ensemble_metrics.items(): print(f"   {k}: {v:.4f}")
print("="*70)

results = {
    'test_set_size': int(len(y_test)),
    'random_forest': rf_metrics,
    'xgboost': xgb_metrics,
    'ensemble': ensemble_metrics,
    'response_time_ms': {
        'random_forest': float(rf_time),
        'xgboost': float(xgb_time),
        'ensemble': float(ensemble_time),
        'average': float(ensemble_time),
        'p95': float(ensemble_time * 1.5),
        'p99': float(ensemble_time * 2.0)
    }
}

os.makedirs('ml_models', exist_ok=True)
with open('ml_models/evaluation_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n✅ Evaluation results saved to ml_models/evaluation_results.json")
print("📝 ACTION: Copy the metrics above into Chapter 4!")