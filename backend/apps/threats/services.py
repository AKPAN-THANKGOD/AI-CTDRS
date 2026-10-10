import os
import time
import threading
import joblib
import numpy as np
import shap
from django.conf import settings as django_settings
from lime.lime_tabular import LimeTabularExplainer
from apps.settings.models import SystemSettings

TOP_N = 5

class ThreatDetectionService:
    _lock = threading.Lock()
    _loaded = False
    _ensemble = None
    _scaler = None
    _label_encoder = None
    _feature_names = None
    _lime_sample = None
    _shap_explainer = None
    _lime_explainer = None

    @classmethod
    def _load(cls):
        if cls._loaded:
            return
        with cls._lock:
            if cls._loaded:
                return
            
            # Path to your multi-class CIC-IDS2017 models
            model_dir = os.path.join(django_settings.BASE_DIR, 'models', 'cicids2017')
            
            cls._ensemble = joblib.load(os.path.join(model_dir, 'ensemble_model.pkl'))
            cls._scaler = joblib.load(os.path.join(model_dir, 'scaler.pkl'))
            cls._label_encoder = joblib.load(os.path.join(model_dir, 'label_encoder.pkl'))
            cls._feature_names = list(joblib.load(os.path.join(model_dir, 'feature_names.pkl')))
            cls._lime_sample = joblib.load(os.path.join(model_dir, 'lime_training_sample.pkl'))
            
            # SHAP Explainer (using the Random Forest estimator from the VotingClassifier)
            rf_model = cls._ensemble.estimators_[0]
            cls._shap_explainer = shap.TreeExplainer(rf_model)
            
            # LIME Explainer
            cls._lime_explainer = LimeTabularExplainer(
                cls._lime_sample,
                feature_names=cls._feature_names,
                class_names=cls._label_encoder.classes_.tolist(),
                mode='classification',
                discretize_continuous=False,
            )
            
            cls._loaded = True

    @classmethod
    def predict(cls, features: dict, explain: bool = True) -> dict:
        t0 = time.time()
        cls._load()
        
        # 1. Build feature vector
        names = cls._feature_names
        idx = {n: i for i, n in enumerate(names)}
        unknown = [k for k in features if k not in idx]
        
        # Initialize with zeros for missing features
        raw_vector = np.zeros(len(names))
        provided = 0
        
        for k, v in features.items():
            i = idx.get(k)
            if i is not None:
                raw_vector[i] = float(v)
                provided += 1
        
        # 2. Scale features
        X = cls._scaler.transform(raw_vector.reshape(1, -1))
        
        # 3. Predict (Multi-class)
        prediction_idx = cls._ensemble.predict(X)[0]
        proba = cls._ensemble.predict_proba(X)[0]
        
        # Get individual model confidences for the frontend
        rf_proba = cls._ensemble.estimators_[0].predict_proba(X)[0]
        xgb_proba = cls._ensemble.estimators_[1].predict_proba(X)[0]
        
        threat_type = cls._label_encoder.inverse_transform([prediction_idx])[0]
        confidence = float(proba.max())
        
        # 4. Determine severity and thresholds
        cfg = SystemSettings.load()
        is_threat = threat_type.lower() != 'benign'
        
        if not is_threat:
            severity = 'low'
        elif confidence >= cfg.critical_threshold or threat_type in ['DDoS', 'Botnet']:
            severity = 'critical'
        elif confidence >= cfg.high_threshold or threat_type in ['PortScan', 'Brute Force', 'Web Attack']:
            severity = 'high'
        elif confidence >= cfg.medium_threshold:
            severity = 'medium'
        else:
            severity = 'low'

        # 5. Build the exact payload the frontend expects
        result = {
            'is_threat': is_threat,
            'threat_type': threat_type,
            'severity': severity,
            'confidence': confidence,
            'attack_probability': confidence if is_threat else 0.0,
            'rf_confidence': float(rf_proba.max()),
            'xgb_confidence': float(xgb_proba.max()),
            'threshold_used': cfg.confidence_threshold,
            'features_provided': provided,
            'features_total': len(cls._feature_names),
            'unknown_features': unknown,
            'shap_explanation': [],
            'lime_explanation': [],
        }
        
        if explain and is_threat:
            result['shap_explanation'] = cls._shap_explain(X, raw_vector)
            result['lime_explanation'] = cls._lime_explain(X[0])
            
        result['response_time_ms'] = (time.time() - t0) * 1000
        return result

    @classmethod
    def _shap_explain(cls, X, raw):
        shap_values = cls._shap_explainer.shap_values(X)
        
        # Get the predicted class index to extract the correct SHAP values
        pred_proba = cls._ensemble.predict_proba(X)[0]
        pred_class_idx = int(np.argmax(pred_proba))
        
        # Handle multiclass SHAP output (list of arrays)
        if isinstance(shap_values, list):
            vals = np.array(shap_values[pred_class_idx])[0]
        else:
            if len(shap_values.shape) == 3:
                vals = shap_values[0, :, pred_class_idx]
            else:
                vals = shap_values[0]
                
        top_indices = np.argsort(np.abs(vals))[::-1][:TOP_N]
        
        return [
            {
                'feature': cls._feature_names[i],
                'shap_value': round(float(vals[i]), 4),
                'input_value': float(raw[i])
            }
            for i in top_indices
        ]

    @classmethod
    def _lime_explain(cls, x):
        # Explain the predicted class
        pred_proba = cls._ensemble.predict_proba(x.reshape(1, -1))[0]
        pred_idx = int(np.argmax(pred_proba))
        
        exp = cls._lime_explainer.explain_instance(
            x, 
            cls._ensemble.predict_proba, 
            num_features=TOP_N, 
            labels=[pred_idx]
        )
        
        return [
            {
                'feature': f, 
                'lime_weight': round(float(w), 4)
            }
            for f, w in exp.as_list(label=pred_idx)[:TOP_N]
        ]