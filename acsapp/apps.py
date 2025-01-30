from django.apps import AppConfig


class AcsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'acsapp'

    def ready(self):
        import acsapp.signals  # Import signals when app is ready

