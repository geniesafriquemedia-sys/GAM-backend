"""
Editorial URLs - Routes pour le contenu éditorial
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AuthorViewSet,
    CategoryViewSet,
    ArticleViewSet,
    VideoViewSet,
    HomepageView,
)

app_name = 'editorial'

# Router pour les viewsets
router = DefaultRouter()
router.register('authors', AuthorViewSet, basename='authors')
router.register('categories', CategoryViewSet, basename='categories')
router.register('articles', ArticleViewSet, basename='articles')
router.register('videos', VideoViewSet, basename='videos')
router.register('homepage', HomepageView, basename='homepage')

urlpatterns = [
    path('', include(router.urls)),
]
