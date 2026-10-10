from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'

    def ready(self):
        """
        Import signals to ensure they are connected when the app is ready.
        This is required for the post_migrate signal to automatically 
        create the superadmin account on every deployment.
        """
        import apps.users.signals  # noqa