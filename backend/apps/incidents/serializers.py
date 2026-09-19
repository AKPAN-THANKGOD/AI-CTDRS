from rest_framework import serializers
from .models import Incident, IncidentNote


class IncidentNoteSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = IncidentNote
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class IncidentSerializer(serializers.ModelSerializer):
    notes = IncidentNoteSerializer(many=True, read_only=True)
    assigned_to_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at']
    
    def get_assigned_to_email(self, obj):
        return obj.assigned_to.email if obj.assigned_to else None