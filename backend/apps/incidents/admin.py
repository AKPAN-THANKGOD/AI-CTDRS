from django.contrib import admin
from .models import Incident, IncidentNote


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'status', 'assigned_to', 'created_at']
    list_filter = ['severity', 'status']
    search_fields = ['title', 'description']


@admin.register(IncidentNote)
class IncidentNoteAdmin(admin.ModelAdmin):
    list_display = ['incident', 'author', 'created_at']