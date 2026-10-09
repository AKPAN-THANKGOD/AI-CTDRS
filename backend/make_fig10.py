# LOCATION: backend/make_fig10.py  (next to manage.py and ml_models/)
"""Figure 10: real SHAP (TreeExplainer on the Random Forest) next to real LIME for ONE
test record, correctly labelled. Replaces gen_fig10.py, which plotted global
feature_importances_ under the title 'SHAP'.  Needs: shap, lime.
Usage (from backend folder):  python make_fig10.py [row_index]"""
import sys
import joblib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from lime.lime_tabular import LimeTabularExplainer
import shap
from common import MODEL_DIR, load_models, load_test, ensemble_proba

idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
rf, xgb = load_models()
X, y = load_test()
names = list(joblib.load(MODEL_DIR / "feature_names.pkl"))
bg = joblib.load(MODEL_DIR / "lime_training_sample.pkl")
x = X[idx:idx + 1]

p = ensemble_proba(rf, xgb, x)[0]
pred = int(np.argmax(p))

sv = shap.TreeExplainer(rf).shap_values(x)
vals = np.asarray(sv[1])[0] if isinstance(sv, list) else (np.asarray(sv)[0, :, 1] if np.ndim(sv) == 3 else np.asarray(sv)[0])
top = np.argsort(np.abs(vals))[::-1][:10]

lime_exp = LimeTabularExplainer(bg, feature_names=names, class_names=["Benign", "Malicious"],
                                mode="classification", discretize_continuous=False
                                ).explain_instance(x[0], lambda a: ensemble_proba(rf, xgb, a),
                                                   labels=[1], num_features=10, num_samples=2000)
lime_list = lime_exp.as_list(label=1)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 6))
a1.barh([names[i] for i in top][::-1], [vals[i] for i in top][::-1],
        color=["#d73027" if vals[i] > 0 else "#4575b4" for i in top][::-1])
a1.set_title("SHAP (TreeExplainer, Random Forest)\nlocal contribution toward 'Malicious'")
a1.set_xlabel("SHAP value"); a1.axvline(0, color="k", lw=1, ls="--")
a2.barh([f for f, _ in lime_list][::-1], [w for _, w in lime_list][::-1],
        color=["#d73027" if w > 0 else "#4575b4" for _, w in lime_list][::-1])
a2.set_title("LIME (local surrogate, ensemble)\nweight toward 'Malicious'")
a2.set_xlabel("LIME weight"); a2.axvline(0, color="k", lw=1, ls="--")
fig.suptitle(f"Figure 10: Explanation of one test record. Ensemble P(malicious)={p[1]:.3f}, "
             f"predicted {'MALICIOUS' if pred else 'BENIGN'}, true {'MALICIOUS' if y[idx] else 'BENIGN'}",
             fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.94])
out = Path("thesis_figures"); out.mkdir(exist_ok=True)
plt.savefig(out / "figure10_shap_lime.png", dpi=300); plt.savefig(out / "figure10_shap_lime.pdf")
print("saved", out / "figure10_shap_lime.png")