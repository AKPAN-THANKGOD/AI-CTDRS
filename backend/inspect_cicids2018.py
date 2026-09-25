import pandas as pd
from pathlib import Path

DATA_FILE = Path("datasets/cicids2018/cic.csv")

print("📊 Loading first 1000 rows to inspect structure...")
df = pd.read_csv(DATA_FILE, nrows=1000)

print(f"\n✅ Shape: {df.shape}")
print(f"\n📋 Column names ({len(df.columns)} total):")
print(df.columns.tolist()[:10])  # First 10 columns
print("...")
print(df.columns.tolist()[-10:])  # Last 10 columns

# Find the label column
label_cols = [col for col in df.columns if 'label' in col.lower() or 'attack' in col.lower() or 'class' in col.lower()]
print(f"\n🏷️ Potential label columns: {label_cols}")

if label_cols:
    label_col = label_cols[0]
    print(f"\n📊 Label distribution (first 1000 rows):")
    print(df[label_col].value_counts())