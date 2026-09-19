from rest_framework import serializers
from .models import SystemSettings


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = [
            'confidence_threshold',
            'critical_threshold',
            'high_threshold',
            'medium_threshold',
            'auto_create_incidents',
            'auto_create_alerts',
            'websocket_notifications',
            'updated_at',
            'updated_by',
        ]
        read_only_fields = ['updated_at', 'updated_by']
    
    def validate_confidence_threshold(self, value):
        if not (0.5 <= value <= 0.99):
            raise serializers.ValidationError("Must be between 0.50 and 0.99")
        return value
    
    def validate(self, attrs):
        # Ensure thresholds are in logical order
        critical = attrs.get('critical_threshold', self.instance.critical_threshold if self.instance else 0.95)
        high = attrs.get('high_threshold', self.instance.high_threshold if self.instance else 0.85)
        medium = attrs.get('medium_threshold', self.instance.medium_threshold if self.instance else 0.70)
        
        if not (critical > high > medium):
            raise serializers.ValidationError({
                'critical_threshold': "Thresholds must be: critical > high > medium"
            })
        return attrs