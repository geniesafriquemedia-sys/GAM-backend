"""
Video Model - Gestion des vidéos Web TV (US-03)
Wagtail Snippet pour interface unifiée
"""

from django.db import models
from django.conf import settings
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel
from wagtail.search import index
from apps.core.models import (
    TimeStampedModel,
    SluggedModel,
    PublishableModel,
    SEOModel
)
from apps.core.validators import validate_youtube_url


# Note: Enregistré comme snippet via EditorialViewSetGroup dans wagtail_hooks.py
class Video(index.Indexed, TimeStampedModel, SluggedModel, PublishableModel, SEOModel):
    """
    Modèle Vidéo pour la Web TV.
    US-03: Publication de vidéos via URL YouTube.
    """

    class VideoType(models.TextChoices):
        EMISSION = 'emission', 'Émission'
        REPORTAGE = 'reportage', 'Reportage'
        INTERVIEW = 'interview', 'Interview'
        DOCUMENTARY = 'documentary', 'Documentaire'
        SHORT = 'short', 'Court métrage'

    # Informations principales
    title = models.CharField(
        'Titre',
        max_length=255,
        db_index=True
    )
    description = models.TextField(
        'Description',
        blank=True,
        help_text='Description de la vidéo'
    )
    youtube_url = models.URLField(
        'URL YouTube',
        validators=[validate_youtube_url],
        help_text='URL de la vidéo YouTube'
    )

    # Miniature (auto-récupérée ou personnalisée)
    thumbnail = models.ImageField(
        'Miniature personnalisée',
        upload_to='videos/thumbnails/',
        blank=True,
        null=True,
        help_text='Laisser vide pour utiliser la miniature YouTube'
    )
    youtube_thumbnail = models.URLField(
        'Miniature YouTube',
        blank=True,
        help_text='URL de la miniature YouTube (auto-générée)'
    )

    # Catégorisation
    video_type = models.CharField(
        'Type de vidéo',
        max_length=20,
        choices=VideoType.choices,
        default=VideoType.REPORTAGE,
        db_index=True
    )
    category = models.ForeignKey(
        'editorial.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
        verbose_name='Catégorie'
    )
    tags = models.CharField(
        'Tags',
        max_length=500,
        blank=True,
        help_text='Tags séparés par des virgules'
    )

    # Durée et métadonnées
    duration = models.PositiveIntegerField(
        'Durée (secondes)',
        default=0,
        help_text='Durée de la vidéo en secondes'
    )
    youtube_id = models.CharField(
        'ID YouTube',
        max_length=20,
        blank=True,
        db_index=True
    )

    # Statistiques
    views_count = models.PositiveIntegerField(
        'Nombre de vues',
        default=0
    )

    # Mise en avant
    is_featured = models.BooleanField(
        'En vedette',
        default=False,
        db_index=True,
        help_text='Marquer comme vidéo en vedette (US-03)'
    )
    is_live = models.BooleanField(
        'En direct',
        default=False,
        help_text='Marquer comme diffusion en direct'
    )

    # Utilisateur créateur
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_videos',
        verbose_name='Créé par'
    )

    # Configuration du slug
    slug_source_field = 'title'

    # Wagtail Panels pour l'interface admin
    panels = [
        MultiFieldPanel([
            FieldPanel('title'),
            FieldPanel('description'),
            FieldPanel('youtube_url'),
            FieldPanel('thumbnail'),
        ], heading="Informations de la vidéo"),
        MultiFieldPanel([
            FieldPanel('video_type'),
            FieldPanel('category'),
            FieldPanel('tags'),
            FieldPanel('duration'),
        ], heading="Classification"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('status'),
                FieldPanel('published_at'),
            ]),
            FieldRowPanel([
                FieldPanel('is_featured'),
                FieldPanel('is_live'),
            ]),
        ], heading="Publication"),
        MultiFieldPanel([
            FieldPanel('meta_title'),
            FieldPanel('meta_description'),
        ], heading="SEO", classname="collapsed"),
    ]

    # Wagtail Search Index
    search_fields = [
        index.SearchField('title', boost=10),
        index.SearchField('description', boost=5),
        index.FilterField('status'),
        index.FilterField('video_type'),
        index.FilterField('category'),
        index.FilterField('is_featured'),
    ]

    class Meta:
        verbose_name = 'Vidéo'
        verbose_name_plural = 'Vidéos'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['video_type', 'status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Extraire l'ID YouTube et générer la miniature
        if self.youtube_url and not self.youtube_id:
            from apps.core.utils import extract_youtube_id, get_youtube_thumbnail
            self.youtube_id = extract_youtube_id(self.youtube_url)
            if self.youtube_id and not self.youtube_thumbnail:
                self.youtube_thumbnail = get_youtube_thumbnail(self.youtube_id)
        super().save(*args, **kwargs)

    @property
    def thumbnail_url(self) -> str:
        """Retourne l'URL de la miniature (personnalisée ou YouTube)."""
        if self.thumbnail:
            return self.thumbnail.url
        return self.youtube_thumbnail or ''

    @property
    def embed_url(self) -> str:
        """Retourne l'URL d'embed YouTube."""
        if self.youtube_id:
            return f'https://www.youtube.com/embed/{self.youtube_id}'
        return ''

    @property
    def duration_formatted(self) -> str:
        """Retourne la durée formatée (MM:SS ou HH:MM:SS)."""
        if not self.duration:
            return '0:00'

        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60

        if hours:
            return f'{hours}:{minutes:02d}:{seconds:02d}'
        return f'{minutes}:{seconds:02d}'

    def get_tags_list(self) -> list:
        """Retourne les tags sous forme de liste."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def increment_views(self):
        """Incrémente le compteur de vues."""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    @property
    def related_videos(self):
        """Retourne les vidéos liées."""
        queryset = Video.objects.filter(
            status=self.PublicationStatus.PUBLISHED
        ).exclude(pk=self.pk)

        # Même type de vidéo en priorité
        same_type = queryset.filter(video_type=self.video_type)[:4]
        if same_type.count() >= 4:
            return same_type

        # Compléter avec la même catégorie
        if self.category:
            same_category = queryset.filter(category=self.category).exclude(
                pk__in=same_type.values_list('pk', flat=True)
            )[:4 - same_type.count()]
            return list(same_type) + list(same_category)

        return same_type
