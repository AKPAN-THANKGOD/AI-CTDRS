# LOCATION: backend/apps/threats/services.py
"""
Threat detection service (fixed).

Matches the models actually trained by train_real_models.py:
  - BINARY classifiers (0 = benign, 1 = malicious), 77 CICIDS2017 flow features
  - MinMaxScaler fitted on those 77 features
  - Ensemble weights 0.45 (RF) / 0.55 (XGB), as used in evaluate_models.py

Fixes vs. the old version:
  * unspecified features are filled with the TRAINING MEDIAN, not 0
  * values are scaled per-feature and clipped to the training range
  * real SHAP (TreeExplainer on the Random Forest) and real LIME
  * unknown feature names are reported instead of silently ignored
"""
import os
import time
import threading

import joblib
import numpy as np
from django.conf import settings as django_settings

RF_WEIGHT, XGB_WEIGHT = 0.45, 0.55
TOP_N = 5


class ThreatDetectionService:
    _lock = threading.Lock()
    _loaded = False
    _rf = _xgb = _scaler = _feature_names = None
    _lime_sample = _scaled_median = _range = _shap = _lime = None

    # ------------------------------------------------------------------ load
    @classmethod
    def _load(cls):
        if cls._loaded:
            return
        with cls._lock:
            if cls._loaded:
                return
            d = os.path.join(django_settings.BASE_DIR, 'ml_models')
            cls._rf = joblib.load(os.path.join(d, 'random_forest.pkl'))
            cls._xgb = joblib.load(os.path.join(d, 'xgboost.pkl'))
            cls._scaler = joblib.load(os.path.join(d, 'scaler.pkl'))
            cls._feature_names = list(joblib.load(os.path.join(d, 'feature_names.pkl')))
            cls._lime_sample = joblib.load(os.path.join(d, 'lime_training_sample.pkl'))

            sc = cls._scaler
            cls._range = np.where((sc.data_max_ - sc.data_min_) == 0, 1.0,
                                  sc.data_max_ - sc.data_min_)
            # median of the (already scaled) background sample = "typical" row
            cls._scaled_median = np.median(cls._lime_sample, axis=0)

            import shap
            cls._shap = shap.TreeExplainer(cls._rf)

            from lime.lime_tabular import LimeTabularExplainer
            cls._lime = LimeTabularExplainer(
                cls._lime_sample,
                feature_names=cls._feature_names,
                class_names=['Benign', 'Malicious'],
                mode='classification',
                discretize_continuous=False,
            )
            cls._loaded = True

    # --------------------------------------------------------------- helpers
    @classmethod
    def feature_names(cls):
        cls._load()
        return list(cls._feature_names)

    @classmethod
    def _build_vector(cls, features: dict):
        """Return (scaled_vector[1,77], raw_vector[77], unknown_keys, n_provided)."""
        names = cls._feature_names
        idx = {n: i for i, n in enumerate(names)}
        unknown = [k for k in features if k not in idx]
        scaled = cls._scaled_median.copy()
        raw = cls._scaler.inverse_transform(scaled.reshape(1, -1))[0]
        provided = 0
        for k, v in features.items():
            i = idx.get(k)
            if i is None:
                continue
            v = float(v)
            raw[i] = v
            scaled[i] = np.clip((v - cls._scaler.data_min_[i]) / cls._range[i], 0.0, 1.0)
            provided += 1
        return scaled.reshape(1, -1), raw, unknown, provided

    @classmethod
    def _ensemble_proba(cls, X):
        return RF_WEIGHT * cls._rf.predict_proba(X) + XGB_WEIGHT * cls._xgb.predict_proba(X)

    # --------------------------------------------------------------- predict
    @classmethod
    def predict(cls, features: dict, explain: bool = True) -> dict:
        t0 = time.time()
        cls._load()
        X, raw, unknown, provided = cls._build_vector(features)

        proba = cls._ensemble_proba(X)[0]
        p_attack = float(proba[1])

        from apps.settings.models import SystemSettings
        cfg = SystemSettings.load()
        is_threat = p_attack >= cfg.confidence_threshold
        if p_attack >= cfg.critical_threshold:
            severity = 'critical'
        elif p_attack >= cfg.high_threshold:
            severity = 'high'
        elif p_attack >= cfg.medium_threshold:
            severity = 'medium'
        else:
            severity = 'low'

        result = {
            'is_threat': is_threat,
            # The trained model is binary: it cannot name the attack family.
            'threat_type': 'Malicious Traffic' if is_threat else 'Benign Traffic',
            'severity': severity if is_threat else 'low',
            'confidence': p_attack if is_threat else float(proba[0]),
            'attack_probability': p_attack,
            'rf_confidence': float(cls._rf.predict_proba(X)[0][1]),
            'xgb_confidence': float(cls._xgb.predict_proba(X)[0][1]),
            'threshold_used': cfg.confidence_threshold,
            'features_provided': provided,
            'features_total': len(cls._feature_names),
            'unknown_features': unknown,
            'shap_explanation': [],
            'lime_explanation': [],
        }
        if provided < len(cls._feature_names) * 0.5:
            result['warning'] = (
                f"Only {provided}/{len(cls._feature_names)} features supplied; "
                "the rest were filled with training medians. Use a full flow record "
                "for a reliable result."
            )
        if explain:
            result['shap_explanation'] = cls._shap_explain(X, raw)
            result['lime_explanation'] = cls._lime_explain(X[0])
        result['response_time_ms'] = (time.time() - t0) * 1000
        return result

    # ------------------------------------------------------------ explainers
    @classmethod
    def _shap_explain(cls, X, raw):
        sv = cls._shap.shap_values(X)
        # shap versions return list[class] of (n,f), or array (n,f,classes), or (n,f)
        if isinstance(sv, list):
            vals = np.asarray(sv[1])[0]
        else:
            sv = np.asarray(sv)
            vals = sv[0, :, 1] if sv.ndim == 3 else sv[0]
        top = np.argsort(np.abs(vals))[::-1][:TOP_N]
        return [{'feature': cls._feature_names[i],
                 'shap_value': round(float(vals[i]), 4),
                 'input_value': float(raw[i])} for i in top]

    @classmethod
    def _lime_explain(cls, x):
        exp = cls._lime.explain_instance(
            x, cls._ensemble_proba, num_features=TOP_N, labels=[1], num_samples=1000)
        return [{'feature': f, 'lime_weight': round(float(w), 4)}
                for f, w in exp.as_list(label=1)[:TOP_N]]