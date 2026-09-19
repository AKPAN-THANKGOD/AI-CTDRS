from django.contrib import admin
from .models import Threat


@admin.register(Threat)
class ThreatAdmin(admin.ModelAdmin):
    list_display = ['threat_type', 'source_ip', 'severity', 'status', 'confidence', 'detected_at']
    list_filter = ['severity', 'status', 'threat_type']
    search_fields = ['source_ip', 'threat_type', 'notes']
    readonly_fields = ['id', 'detected_at', 'raw_features', 'shap_explanation', 'lime_explanation']