import kagglehub
import shutil
from pathlib import Path

print("📥 Downloading CIC-IDS2018 dataset from Kaggle...")

# Download latest version
path = kagglehub.dataset_download("primus11/cic-ids-2018-dataset")

print(f"✅ Downloaded to: {path}")

# Move files to your project structure
DATASET_DIR = Path("datasets/cicids2018")
DATASET_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n📁 Organizing files into {DATASET_DIR}...")

# Copy all CSV files from the downloaded location
downloaded_path = Path(path)
csv_files = list(downloaded_path.rglob("*.csv"))

print(f"Found {len(csv_files)} CSV files")

for csv_file in csv_files:
    dest = DATASET_DIR / csv_file.name
    shutil.copy2(csv_file, dest)
    print(f"  ✅ Copied: {csv_file.name}")

print(f"\n🎉 Dataset ready at: {DATASET_DIR.absolute()}")
print(f"📊 Total files: {len(list(DATASET_DIR.glob('*.csv')))}")