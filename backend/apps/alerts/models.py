import uuid
from django.db import models
from django.conf import settings


class Alert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=[
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ])
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('acknowledged', 'Acknowledged'),
        ('dismissed', 'Dismissed'),
    ], default='pending')
    threat = models.ForeignKey(
        'threats.Threat',
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True
    )
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.severity})"