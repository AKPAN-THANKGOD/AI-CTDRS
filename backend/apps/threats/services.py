import numpy as np
import joblib
import time
from django.conf import settings as django_settings
import os


class ThreatDetectionService:
    """AI-powered threat detection using ensemble ML models"""
    
    _models_loaded = False
    _rf_model = None
    _xgb_model = None
    _scaler = None
    _feature_names = None
    
    @classmethod
    def _load_models(cls):
        if cls._models_loaded:
            return
        
        model_dir = os.path.join(django_settings.BASE_DIR, 'ml_models')
        
        try:
            cls._rf_model = joblib.load(os.path.join(model_dir, 'random_forest_model.pkl'))
            cls._xgb_model = joblib.load(os.path.join(model_dir, 'xgboost_model.pkl'))
            cls._scaler = joblib.load(os.path.join(model_dir, 'scaler.pkl'))
            
            # Load feature names
            import json
            with open(os.path.join(model_dir, 'feature_names.json'), 'r') as f:
                cls._feature_names = json.load(f)
            
            cls._models_loaded = True
            print(f"✅ All models loaded. Features: {len(cls._feature_names)}")
        except Exception as e:
            print(f"❌ Failed to load models: {e}")
            raise
    
    @classmethod
    def predict(cls, features: dict) -> dict:
        """
        Predict threat using ensemble of RF + XGBoost.
        Uses configurable thresholds from SystemSettings.
        """
        start_time = time.time()
        
        cls._load_models()
        
        # Prepare feature vector
        feature_vector = []
        for fname in cls._feature_names:
            feature_vector.append(float(features.get(fname, 0)))
        
        X = np.array([feature_vector])
        
        # Scale features
        X_scaled = cls._scaler.transform(X)
        
        # Get predictions from both models
        rf_pred = cls._rf_model.predict(X_scaled)[0]
        rf_proba = cls._rf_model.predict_proba(X_scaled)[0]
        
        xgb_pred = cls._xgb_model.predict(X_scaled)[0]
        xgb_proba = cls._xgb_model.predict_proba(X_scaled)[0]
        
        # Ensemble: average probabilities
        ensemble_proba = (rf_proba + xgb_proba) / 2
        threat_proba = float(ensemble_proba[1])  # Probability of being a threat
        
        # 🔧 LOAD CONFIGURABLE THRESHOLDS FROM SETTINGS
        from apps.settings.models import SystemSettings
        settings = SystemSettings.load()
        
        # Determine if it's a threat based on configurable threshold
        is_threat = threat_proba >= settings.confidence_threshold
        
        # Determine severity based on configurable thresholds
        if threat_proba >= settings.critical_threshold:
            severity = 'critical'
        elif threat_proba >= settings.high_threshold:
            severity = 'high'
        elif threat_proba >= settings.medium_threshold:
            severity = 'medium'
        else:
            severity = 'low'
        
        # Determine threat type based on features
        threat_type = cls._classify_threat_type(features, threat_proba)
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        
        # Generate SHAP explanation (simplified)
        shap_explanation = cls._generate_shap_explanation(features, cls._feature_names)
        
        # Generate LIME explanation
        lime_explanation = cls._generate_lime_explanation(features, cls._feature_names)
        
        return {
            'is_threat': is_threat,
            'threat_type': threat_type if is_threat else 'Benign Traffic',
            'severity': severity if is_threat else 'low',
            'confidence': threat_proba,
            'rf_prediction': int(rf_pred),
            'xgb_prediction': int(xgb_pred),
            'rf_confidence': float(rf_proba[1]),
            'xgb_confidence': float(xgb_proba[1]),
            'response_time_ms': response_time_ms,
            'shap_explanation': shap_explanation,
            'lime_explanation': lime_explanation,
            'threshold_used': settings.confidence_threshold,
        }
    
    @classmethod
    def _classify_threat_type(cls, features: dict, confidence: float) -> str:
        """Classify threat type based on feature patterns"""
        syn_count = float(features.get('SYN Flag Count', 0))
        flow_packets = float(features.get('Flow Packets/s', 0))
        fwd_packets = float(features.get('Total Fwd Packets', 0))
        bwd_packets = float(features.get('Total Backward Packets', 0))
        flow_duration = float(features.get('Flow Duration', 0))
        
        # DDoS / SYN Flood
        if syn_count > 10000 and flow_packets > 100000:
            return 'DDoS / SYN Flood'
        
        # Port Scan
        if flow_duration < 100 and fwd_packets > 1000 and bwd_packets < 100:
            return 'Port Scan'
        
        # Brute Force
        if fwd_packets > 5000 and bwd_packets > 5000 and flow_duration > 1000:
            return 'Brute Force Attempt'
        
        # SQL Injection indicators
        if flow_packets > 1000 and syn_count < 100:
            return 'SQL Injection Attempt'
        
        # Default
        return 'Malicious Traffic'
    
    @classmethod
    def _generate_shap_explanation(cls, features: dict, feature_names: list) -> list:
        """Generate simplified SHAP-like explanations"""
        top_features = [
            'SYN Flag Count', 'Flow Packets/s', 'Total Fwd Packets',
            'Flow Duration', 'Total Backward Packets', 'Flow Bytes/s'
        ]
        
        explanations = []
        for fname in top_features:
            value = float(features.get(fname, 0))
            if value > 0:
                # Simplified SHAP value calculation
                shap_val = min(value / 10000, 3.0) if value > 1000 else value / 1000
                explanations.append({
                    'feature': fname,
                    'shap_value': round(shap_val, 3),
                    'input_value': value
                })
        
        # Sort by absolute SHAP value
        explanations.sort(key=lambda x: abs(x['shap_value']), reverse=True)
        return explanations[:5]
    
    @classmethod
    def _generate_lime_explanation(cls, features: dict, feature_names: list) -> list:
        """Generate simplified LIME-like explanations"""
        top_features = [
            ('SYN Flag Count > 1000', float(features.get('SYN Flag Count', 0)) > 1000),
            ('Flow Packets/s > 10000', float(features.get('Flow Packets/s', 0)) > 10000),
            ('Flow Duration < 100', float(features.get('Flow Duration', 1000)) < 100),
            ('Total Fwd Packets > 5000', float(features.get('Total Fwd Packets', 0)) > 5000),
        ]
        
        explanations = []
        for condition, met in top_features:
            if met:
                explanations.append({
                    'feature': condition,
                    'lime_weight': 0.8 if 'SYN' in condition else 0.6
                })
        
        return explanations[:4]