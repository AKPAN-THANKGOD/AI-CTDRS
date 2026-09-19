from django.db import models


class SystemSettings(models.Model):
    """Singleton model for system-wide settings"""
    
    # AI Detection Thresholds
    confidence_threshold = models.FloatField(
        default=0.70,
        help_text="Minimum confidence (0.0-1.0) to flag as a threat"
    )
    
    critical_threshold = models.FloatField(
        default=0.95,
        help_text="Confidence above this = CRITICAL severity"
    )
    high_threshold = models.FloatField(
        default=0.85,
        help_text="Confidence above this = HIGH severity"
    )
    medium_threshold = models.FloatField(
        default=0.70,
        help_text="Confidence above this = MEDIUM severity, below = LOW"
    )
    
    # Feature Toggles
    auto_create_incidents = models.BooleanField(
        default=True,
        help_text="Automatically create incidents when threats are detected"
    )
    auto_create_alerts = models.BooleanField(
        default=True,
        help_text="Automatically create alerts when threats are detected"
    )
    websocket_notifications = models.BooleanField(
        default=True,
        help_text="Enable real-time WebSocket notifications"
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return "System Settings"
    
    def save(self, *args, **kwargs):
        self.pk = 1  # Force singleton
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj