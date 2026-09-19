import uuid
from django.db import models


class Threat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    threat_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=[
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ])
    source_ip = models.GenericIPAddressField()
    destination_ip = models.GenericIPAddressField(null=True, blank=True)
    confidence = models.FloatField()
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('responded', 'Responded'),
        ('resolved', 'Resolved'),
    ], default='open')
    detected_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    raw_features = models.JSONField(null=True, blank=True)
    shap_explanation = models.JSONField(null=True, blank=True)
    lime_explanation = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"{self.threat_type} - {self.source_ip} ({self.severity})"