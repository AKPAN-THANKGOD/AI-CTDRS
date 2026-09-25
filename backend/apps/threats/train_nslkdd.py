"""
NSL-KDD Model Training Script for AI-CTDRS
Trains an ensemble model (Random Forest + XGBoost) with SHAP/LIME explainability
"""

import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import xgboost as xgb
import shap
import lime
import lime.lime_tabular
import joblib
import warnings
warnings.filterwarnings('ignore')

# ============================================
# 1. CONFIGURATION
# ============================================
DATASET_DIR = Path("datasets/nslkdd")  # 👈 Put your NSL-KDD CSV files here
MODEL_DIR = Path("models/nslkdd")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_FILE = DATASET_DIR / "KDDTrain+.csv"
TEST_FILE = DATASET_DIR / "KDDTest+.csv"

# NSL-KDD column names (the CSV doesn't have headers)
COLUMN_NAMES = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
    'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
    'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
    'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
    'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
    'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
    'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
    'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label', 'difficulty_level'
]

# Categorical columns that need encoding
CATEGORICAL_COLS = ['protocol_type', 'service', 'flag']

# ============================================
# 2. LOAD DATA
# ============================================
print("=" * 60)
print("📊 LOADING NSL-KDD DATASET")
print("=" * 60)

def load_nslkdd(filepath):
    """Load NSL-KDD dataset with proper column names"""
    df = pd.read_csv(filepath, names=COLUMN_NAMES)
    df = df.drop(columns=['difficulty_level'])  # Not needed for ML
    return df

df_train = load_nslkdd(TRAIN_FILE)
df_test = load_nslkdd(TEST_FILE)

print(f"✅ Training set: {df_train.shape}")
print(f"✅ Testing set:  {df_test.shape}")
print(f"\n📋 Label distribution (training):")
print(df_train['label'].value_counts())

# ============================================
# 3. MAP LABELS TO THREAT CATEGORIES
# ============================================
print("\n" + "=" * 60)
print("🏷️  MAPPING LABELS TO THREAT CATEGORIES")
print("=" * 60)

# NSL-KDD has many specific attack types. Group them into 5 categories:
# normal, DoS, Probe, R2L (Remote to Local), U2R (User to Root)
LABEL_MAP = {
    'normal': 'normal',
    # DoS attacks
    'back': 'dos', 'land': 'dos', 'neptune': 'dos', 'pod': 'dos',
    'smurf': 'dos', 'teardrop': 'dos', 'mailbomb': 'dos', 'processtable': 'dos',
    'udpstorm': 'dos', 'apache2': 'dos', 'worm': 'dos',
    # Probe attacks
    'satan': 'probe', 'ipsweep': 'probe', 'nmap': 'probe', 'portsweep': 'probe',
    'mscan': 'probe', 'saint': 'probe',
    # R2L attacks
    'guess_passwd': 'r2l', 'ftp_write': 'r2l', 'imap': 'r2l', 'phf': 'r2l',
    'multihop': 'r2l', 'warezmaster': 'r2l', 'warezclient': 'r2l', 'spy': 'r2l',
    'xlock': 'r2l', 'xsnoop': 'r2l', 'snmpguess': 'r2l', 'snmpgetattack': 'r2l',
    'httptunnel': 'r2l', 'sendmail': 'r2l', 'named': 'r2l', 'postgresql': 'r2l',
    # U2R attacks
    'buffer_overflow': 'u2r', 'loadmodule': 'u2r', 'rootkit': 'u2r', 'perl': 'u2r',
    'xterm': 'u2r', 'ps': 'u2r',
}

df_train['threat_category'] = df_train['label'].map(LABEL_MAP)
df_test['threat_category'] = df_test['label'].map(LABEL_MAP)

# Handle any unmapped labels
df_train = df_train.dropna(subset=['threat_category'])
df_test = df_test.dropna(subset=['threat_category'])

print(f"✅ Mapped labels. Distribution:")
print(df_train['threat_category'].value_counts())

# ============================================
# 4. PREPROCESS FEATURES
# ============================================
print("\n" + "=" * 60)
print("🔧 PREPROCESSING FEATURES")
print("=" * 60)

# Separate features and target
X_train = df_train.drop(columns=['label', 'threat_category'])
y_train = df_train['threat_category']
X_test = df_test.drop(columns=['label', 'threat_category'])
y_test = df_test['threat_category']

# One-hot encode categorical features
print("📝 One-hot encoding categorical features...")
X_train_encoded = pd.get_dummies(X_train, columns=CATEGORICAL_COLS, drop_first=False)
X_test_encoded = pd.get_dummies(X_test, columns=CATEGORICAL_COLS, drop_first=False)

# Align columns (test set might have different categories)
X_train_encoded, X_test_encoded = X_train_encoded.align(X_test_encoded, join='left', axis=1, fill_value=0)

print(f"✅ Features after encoding: {X_train_encoded.shape[1]}")

# Scale numerical features
print("📏 Scaling numerical features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_encoded)
X_test_scaled = scaler.transform(X_test_encoded)

# Encode target labels
label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
y_test_encoded = label_encoder.transform(y_test)

print(f"✅ Classes: {label_encoder.classes_}")

# Save preprocessing artifacts
joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
joblib.dump(label_encoder, MODEL_DIR / "label_encoder.pkl")
joblib.dump(X_train_encoded.columns.tolist(), MODEL_DIR / "feature_names.pkl")

print(f"💾 Saved: scaler.pkl, label_encoder.pkl, feature_names.pkl")

# ============================================
# 5. TRAIN ENSEMBLE MODEL
# ============================================
print("\n" + "=" * 60)
print("🤖 TRAINING ENSEMBLE MODEL")
print("=" * 60)

# Random Forest
print("\n🌲 Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
rf_model.fit(X_train_scaled, y_train_encoded)
print("✅ Random Forest trained")

# XGBoost
print("\n⚡ Training XGBoost...")
xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=8,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    scale_pos_weight=len(y_train_encoded[y_train_encoded==0]) / max(1, len(y_train_encoded[y_train_encoded!=0]))
)
xgb_model.fit(X_train_scaled, y_train_encoded)
print("✅ XGBoost trained")

# ============================================
# 6. EVALUATE MODELS
# ============================================
print("\n" + "=" * 60)
print("📈 MODEL EVALUATION")
print("=" * 60)

def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate a model and print metrics"""
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    print(f"\n🎯 {model_name} Results:")
    print(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall:    {recall:.4f}")
    print(f"   F1-Score:  {f1:.4f}")
    
    print(f"\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_, zero_division=0))
    
    return accuracy, precision, recall, f1

rf_metrics = evaluate_model(rf_model, X_test_scaled, y_test_encoded, "Random Forest")
xgb_metrics = evaluate_model(xgb_model, X_test_scaled, y_test_encoded, "XGBoost")

# ============================================
# 7. CREATE ENSEMBLE (Voting Classifier)
# ============================================
print("\n" + "=" * 60)
print("🎭 CREATING ENSEMBLE (Majority Voting)")
print("=" * 60)

from sklearn.ensemble import VotingClassifier

ensemble = VotingClassifier(
    estimators=[
        ('rf', rf_model),
        ('xgb', xgb_model)
    ],
    voting='soft'  # Use probability averaging
)

# Train ensemble
ensemble.fit(X_train_scaled, y_train_encoded)
ensemble_metrics = evaluate_model(ensemble, X_test_scaled, y_test_encoded, "Ensemble (RF + XGB)")

# ============================================
# 8. SAVE MODELS
# ============================================
print("\n" + "=" * 60)
print("💾 SAVING MODELS")
print("=" * 60)

joblib.dump(rf_model, MODEL_DIR / "rf_model.pkl")
joblib.dump(xgb_model, MODEL_DIR / "xgb_model.pkl")
joblib.dump(ensemble, MODEL_DIR / "ensemble_model.pkl")

print(f"✅ Saved: rf_model.pkl, xgb_model.pkl, ensemble_model.pkl")

# ============================================
# 9. SET UP SHAP EXPLAINABILITY
# ============================================
print("\n" + "=" * 60)
print("🔬 GENERATING SHAP EXPLANATIONS")
print("=" * 60)

# Use a sample for SHAP (it's computationally expensive)
X_sample = X_train_scaled[:100]

# SHAP for Random Forest
print("🌲 Computing SHAP values for Random Forest...")
rf_explainer = shap.TreeExplainer(rf_model)
rf_shap_values = rf_explainer.shap_values(X_sample)

# Save SHAP explainer
joblib.dump(rf_explainer, MODEL_DIR / "rf_shap_explainer.pkl")
print("✅ SHAP explainer saved")

# ============================================
# 10. SET UP LIME EXPLAINABILITY
# ============================================
print("\n" + "=" * 60)
print("🔬 SETTING UP LIME EXPLANATIONS")
print("=" * 60)

lime_explainer = lime.lime_tabular.LimeTabularExplainer(
    X_train_scaled,
    feature_names=X_train_encoded.columns.tolist(),
    class_names=label_encoder.classes_.tolist(),
    mode='classification',
    discretize_continuous=True
)

joblib.dump(lime_explainer, MODEL_DIR / "lime_explainer.pkl")
print("✅ LIME explainer saved")

# ============================================
# 11. GENERATE SAMPLE EXPLANATION
# ============================================
print("\n" + "=" * 60)
print("📝 SAMPLE EXPLANATION (First Test Instance)")
print("=" * 60)

sample_idx = 0
sample = X_test_scaled[sample_idx:sample_idx+1]
true_label = label_encoder.inverse_transform([y_test_encoded[sample_idx]])[0]

# Ensemble prediction
pred_proba = ensemble.predict_proba(sample)[0]
pred_class = label_encoder.inverse_transform([np.argmax(pred_proba)])[0]
confidence = pred_proba.max()

print(f"🎯 True label:      {true_label}")
print(f"🤖 Predicted label: {pred_class}")
print(f"💪 Confidence:      {confidence:.4f} ({confidence*100:.2f}%)")

# LIME explanation
lime_exp = lime_explainer.explain_instance(
    sample[0],
    ensemble.predict_proba,
    top_labels=5,
    num_features=10
)

print(f"\n🔬 LIME Explanation (top 5 features):")
for feature, weight in lime_exp.as_list()[:5]:
    print(f"   {weight:+.4f} | {feature}")

# ============================================
# 12. FINAL SUMMARY
# ============================================
print("\n" + "=" * 60)
print("🎉 TRAINING COMPLETE!")
print("=" * 60)
print(f"\n📁 All files saved to: {MODEL_DIR.absolute()}")
print(f"\n📦 Files created:")
for f in sorted(MODEL_DIR.glob("*")):
    size_kb = f.stat().st_size / 1024
    print(f"   • {f.name} ({size_kb:.1f} KB)")

print(f"\n🎯 Final Ensemble Performance:")
print(f"   Accuracy:  {ensemble_metrics[0]*100:.2f}%")
print(f"   Precision: {ensemble_metrics[1]:.4f}")
print(f"   Recall:    {ensemble_metrics[2]:.4f}")
print(f"   F1-Score:  {ensemble_metrics[3]:.4f}")

print("\n✅ Next steps:")
print("   1. Update backend/apps/threats/services.py to load these models")
print("   2. Update frontend form to match the 120+ NSL-KDD features")
print("   3. Test with sample NSL-KDD data")