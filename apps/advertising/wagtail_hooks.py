"""
Advertising Wagtail Hooks - Interface admin Wagtail pour les publicités
"""

from django.utils.html import format_html
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail import hooks

from .models import Advertisement


class AdvertisementViewSet(SnippetViewSet):
    """Interface Wagtail pour la gestion des publicités."""
    model = Advertisement
    icon = 'placeholder'
    menu_label = 'Publicités'
    menu_order = 200
    add_to_admin_menu = False
    list_display = [
        'title', 'advertiser_name', 'position', 'status',
        'start_date', 'end_date',
        'impressions_count', 'clicks_count',
    ]
    list_filter = ['status', 'ad_type', 'position', 'is_active']
    search_fields = ['title', 'advertiser_name']
    ordering = ['-created_at']


class AdvertisingViewSetGroup(SnippetViewSetGroup):
    """Groupe de menu pour la régie publicitaire."""
    menu_label = 'Régie Publicitaire'
    menu_icon = 'pick'
    menu_order = 200
    items = (AdvertisementViewSet,)


register_snippet(AdvertisingViewSetGroup)
