"""
Advertising URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActiveAdsView, TrackAdView, AdvertisementAdminViewSet

router = DefaultRouter()
router.register(r'admin', AdvertisementAdminViewSet, basename='advertisement-admin')

urlpatterns = [
    # Public endpoints
    path('active/', ActiveAdsView.as_view(), name='advertising-active'),
    path('track/', TrackAdView.as_view(), name='advertising-track'),

    # Admin CRUD (staff only)
    path('', include(router.urls)),
]
