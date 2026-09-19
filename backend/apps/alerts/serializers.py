from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    acknowledged_by_email = serializers.SerializerMethodField()
    threat_id = serializers.UUIDField(source='threat.id', read_only=True, allow_null=True)
    
    class Meta:
        model = Alert
        fields = ['id', 'title', 'message', 'severity', 'status', 'threat', 'threat_id', 
                  'acknowledged_by', 'acknowledged_by_email', 'created_at', 'acknowledged_at']
        read_only_fields = ['id', 'created_at', 'acknowledged_at']
    
    def get_acknowledged_by_email(self, obj):
        return obj.acknowledged_by.email if obj.acknowledged_by else None