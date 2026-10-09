# LOCATION: backend/apps/settings/serializers.py
from rest_framework import serializers
from .models import SystemSettings

THRESHOLDS = ('confidence_threshold', 'critical_threshold', 'high_threshold', 'medium_threshold')


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = [*THRESHOLDS, 'auto_create_incidents', 'auto_create_alerts',
                  'websocket_notifications', 'updated_at', 'updated_by']
        read_only_fields = ['updated_at', 'updated_by']

    def _range(self, value):
        if not (0.5 <= value <= 0.99):
            raise serializers.ValidationError("Must be between 0.50 and 0.99")
        return value

    validate_confidence_threshold = _range
    validate_critical_threshold = _range
    validate_high_threshold = _range
    validate_medium_threshold = _range

    def validate(self, attrs):
        inst = self.instance
        get = lambda k, d: attrs.get(k, getattr(inst, k, d) if inst else d)
        critical, high, medium = (get('critical_threshold', 0.95),
                                  get('high_threshold', 0.85),
                                  get('medium_threshold', 0.70))
        if not (critical > high > medium):
            raise serializers.ValidationError(
                {'critical_threshold': "Thresholds must be: critical > high > medium"})
        return attrs