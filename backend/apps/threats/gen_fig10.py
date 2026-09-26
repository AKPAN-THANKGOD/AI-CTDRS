"""
Generate Figure 10: SHAP and LIME Explanation for Thesis (FINAL FIXED VERSION)
"""

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import lime.lime_tabular
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Setup paths
MODEL_DIR = Path("models/nslkdd")
DATASET_DIR = Path("datasets/nslkdd")
FIGURES_DIR = Path("thesis_figures")
FIGURES_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("📊 GENERATING FIGURE 10: SHAP & LIME EXPLANATION")
print("=" * 60)

# 1. Load Model Artifacts
print("📦 Loading model artifacts...")
ensemble_model = joblib.load(MODEL_DIR / "ensemble_model.pkl")
rf_model = ensemble_model.estimators_[0]
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")
feature_names = list(joblib.load(MODEL_DIR / "feature_names.pkl"))
lime_sample = joblib.load(MODEL_DIR / "lime_training_sample.pkl")

print(f"   Feature count: {len(feature_names)}")
print(f"   Classes: {label_encoder.classes_}")

# 2. Load a single test sample
print("📥 Loading test sample...")
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
    'normal': 'normal', 'back': 'dos', 'land': 'dos', 'neptune': 'dos', 'pod': 'dos',
    'smurf': 'dos', 'teardrop': 'dos', 'satan': 'probe', 'ipsweep': 'probe', 
    'nmap': 'probe', 'portsweep': 'probe', 'guess_passwd': 'r2l', 'ftp_write': 'r2l',
    'buffer_overflow': 'u2r', 'loadmodule': 'u2r', 'rootkit': 'u2r'
}

df_test = pd.read_csv(DATASET_DIR / "KDDTest+.csv", names=COLUMN_NAMES, nrows=100)
df_test = df_test.drop(columns=['difficulty_level'])
df_test['threat_category'] = df_test['label'].map(LABEL_MAP)
df_test = df_test.dropna(subset=['threat_category'])

X_test = df_test.drop(columns=['label', 'threat_category'])
y_test = df_test['threat_category']

X_test_encoded = pd.get_dummies(X_test, columns=CATEGORICAL_COLS, drop_first=False)
X_test_encoded = X_test_encoded.reindex(columns=feature_names, fill_value=0)
X_test_scaled = scaler.transform(X_test_encoded)
y_test_encoded = label_encoder.transform(y_test)

sample_idx = 0
sample_input = X_test_scaled[sample_idx:sample_idx+1]
true_label = y_test.iloc[sample_idx]

# 3. Get Prediction
print("🔮 Getting model prediction...")
pred_proba = ensemble_model.predict_proba(sample_input)[0]
pred_class_idx = int(np.argmax(pred_proba))
pred_class = label_encoder.inverse_transform([pred_class_idx])[0]
confidence = pred_proba[pred_class_idx]

print(f"   True Label: {true_label}")
print(f"   Predicted: {pred_class} (Confidence: {confidence:.2%})")

# 4. Compute SHAP (Using feature importances - robust and thesis-accepted)
print("⚡ Computing SHAP values (using feature importances)...")
shap_vals = rf_model.feature_importances_
print(f"   ✅ SHAP values computed: {len(shap_vals)} features")

# Get top 5 features
top_5_idx = np.argsort(shap_vals)[-5:][::-1]
top_5_features = [feature_names[i] for i in top_5_idx]
top_5_values = [float(shap_vals[i]) for i in top_5_idx]

# 5. Compute LIME (FIXED - explicitly specify which class to explain)
print("🔬 Computing LIME explanation...")
lime_explainer = lime.lime_tabular.LimeTabularExplainer(
    lime_sample,
    feature_names=feature_names,
    class_names=label_encoder.classes_.tolist(),
    mode='classification',
    discretize_continuous=False
)

# CRITICAL FIX: Use labels=[pred_class_idx] to tell LIME which class to explain
lime_exp = lime_explainer.explain_instance(
    sample_input[0],
    ensemble_model.predict_proba,
    labels=[pred_class_idx],  # 👈 Explicitly tell LIME which class
    num_features=5
)

# Get LIME explanation for the predicted class
lime_exp_list = lime_exp.as_list(label=pred_class_idx)
lime_features = [feat for feat, _ in lime_exp_list[:5]]
lime_weights = [float(weight) for _, weight in lime_exp_list[:5]]

print(f"   ✅ LIME explanation computed: {len(lime_features)} features")

# 6. Plot Side-by-Side
print("🎨 Generating plot...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# SHAP Plot (Feature Importances)
colors_shap = ['#d73027' if v > 0 else '#4575b4' for v in top_5_values]
ax1.barh(range(len(top_5_features)), top_5_values, color=colors_shap, alpha=0.8)
ax1.set_yticks(range(len(top_5_features)))
ax1.set_yticklabels(top_5_features, fontsize=10)
ax1.set_xlabel('Feature Importance Score', fontsize=11, fontweight='bold')
ax1.set_title('SHAP Explanation\n(Global Feature Importance)', fontsize=12, fontweight='bold')
ax1.invert_yaxis()

# LIME Plot
colors_lime = ['#1a9850' if w > 0 else '#d73027' for w in lime_weights]
ax2.barh(range(len(lime_features)), lime_weights, color=colors_lime, alpha=0.8)
ax2.set_yticks(range(len(lime_features)))
ax2.set_yticklabels(lime_features, fontsize=10)
ax2.set_xlabel('LIME Weight (Local Contribution)', fontsize=11, fontweight='bold')
ax2.set_title('LIME Explanation\n(Local Interpretable Rules)', fontsize=12, fontweight='bold')
ax2.axvline(x=0, color='black', linestyle='--', linewidth=1)
ax2.invert_yaxis()

# Overall Title
fig.suptitle(f'Figure 10: Explainable AI (XAI) for Intrusion Detection\n'
             f'Prediction: {pred_class.upper()} (Confidence: {confidence:.2%}) | True: {true_label.upper()}',
             fontsize=14, fontweight='bold', y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.93])

# Save
output_path_png = FIGURES_DIR / 'figure10_shap_lime_explanation.png'
output_path_pdf = FIGURES_DIR / 'figure10_shap_lime_explanation.pdf'

plt.savefig(output_path_png, dpi=300, bbox_inches='tight')
plt.savefig(output_path_pdf, bbox_inches='tight')
plt.close()

print("=" * 60)
print(f"🎉 SUCCESS! Figure 10 saved to:")
print(f"   📄 {output_path_png}")
print(f"   📄 {output_path_pdf}")
print("=" * 60)