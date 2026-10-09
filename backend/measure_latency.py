# LOCATION: backend/measure_latency.py  (next to manage.py and ml_models/)
"""MEASURED latency (replaces the p95 = 1.5x mean / p99 = 2x mean placeholders in
evaluate_models.py). Times single-record predictions, the way the API uses them.
Usage (from backend folder):  python measure_latency.py"""
import json, time
import numpy as np
from common import load_models, load_test, ensemble_proba


def run(rf, xgb, X, n=500):
    rng = np.random.default_rng(0)
    rows = X[rng.choice(len(X), size=min(n, len(X)), replace=False)]
    for r in rows[:20]:                       # warm-up (first calls are slower)
        ensemble_proba(rf, xgb, r.reshape(1, -1))
    t = []
    for r in rows:
        s = time.perf_counter()
        ensemble_proba(rf, xgb, r.reshape(1, -1))
        t.append((time.perf_counter() - s) * 1000)
    t = np.array(t)
    return {"records_timed": int(len(t)), "scope": "model inference only, single record, ms",
            "mean": float(t.mean()), "p50": float(np.percentile(t, 50)),
            "p95": float(np.percentile(t, 95)), "p99": float(np.percentile(t, 99)),
            "max": float(t.max())}


if __name__ == "__main__":
    rf, xgb = load_models()
    X, _ = load_test()
    res = run(rf, xgb, X)
    json.dump(res, open("latency_results.json", "w"), indent=2)
    print(json.dumps(res, indent=2))
    print("\nThis is MODEL time only. Time the full /api/threats/analyze/ call (incl. SHAP+LIME)"
          "\nseparately, e.g. with curl -w '%{time_total}', before claiming an end-to-end figure.")