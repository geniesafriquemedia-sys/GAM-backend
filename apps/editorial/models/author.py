"""
Author Model - Gestion des auteurs (US-01)
Wagtail Snippet pour interface unifiée
"""

from django.db import models
from django.conf import settings
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from apps.core.models import TimeStampedModel, SluggedModel


# Note: Enregistré comme snippet via EditorialViewSetGroup dans wagtail_hooks.py
class Author(TimeStampedModel, SluggedModel):
    """
    Modèle Auteur pour les articles.
    US-01: Ajout d'une photo et d'une biographie pour chaque auteur.
    """

    # Lien optionnel vers un utilisateur
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='author_profile',
        verbose_name='Utilisateur lié'
    )

    # Informations de l'auteur
    name = models.CharField(
        'Nom',
        max_length=255,
        db_index=True
    )
    photo = models.ImageField(
        'Photo',
        upload_to='authors/photos/',
        blank=True,
        null=True,
        help_text='Photo de l\'auteur (format carré recommandé)'
    )
    bio = models.TextField(
        'Biographie',
        blank=True,
        help_text='Biographie de l\'auteur'
    )
    email = models.EmailField(
        'Email',
        blank=True,
        help_text='Email de contact (optionnel)'
    )

    # Réseaux sociaux
    twitter = models.URLField(
        'Twitter/X',
        blank=True
    )
    linkedin = models.URLField(
        'LinkedIn',
        blank=True
    )
    website = models.URLField(
        'Site web',
        blank=True
    )

    # Statut
    is_active = models.BooleanField(
        'Actif',
        default=True,
        help_text='Les auteurs inactifs n\'apparaissent pas dans les listes'
    )

    # Configuration du slug
    slug_source_field = 'name'

    # Wagtail Panels pour l'interface admin
    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('photo'),
            FieldPanel('bio'),
            FieldPanel('email'),
        ], heading="Informations de l'auteur"),
        MultiFieldPanel([
            FieldPanel('twitter'),
            FieldPanel('linkedin'),
            FieldPanel('website'),
        ], heading="Réseaux sociaux"),
        FieldPanel('is_active'),
    ]

    class Meta:
        verbose_name = 'Auteur'
        verbose_name_plural = 'Auteurs'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def articles_count(self) -> int:
        """Nombre d'articles publiés par cet auteur."""
        return self.articles.filter(status='published').count()

    @property
    def photo_url(self) -> str:
        """URL de la photo ou placeholder."""
        if self.photo:
            return self.photo.url
        return ''
