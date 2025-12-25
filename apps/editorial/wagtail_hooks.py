"""
Wagtail Hooks - Configuration de l'interface admin Wagtail
Menu personnalisé pour la gestion éditoriale GAM
"""

from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html

from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail.admin.menu import MenuItem

from apps.editorial.models import Author, Category, Article, Video

# URL du site frontend
FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')


class AuthorViewSet(SnippetViewSet):
    """Configuration de l'interface Wagtail pour les Auteurs."""
    model = Author
    icon = 'user'
    menu_label = 'Auteurs'
    menu_order = 100
    add_to_admin_menu = False
    list_display = ['name', 'email', 'is_active', 'articles_count']
    list_filter = ['is_active']
    search_fields = ['name', 'email', 'bio']


class CategoryViewSet(SnippetViewSet):
    """Configuration de l'interface Wagtail pour les Catégories."""
    model = Category
    icon = 'folder-open-inverse'
    menu_label = 'Catégories'
    menu_order = 200
    add_to_admin_menu = False
    list_display = ['name', 'color', 'is_active', 'is_featured', 'articles_count']
    list_filter = ['is_active', 'is_featured', 'parent']
    search_fields = ['name', 'description']


class ArticleViewSet(SnippetViewSet):
    """Configuration de l'interface Wagtail pour les Articles."""
    model = Article
    icon = 'doc-full'
    menu_label = 'Articles'
    menu_order = 300
    add_to_admin_menu = False
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'published_at']
    list_filter = ['status', 'is_featured', 'is_trending', 'category', 'author']
    search_fields = ['title', 'excerpt']
    ordering = ['-published_at', '-created_at']


class VideoViewSet(SnippetViewSet):
    """Configuration de l'interface Wagtail pour les Vidéos."""
    model = Video
    icon = 'media'
    menu_label = 'Vidéos'
    menu_order = 400
    add_to_admin_menu = False
    list_display = ['title', 'video_type', 'category', 'status', 'is_featured', 'published_at']
    list_filter = ['status', 'is_featured', 'is_live', 'video_type', 'category']
    search_fields = ['title', 'description']
    ordering = ['-published_at', '-created_at']


class EditorialViewSetGroup(SnippetViewSetGroup):
    """Groupe de menu pour la gestion éditoriale."""
    menu_label = 'Gestion Éditoriale'
    menu_icon = 'folder-open-1'
    menu_order = 100
    items = (ArticleViewSet, VideoViewSet, AuthorViewSet, CategoryViewSet)


# Enregistrer le groupe de snippets
register_snippet(EditorialViewSetGroup)


@hooks.register('construct_main_menu')
def hide_default_snippets_menu(request, menu_items):
    """Cache le menu Snippets par défaut car on utilise notre groupe personnalisé."""
    menu_items[:] = [item for item in menu_items if item.name != 'snippets']


@hooks.register('insert_global_admin_css')
def global_admin_css():
    """CSS personnalisé pour l'admin Wagtail - Thème GAM moderne sombre."""
    return format_html(
        '<link rel="stylesheet" href="{}core/css/wagtail-theme.css">',
        settings.STATIC_URL
    )


@hooks.register('register_admin_urls')
def register_admin_urls():
    """URLs personnalisées pour l'admin si nécessaire."""
    return []


# =============================================================================
# RACCOURCI VERS LE SITE FRONTEND
# =============================================================================

class ViewSiteMenuItem(MenuItem):
    """Menu item pour accéder au site frontend."""

    def __init__(self):
        super().__init__(
            label='Voir le site',
            url=FRONTEND_URL,
            icon_name='view',
            order=10000,  # Apparaît en bas du menu
            attrs={'target': '_blank', 'rel': 'noopener noreferrer'},
        )


@hooks.register('register_admin_menu_item')
def register_view_site_menu_item():
    """Ajoute le lien 'Voir le site' dans le menu Wagtail."""
    return ViewSiteMenuItem()


@hooks.register('insert_global_admin_js')
def global_admin_js():
    """JavaScript pour améliorer le lien 'Voir le site'."""
    return format_html('''
    <script>
        // Ajouter une icône externe au lien "Voir le site"
        document.addEventListener('DOMContentLoaded', function() {{
            const viewSiteLink = document.querySelector('a[href="{}"]');
            if (viewSiteLink) {{
                viewSiteLink.title = 'Ouvrir le site dans un nouvel onglet';
            }}
        }});
    </script>
    ''', FRONTEND_URL)
