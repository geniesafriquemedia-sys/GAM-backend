from django.apps import AppConfig


class EditorialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.editorial'
    verbose_name = 'Éditorial'

    def ready(self):
        # Importer les signaux
        from . import signals  # noqa
