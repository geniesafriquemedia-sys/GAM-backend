"""
Core Wagtail Hooks - Paramètres du site (réseaux sociaux, config globale)
"""

from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel

from .models import SocialNetwork


class SocialNetworkViewSet(SnippetViewSet):
    """Interface Wagtail pour la gestion des réseaux sociaux."""
    model = SocialNetwork
    icon = 'link'
    menu_label = 'Réseaux Sociaux'
    menu_order = 100
    add_to_admin_menu = False
    list_display = ['network', 'label', 'url', 'is_active', 'order']
    list_filter = ['is_active', 'network']
    search_fields = ['label', 'url']
    ordering = ['order', 'network']

    panels = [
        MultiFieldPanel([
            FieldPanel('network'),
            FieldPanel('label'),
        ], heading='Identification'),
        FieldPanel('url'),
        FieldRowPanel([
            FieldPanel('is_active'),
            FieldPanel('order'),
        ], heading='Affichage'),
    ]


class SiteSettingsViewSetGroup(SnippetViewSetGroup):
    """Groupe de menu pour les paramètres du site."""
    menu_label = 'Paramètres du Site'
    menu_icon = 'cog'
    menu_order = 300
    items = (SocialNetworkViewSet,)


register_snippet(SiteSettingsViewSetGroup)
