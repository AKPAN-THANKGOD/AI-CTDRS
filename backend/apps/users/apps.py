from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    label = 'users'
    verbose_name = 'Users'

    
    def ready(self):
        # Import signals to ensure they are connected
        import apps.users.signals  # noqa
    

