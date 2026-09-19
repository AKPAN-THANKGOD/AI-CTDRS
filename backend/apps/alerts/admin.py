from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'status', 'created_at']
    list_filter = ['severity', 'status']
    search_fields = ['title', 'message']