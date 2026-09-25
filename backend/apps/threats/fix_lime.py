"""
Final Fix for LIME Memory & Pickle Errors
Loads only a small sample of data to avoid memory limits, 
and saves the data (not the explainer object) to avoid pickle errors.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import lime.lime_tabular
import warnings
warnings.filterwarnings('ignore')

DATASET_DIR = Path("datasets/nslkdd")
MODEL_DIR = Path("models/nslkdd")

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

CATEGORICAL_COLS = ['protocol_type', 'service', 'flag']

LABEL_MAP = {
    'normal': 'normal',
    'back': 'dos', 'land': 'dos', 'neptune': 'dos', 'pod': 'dos',
    'smurf': 'dos', 'teardrop': 'dos', 'mailbomb': 'dos', 'processtable': 'dos',
    'udpstorm': 'dos', 'apache2': 'dos', 'worm': 'dos',
    'satan': 'probe', 'ipsweep': 'probe', 'nmap': 'probe', 'portsweep': 'probe',
    'mscan': 'probe', 'saint': 'probe',
    'guess_passwd': 'r2l', 'ftp_write': 'r2l', 'imap': 'r2l', 'phf': 'r2l',
    'multihop': 'r2l', 'warezmaster': 'r2l', 'warezclient': 'r2l', 'spy': 'r2l',
    'xlock': 'r2l', 'xsnoop': 'r2l', 'snmpguess': 'r2l', 'snmpgetattack': 'r2l',
    'httptunnel': 'r2l', 'sendmail': 'r2l', 'named': 'r2l', 'postgresql': 'r2l',
    'buffer_overflow': 'u2r', 'loadmodule': 'u2r', 'rootkit': 'u2r', 'perl': 'u2r',
    'xterm': 'u2r', 'ps': 'u2r',
}

print("📊 Loading a SMALL sample of training data (10,000 rows) to save memory...")
# 👈 CRITICAL FIX: nrows=10000 prevents loading the entire 125k row dataset into RAM
df_train = pd.read_csv(DATASET_DIR / "KDDTrain+.csv", names=COLUMN_NAMES, nrows=10000)
df_train = df_train.drop(columns=['difficulty_level'])
df_train['threat_category'] = df_train['label'].map(LABEL_MAP)
df_train = df_train.dropna(subset=['threat_category'])

X_train = df_train.drop(columns=['label', 'threat_category'])

print("🔧 Encoding features...")
X_train_encoded = pd.get_dummies(X_train, columns=CATEGORICAL_COLS, drop_first=False)

# Load the saved scaler and label encoder
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")
feature_names = joblib.load(MODEL_DIR / "feature_names.pkl")

# Align columns
X_train_encoded = X_train_encoded.reindex(columns=feature_names, fill_value=0)

print("📏 Scaling features...")
X_train_scaled = scaler.transform(X_train_encoded)

# ✅ THE FIX: Save the data sample, NOT the explainer object
print("💾 Saving LIME background data (5000 samples)...")
SAMPLE_SIZE = 5000
X_sample = X_train_scaled[:SAMPLE_SIZE]

joblib.dump(X_sample, MODEL_DIR / "lime_training_sample.pkl")
joblib.dump(feature_names, MODEL_DIR / "lime_feature_names.pkl")
joblib.dump(label_encoder.classes_.tolist(), MODEL_DIR / "lime_class_names.pkl")

print("✅ Saved: lime_training_sample.pkl, lime_feature_names.pkl, lime_class_names.pkl")

# Quick test to verify it works on-the-fly
print("\n🧪 Testing on-the-fly LIME creation...")
ensemble = joblib.load(MODEL_DIR / "ensemble_model.pkl")

# Load the saved data
saved_sample = joblib.load(MODEL_DIR / "lime_training_sample.pkl")
saved_features = joblib.load(MODEL_DIR / "lime_feature_names.pkl")
saved_classes = joblib.load(MODEL_DIR / "lime_class_names.pkl")

# Create explainer on the fly (this is how the backend will do it in production)
explainer = lime.lime_tabular.LimeTabularExplainer(
    saved_sample,
    feature_names=saved_features,
    class_names=saved_classes,
    mode='classification',
    discretize_continuous=False
)

test_sample = X_train_scaled[0:1]
pred_proba = ensemble.predict_proba(test_sample)[0]
pred_class = label_encoder.inverse_transform([np.argmax(pred_proba)])[0]

lime_exp = explainer.explain_instance(
    test_sample[0],
    ensemble.predict_proba,
    top_labels=1,
    num_features=5
)

print(f"🎯 Predicted: {pred_class} (confidence: {pred_proba.max():.2%})")
print(f"🔬 Top LIME features:")
for feature, weight in lime_exp.as_list()[:5]:
    print(f"   {weight:+.4f} | {feature}")

print("\n🎉 LIME fix complete! Your NSL-KDD model is now 100% ready.")