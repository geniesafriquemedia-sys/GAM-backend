"""
Core Models - Modèles de base réutilisables
"""

import uuid
from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    """
    Modèle abstrait avec timestamps de création et modification.
    Hérité par tous les modèles métier.
    """
    created_at = models.DateTimeField(
        'Date de création',
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        'Date de modification',
        auto_now=True
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDModel(models.Model):
    """
    Modèle abstrait avec UUID comme clé primaire.
    Utile pour les APIs publiques (évite l'énumération d'IDs).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    class Meta:
        abstract = True


class SluggedModel(models.Model):
    """
    Modèle abstrait avec slug auto-généré.
    """
    slug = models.SlugField(
        'Slug',
        max_length=255,
        unique=True,
        blank=True,
        db_index=True
    )

    # Champ source pour le slug (à définir dans les sous-classes)
    slug_source_field = 'title'

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            source = getattr(self, self.slug_source_field, '')
            self.slug = self._generate_unique_slug(source)
        super().save(*args, **kwargs)

    def _generate_unique_slug(self, source: str) -> str:
        """Génère un slug unique."""
        base_slug = slugify(source)
        slug = base_slug
        counter = 1

        while self.__class__.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug


class PublishableModel(models.Model):
    """
    Modèle abstrait pour les contenus publiables.
    Gère le workflow de publication (US-04).
    """
    class PublicationStatus(models.TextChoices):
        DRAFT = 'draft', 'Brouillon'
        PUBLISHED = 'published', 'Publié'

    status = models.CharField(
        'Statut',
        max_length=20,
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
        db_index=True
    )
    published_at = models.DateTimeField(
        'Date de publication',
        null=True,
        blank=True,
        db_index=True,
        help_text='Laisser vide pour publier immédiatement, ou définir une date future pour planifier.'
    )

    class Meta:
        abstract = True

    @property
    def is_published(self) -> bool:
        """Vérifie si le contenu est publié."""
        from django.utils import timezone

        if self.status != self.PublicationStatus.PUBLISHED:
            return False

        if self.published_at and self.published_at > timezone.now():
            return False

        return True


class SEOModel(models.Model):
    """
    Modèle abstrait pour les métadonnées SEO (US-11).
    """
    meta_title = models.CharField(
        'Meta Title',
        max_length=70,
        blank=True,
        help_text='Titre pour les moteurs de recherche (max 70 caractères)'
    )
    meta_description = models.TextField(
        'Meta Description',
        max_length=160,
        blank=True,
        help_text='Description pour les moteurs de recherche (max 160 caractères)'
    )

    class Meta:
        abstract = True

    def get_seo_title(self) -> str:
        """Retourne le titre SEO ou le titre par défaut."""
        if self.meta_title:
            return self.meta_title
        return getattr(self, 'title', '')

    def get_seo_description(self) -> str:
        """Retourne la description SEO ou un extrait."""
        if self.meta_description:
            return self.meta_description
        # Essayer de récupérer un extrait ou une description
        for field in ['excerpt', 'description', 'content']:
            if hasattr(self, field):
                text = getattr(self, field)
                if text:
                    return text[:157] + '...' if len(text) > 160 else text
        return ''


class OrderedModel(models.Model):
    """
    Modèle abstrait pour les éléments ordonnables.
    """
    order = models.PositiveIntegerField(
        'Ordre',
        default=0,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ['order']


class SocialNetwork(TimeStampedModel):
    """
    Réseaux sociaux du site GAM — géré depuis l'admin Wagtail.
    Permet aux opérateurs d'ajouter/modifier les liens sans toucher au code.
    """

    class Network(models.TextChoices):
        FACEBOOK  = 'facebook',  'Facebook'
        LINKEDIN  = 'linkedin',  'LinkedIn'
        WHATSAPP  = 'whatsapp',  'WhatsApp'
        TIKTOK    = 'tiktok',    'TikTok'
        YOUTUBE   = 'youtube',   'YouTube'
        INSTAGRAM = 'instagram', 'Instagram'
        TWITTER   = 'twitter',   'Twitter / X'
        TELEGRAM  = 'telegram',  'Telegram'
        SNAPCHAT  = 'snapchat',  'Snapchat'
        OTHER     = 'other',     'Autre'

    network = models.CharField(
        'Réseau',
        max_length=30,
        choices=Network.choices,
        unique=True,
        help_text="Identifiant du réseau (détermine l'icône affichée sur le site)"
    )
    label = models.CharField(
        'Libellé',
        max_length=100,
        blank=True,
        help_text='Nom affiché (laisser vide pour utiliser le nom du réseau)'
    )
    url = models.URLField(
        'URL',
        help_text='Ex: https://facebook.com/geniesdafriquemedia'
    )
    is_active = models.BooleanField(
        'Actif',
        default=True,
        help_text='Décocher pour masquer ce réseau sur le site'
    )
    order = models.PositiveIntegerField(
        "Ordre d'affichage",
        default=0,
        help_text='0 = en premier'
    )

    class Meta:
        verbose_name = 'Réseau Social'
        verbose_name_plural = 'Réseaux Sociaux'
        ordering = ['order', 'network']

    def __str__(self):
        return self.label or self.get_network_display()
