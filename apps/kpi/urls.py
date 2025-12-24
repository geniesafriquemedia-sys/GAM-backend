"""
KPI URLs
"""

from django.urls import path
from .views import PlatformKPIView

app_name = 'kpi'

urlpatterns = [
    path('platform/', PlatformKPIView.as_view(), name='platform-kpi'),
]
