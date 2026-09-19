from django.apps import AppConfig


class SettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.settings'
    label = 'settings'
    verbose_name = 'System Settings'