from django.apps import AppConfig


class AppNuamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_nuam'

    #para cuando las señales se carguen al iniciar la app
    def ready(self):
        import app_nuam.signals