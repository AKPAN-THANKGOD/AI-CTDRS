# LOCATION: backend/make_fig8.py  (next to manage.py and ml_models/)
"""Figure 8 from REAL predictions on the held-out test set (replaces gen_fig8.py,
which used a hand-typed matrix, and the random-number branch of generate_figures.py).
Usage (from backend folder):  python make_fig8.py"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from common import load_models, load_test, ensemble_proba


def run(rf, xgb, X, y, out=Path("thesis_figures")):
    out.mkdir(exist_ok=True)
    pred = np.argmax(ensemble_proba(rf, xgb, X), axis=1)
    cm = confusion_matrix(y, pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    metrics = {
        "test_set_size": int(len(y)),
        "accuracy": float(accuracy_score(y, pred)),
        "precision": float(precision_score(y, pred)),
        "recall": float(recall_score(y, pred)),
        "f1": float(f1_score(y, pred)),
        "false_positive_rate": float(fp / (fp + tn)),
        "confusion_matrix": {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)},
    }
    labels = ["Benign", "Malicious"]
    plt.figure(figsize=(6.5, 5.5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels,
                cbar_kws={"label": "Number of records"})
    plt.xlabel("Predicted label", fontweight="bold")
    plt.ylabel("True label", fontweight="bold")
    plt.title(f"Figure 8: Confusion matrix, CICIDS2017 sample (n={len(y):,})\n"
              f"Soft-voting ensemble, accuracy {metrics['accuracy']*100:.2f}%", fontweight="bold")
    plt.tight_layout()
    plt.savefig(out / "figure8_confusion_matrix.png", dpi=300)
    plt.savefig(out / "figure8_confusion_matrix.pdf")
    plt.close()
    (out / "figure8_metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    rf, xgb = load_models()
    X, y = load_test()
    print(json.dumps(run(rf, xgb, X, y), indent=2))