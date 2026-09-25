"""
CIC-IDS2018 Memory-Safe Training Script
Only loads 100,000 rows from the start to avoid memory errors.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import shap
import joblib
import warnings
warnings.filterwarnings('ignore')

DATASET_DIR = Path("datasets/cicids2018")
MODEL_DIR = Path("models/cicids2018")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATASET_DIR / "cic.csv"

print("=" * 60)
print("📊 LOADING CIC-IDS2018 (100,000 rows only - memory safe)")
print("=" * 60)

# ✅ CRITICAL FIX: Only read 100,000 rows from the start
# This prevents loading the full 1M+ rows into memory
df = pd.read_csv(DATA_FILE, nrows=100000)
print(f"✅ Loaded shape: {df.shape}")

# Clean column names
df.columns = df.columns.str.strip().str.replace(' ', '_')

# Drop non-predictive columns
cols_to_drop = [col for col in ['Timestamp', 'Flow_ID', 'Source_IP', 'Destination_IP'] if col in df.columns]
if cols_to_drop:
    df = df.drop(columns=cols_to_drop)
    print(f"🗑️ Dropped: {cols_to_drop}")

# Identify label column
label_col = 'Label'
print(f"\n📊 Label distribution in sample:")
print(df[label_col].value_counts())

# Separate features and target
X = df.drop(columns=[label_col])
y = df[label_col]

# Only keep numeric columns (skip any string columns)
X = X.select_dtypes(include=[np.number])
print(f"\n📏 Numeric features: {X.shape[1]}")

# Handle missing/infinite values
X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

# Split data (80/20)
print("\n🔀 Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✅ Train: {X_train.shape}, Test: {X_test.shape}")

# Free memory
del df

# Scale features
print("📏 Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Encode labels
label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
y_test_encoded = label_encoder.transform(y_test)
print(f"✅ Classes: {label_encoder.classes_}")

# Save preprocessing artifacts
joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
joblib.dump(label_encoder, MODEL_DIR / "label_encoder.pkl")
joblib.dump(X.columns.tolist(), MODEL_DIR / "feature_names.pkl")
print("💾 Saved preprocessing artifacts")

# Train models
print("\n" + "=" * 60)
print("🤖 TRAINING MODELS")
print("=" * 60)

print("\n🌲 Training Random Forest...")
rf = RandomForestClassifier(
    n_estimators=100, max_depth=15, random_state=42, 
    n_jobs=-1, class_weight='balanced'
)
rf.fit(X_train_scaled, y_train_encoded)
print("✅ Random Forest trained")

print("\n⚡ Training XGBoost...")
xgb_model = xgb.XGBClassifier(
    n_estimators=100, max_depth=6, learning_rate=0.1, 
    random_state=42, n_jobs=-1
)
xgb_model.fit(X_train_scaled, y_train_encoded)
print("✅ XGBoost trained")

# Evaluate
print("\n" + "=" * 60)
print("📈 MODEL EVALUATION")
print("=" * 60)

def evaluate(model, name):
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test_encoded, y_pred)
    print(f"\n🎯 {name} Accuracy: {acc*100:.2f}%")
    print(classification_report(
        y_test_encoded, y_pred, 
        target_names=label_encoder.classes_, 
        zero_division=0
    ))
    return acc

acc_rf = evaluate(rf, "Random Forest")
acc_xgb = evaluate(xgb_model, "XGBoost")

# Ensemble
print("\n🎭 Creating Ensemble (Soft Voting)...")
ensemble = VotingClassifier(
    estimators=[('rf', rf), ('xgb', xgb_model)], 
    voting='soft'
)
ensemble.fit(X_train_scaled, y_train_encoded)
acc_ens = evaluate(ensemble, "Ensemble (RF + XGB)")

# Save models
print("\n💾 Saving models...")
joblib.dump(rf, MODEL_DIR / "rf_model.pkl")
joblib.dump(xgb_model, MODEL_DIR / "xgb_model.pkl")
joblib.dump(ensemble, MODEL_DIR / "ensemble_model.pkl")
print("✅ Models saved")

# SHAP
print("\n🔬 Generating SHAP explainer...")
rf_explainer = shap.TreeExplainer(rf)
joblib.dump(rf_explainer, MODEL_DIR / "rf_shap_explainer.pkl")
print("✅ SHAP explainer saved")

# LIME (save data sample, not explainer object)
print("💾 Saving LIME background data...")
joblib.dump(X_train_scaled[:2000], MODEL_DIR / "lime_training_sample.pkl")
joblib.dump(X.columns.tolist(), MODEL_DIR / "lime_feature_names.pkl")
joblib.dump(label_encoder.classes_.tolist(), MODEL_DIR / "lime_class_names.pkl")
print("✅ LIME data saved")

print("\n" + "=" * 60)
print("🎉 TRAINING COMPLETE!")
print("=" * 60)
print(f"📁 All files saved to: {MODEL_DIR.absolute()}")
print(f"🏆 Final Ensemble Accuracy: {acc_ens*100:.2f}%")