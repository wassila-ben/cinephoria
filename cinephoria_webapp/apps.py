from django.apps import AppConfig


class CinephoriaWebappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cinephoria_webapp'

    def ready(self):
        import cinephoria_webapp.signals
