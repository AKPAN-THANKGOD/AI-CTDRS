import os
import gc
import urllib.request
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils import resample

print("🌐 Step 1: Checking/Downloading real CICIDS2017 dataset...")
url = "https://raw.githubusercontent.com/Western-OC2-Lab/Intrusion-Detection-System-Using-Machine-Learning/main/data/CICIDS2017_sample.csv"
file_path = "cicids2017_preprocessed.csv"

if not os.path.exists(file_path):
    print("   Downloading...")
    urllib.request.urlretrieve(url, file_path)
    print("   ✅ Download complete!")
else:
    print("   ✅ Dataset already exists.")

print("\n🔄 Step 2: Loading and Preprocessing Data...")
df = pd.read_csv(file_path, low_memory=True)

df['label'] = df['Label'].apply(lambda x: 0 if 'BENIGN' in str(x).upper() else 1)
df = df.drop(columns=['Label'], errors='ignore')
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.fillna(0, inplace=True)

# Downcast to save memory
for col in df.select_dtypes(include=['float64']).columns:
    df[col] = pd.to_numeric(df[col], downcast='float')
for col in df.select_dtypes(include=['int64']).columns:
    df[col] = pd.to_numeric(df[col], downcast='integer')

# Encode categoricals
categorical_cols = df.select_dtypes(include=['object', 'category']).columns
le_dict = {}
for col in categorical_cols:
    if col == 'label':
        continue
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    le_dict[col] = le

y = df['label'].values.astype(np.int8)
X_df = df.drop(columns=['label'])
feature_names = list(X_df.columns)
X = X_df.values.astype(np.float32)

del df, X_df
gc.collect()

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
del X
gc.collect()

print("\n🔄 Step 3: Splitting data...")
X_temp, X_test, y_temp, y_test = train_test_split(X_scaled, y, test_size=0.15, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.176, random_state=42, stratify=y_temp)

print(f"   Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")

# Save data for LIME
print("\n💾 Saving data for LIME training...")
os.makedirs('ml_models', exist_ok=True)
joblib.dump(X_train, 'ml_models/X_train_scaled.pkl')
joblib.dump(y_train, 'ml_models/y_train.pkl')
joblib.dump(X_val, 'ml_models/X_val_scaled.pkl')
joblib.dump(y_val, 'ml_models/y_val.pkl')
joblib.dump(X_test, 'ml_models/X_test_scaled.pkl')
joblib.dump(y_test, 'ml_models/y_test.pkl')

# Save a representative sample for LIME
lime_sample, _ = resample(X_train, y_train, n_samples=min(1000, len(X_train)), 
                          stratify=y_train, random_state=42)
joblib.dump(lime_sample, 'ml_models/lime_training_sample.pkl')
print(f"   ✅ Saved LIME training sample: {lime_sample.shape}")

print("\n🚀 Step 4: Training Random Forest...")
rf_model = RandomForestClassifier(n_estimators=300, max_depth=20, min_samples_leaf=2, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

print("🚀 Training XGBoost...")
xgb_model = XGBClassifier(n_estimators=250, learning_rate=0.1, max_depth=8, random_state=42, n_jobs=-1, eval_metric='logloss')
xgb_model.fit(X_train, y_train)

print("\n📊 Step 5: Evaluating...")
rf_preds = rf_model.predict(X_test)
xgb_preds = xgb_model.predict(X_test)

print("\n--- Random Forest Performance ---")
print(classification_report(y_test, rf_preds, target_names=['Benign (0)', 'Malicious (1)']))
print("--- XGBoost Performance ---")
print(classification_report(y_test, xgb_preds, target_names=['Benign (0)', 'Malicious (1)']))

print("\n💾 Step 6: Saving RF and XGBoost models...")
joblib.dump(rf_model, 'ml_models/random_forest.pkl')
joblib.dump(xgb_model, 'ml_models/xgboost.pkl')
joblib.dump(scaler, 'ml_models/scaler.pkl')
joblib.dump(le_dict, 'ml_models/label_encoders.pkl')
joblib.dump(feature_names, 'ml_models/feature_names.pkl')

print("✅ Phase 1 Complete! RF & XGBoost saved. Data ready for evaluation.")