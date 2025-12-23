"""
Editorial Admin - Configuration de l'administration éditoriale
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Author, Category, Article, ArticleBlock, Video


# =============================================================================
# AUTHOR ADMIN
# =============================================================================

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Administration des auteurs."""

    list_display = ['name', 'photo_preview', 'email', 'articles_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'bio']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'user')
        }),
        ('Informations', {
            'fields': ('photo', 'bio', 'email')
        }),
        ('Réseaux sociaux', {
            'fields': ('twitter', 'linkedin', 'website'),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.photo.url
            )
        return '-'
    photo_preview.short_description = 'Photo'

    def articles_count(self, obj):
        return obj.articles.count()
    articles_count.short_description = 'Articles'


# =============================================================================
# CATEGORY ADMIN
# =============================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Administration des catégories."""

    list_display = ['name', 'color_preview', 'parent', 'articles_count', 'is_featured', 'order', 'is_active']
    list_filter = ['is_active', 'is_featured', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    list_editable = ['order', 'is_featured']

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Apparence', {
            'fields': ('color', 'icon', 'image')
        }),
        ('Hiérarchie', {
            'fields': ('parent', 'order')
        }),
        ('Statut', {
            'fields': ('is_active', 'is_featured')
        }),
    )

    def color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 15px; border-radius: 3px; color: white;">{}</span>',
            obj.color, obj.color
        )
    color_preview.short_description = 'Couleur'

    def articles_count(self, obj):
        return obj.articles.count()
    articles_count.short_description = 'Articles'


# =============================================================================
# ARTICLE BLOCK INLINE
# =============================================================================

class ArticleBlockInline(admin.TabularInline):
    """Inline pour les blocs d'article."""

    model = ArticleBlock
    extra = 0
    ordering = ['order']
    fields = ['block_type', 'order', 'content', 'image', 'embed_url']


# =============================================================================
# ARTICLE ADMIN
# =============================================================================

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Administration des articles."""

    list_display = [
        'title', 'author', 'category', 'status_badge',
        'is_featured', 'views_count', 'reading_time', 'published_at'
    ]
    list_filter = ['status', 'is_featured', 'is_trending', 'category', 'author', 'created_at']
    search_fields = ['title', 'excerpt', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_editable = ['is_featured']
    raw_id_fields = ['author', 'created_by', 'updated_by']
    inlines = [ArticleBlockInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'excerpt')
        }),
        ('Contenu', {
            'fields': ('featured_image', 'featured_image_caption', 'content')
        }),
        ('Relations', {
            'fields': ('author', 'category', 'tags')
        }),
        ('Publication', {
            'fields': ('status', 'published_at', 'is_featured', 'is_trending')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('reading_time', 'views_count', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['reading_time', 'views_count', 'created_by', 'updated_by']

    def status_badge(self, obj):
        colors = {
            'draft': '#FFA500',
            'published': '#28A745',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['publish_articles', 'unpublish_articles', 'feature_articles']

    @admin.action(description='Publier les articles sélectionnés')
    def publish_articles(self, request, queryset):
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} article(s) publié(s).')

    @admin.action(description='Dépublier les articles sélectionnés')
    def unpublish_articles(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} article(s) dépublié(s).')

    @admin.action(description='Mettre en vedette')
    def feature_articles(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} article(s) mis en vedette.')


# =============================================================================
# VIDEO ADMIN
# =============================================================================

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Administration des vidéos."""

    list_display = [
        'title', 'thumbnail_preview', 'video_type', 'category',
        'status_badge', 'is_featured', 'is_live', 'views_count', 'published_at'
    ]
    list_filter = ['status', 'video_type', 'is_featured', 'is_live', 'category', 'created_at']
    search_fields = ['title', 'description', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_editable = ['is_featured', 'is_live']
    raw_id_fields = ['created_by']

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description')
        }),
        ('Vidéo', {
            'fields': ('youtube_url', 'youtube_id', 'youtube_thumbnail', 'thumbnail', 'duration')
        }),
        ('Catégorisation', {
            'fields': ('video_type', 'category', 'tags')
        }),
        ('Publication', {
            'fields': ('status', 'published_at', 'is_featured', 'is_live')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('views_count', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['youtube_id', 'youtube_thumbnail', 'views_count', 'created_by']

    def thumbnail_preview(self, obj):
        url = obj.thumbnail_url
        if url:
            return format_html(
                '<img src="{}" width="80" height="45" style="object-fit: cover; border-radius: 4px;" />',
                url
            )
        return '-'
    thumbnail_preview.short_description = 'Miniature'

    def status_badge(self, obj):
        colors = {
            'draft': '#FFA500',
            'published': '#28A745',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['publish_videos', 'unpublish_videos', 'feature_videos']

    @admin.action(description='Publier les vidéos sélectionnées')
    def publish_videos(self, request, queryset):
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} vidéo(s) publiée(s).')

    @admin.action(description='Dépublier les vidéos sélectionnées')
    def unpublish_videos(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} vidéo(s) dépubliée(s).')

    @admin.action(description='Mettre en vedette')
    def feature_videos(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} vidéo(s) mise(s) en vedette.')
