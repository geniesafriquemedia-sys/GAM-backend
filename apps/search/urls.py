"""
Search URLs - Routes pour la recherche
"""

from django.urls import path

from .views import (
    SearchView,
    SearchSuggestionsView,
    TrendingTagsView,
    GlobalSearchView,
)

app_name = 'search'

urlpatterns = [
    # Recherche simple
    path('', SearchView.as_view(), name='search'),

    # Recherche globale paginée
    path('global/', GlobalSearchView.as_view(), name='global-search'),

    # Suggestions
    path('suggestions/', SearchSuggestionsView.as_view(), name='suggestions'),

    # Tags populaires
    path('trending-tags/', TrendingTagsView.as_view(), name='trending-tags'),
]
