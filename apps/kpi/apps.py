"""
KPI App Configuration
"""

from django.apps import AppConfig


class KpiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.kpi'
    verbose_name = 'KPI & Statistiques'

    def ready(self):
        import apps.kpi.signals
