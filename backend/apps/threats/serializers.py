# LOCATION: backend/apps/threats/serializers.py
from rest_framework import serializers
from .models import Threat


class ThreatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Threat
        fields = '__all__'
        # Detection results are produced by the model, never edited by clients.
        read_only_fields = ['id', 'threat_type', 'severity', 'source_ip', 'destination_ip',
                            'confidence', 'status', 'detected_at', 'responded_at', 'resolved_at',
                            'raw_features', 'shap_explanation', 'lime_explanation']


class ThreatAnalyzeSerializer(serializers.Serializer):
    features = serializers.DictField(child=serializers.FloatField(), allow_empty=False)
    src_ip = serializers.IPAddressField()
    dst_ip = serializers.IPAddressField(required=False, allow_null=True)