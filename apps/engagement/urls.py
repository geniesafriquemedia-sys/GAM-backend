"""
Engagement URLs - Routes pour l'engagement utilisateur
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    NewsletterSubscribeView,
    NewsletterUnsubscribeView,
    AdminNewsletterViewSet,
    ContactMessageCreateView,
    AdminContactMessageViewSet,
)

app_name = 'engagement'

# Router pour les viewsets admin
router = DefaultRouter()
router.register('admin/newsletter', AdminNewsletterViewSet, basename='admin-newsletter')
router.register('admin/contacts', AdminContactMessageViewSet, basename='admin-contacts')

urlpatterns = [
    # Newsletter public
    path('newsletter/subscribe/', NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', NewsletterUnsubscribeView.as_view(), name='newsletter-unsubscribe'),

    # Contact public
    path('contact/', ContactMessageCreateView.as_view(), name='contact'),

    # Admin routes
    path('', include(router.urls)),
]
