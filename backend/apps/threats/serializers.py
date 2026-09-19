from rest_framework import serializers
from .models import Threat


class ThreatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Threat
        fields = '__all__'
        read_only_fields = ['id', 'detected_at', 'responded_at', 'resolved_at']


class ThreatAnalyzeSerializer(serializers.Serializer):
    features = serializers.DictField(child=serializers.FloatField())
    src_ip = serializers.IPAddressField()
    dst_ip = serializers.IPAddressField(required=False, allow_null=True)