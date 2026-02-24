"""
Advertising Models - Gestion des publicités GAM
"""

from datetime import date
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel
from apps.core.models import TimeStampedModel


class Advertisement(TimeStampedModel):
    """
    Modèle pour les publicités diffusées sur le site GAM.
    Gestion complète : planification, placement, suivi des performances.
    """

    class AdType(models.TextChoices):
        LEADERBOARD = 'LEADERBOARD', 'Leaderboard (970x90)'
        BANNER = 'BANNER', 'Banner (728x90)'
        SIDEBAR = 'SIDEBAR', 'Sidebar (300x250)'
        NATIVE = 'NATIVE', 'Native (inline article)'
        IN_ARTICLE = 'IN_ARTICLE', 'In-Article'
        INTERSTITIEL = 'INTERSTITIEL', 'Interstitiel'

    class Position(models.TextChoices):
        HOMEPAGE_TOP = 'HOMEPAGE_TOP', 'Homepage – Haut'
        HOMEPAGE_MID = 'HOMEPAGE_MID', 'Homepage – Milieu'
        ARTICLE_SIDEBAR = 'ARTICLE_SIDEBAR', 'Article – Sidebar'
        ARTICLE_IN_BODY_1 = 'ARTICLE_IN_BODY_1', 'Article – Dans le corps 1'
        ARTICLE_IN_BODY_2 = 'ARTICLE_IN_BODY_2', 'Article – Dans le corps 2'
        CATEGORIES_TOP = 'CATEGORIES_TOP', 'Page Catégories – Haut'
        WEBTV_TOP = 'WEBTV_TOP', 'Web TV – Haut'
        FOOTER_BANNER = 'FOOTER_BANNER', 'Footer – Bannière'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Brouillon'
        ACTIVE = 'ACTIVE', 'Active'
        PAUSED = 'PAUSED', 'En pause'
        EXPIRED = 'EXPIRED', 'Expirée'

    # ── Identification ────────────────────────────────────────────────────────
    title = models.CharField(
        'Nom interne',
        max_length=255,
        help_text='Nom interne pour identifier la campagne (non visible sur le site)'
    )
    advertiser_name = models.CharField('Nom du client', max_length=255)
    advertiser_email = models.EmailField('Email du client')
    advertiser_phone = models.CharField('Téléphone', max_length=50, blank=True)
    notes = models.TextField('Notes admin', blank=True)

    # ── Contenu ───────────────────────────────────────────────────────────────
    image = models.ImageField(
        'Image publicitaire',
        upload_to='advertising/',
        help_text='Dimensions recommandées selon le type (Leaderboard: 970x90, Sidebar: 300x250, etc.)'
    )
    external_url = models.URLField('URL de destination (clic)', max_length=500)
    alt_text = models.CharField(
        'Texte alternatif',
        max_length=255,
        blank=True,
        help_text='Texte alternatif pour l\'accessibilité'
    )

    # ── Placement ─────────────────────────────────────────────────────────────
    ad_type = models.CharField(
        'Type de publicité',
        max_length=20,
        choices=AdType.choices,
        default=AdType.BANNER
    )
    position = models.CharField(
        'Position',
        max_length=30,
        choices=Position.choices,
        default=Position.HOMEPAGE_TOP
    )

    # ── Planification ─────────────────────────────────────────────────────────
    start_date = models.DateField('Date de début')
    end_date = models.DateField('Date de fin')
    is_active = models.BooleanField('Activée', default=True)
    status = models.CharField(
        'Statut',
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )

    # ── Suivi des performances ────────────────────────────────────────────────
    impressions_count = models.PositiveIntegerField(
        'Impressions',
        default=0,
        editable=False
    )
    clicks_count = models.PositiveIntegerField(
        'Clics',
        default=0,
        editable=False
    )

    # ── Tarification ──────────────────────────────────────────────────────────
    price_per_month = models.DecimalField(
        'Prix mensuel (€)',
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text='Informationnel uniquement – facturation manuelle'
    )

    # ── Wagtail panels ────────────────────────────────────────────────────────
    panels = [
        MultiFieldPanel([
            FieldPanel('title'),
            FieldRowPanel([
                FieldPanel('advertiser_name'),
                FieldPanel('advertiser_email'),
            ]),
            FieldPanel('advertiser_phone'),
            FieldPanel('notes'),
        ], heading='Informations client'),
        MultiFieldPanel([
            FieldPanel('image'),
            FieldPanel('external_url'),
            FieldPanel('alt_text'),
        ], heading='Contenu publicitaire'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('ad_type'),
                FieldPanel('position'),
            ]),
        ], heading='Placement'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('start_date'),
                FieldPanel('end_date'),
            ]),
            FieldRowPanel([
                FieldPanel('status'),
                FieldPanel('is_active'),
            ]),
            FieldPanel('price_per_month'),
        ], heading='Planification & Tarification'),
    ]

    class Meta:
        verbose_name = 'Publicité'
        verbose_name_plural = 'Publicités'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['position', 'status', 'start_date', 'end_date']),
            models.Index(fields=['is_active', 'status']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"

    @property
    def ctr(self) -> float:
        """Click-Through Rate en pourcentage."""
        if self.impressions_count == 0:
            return 0.0
        return round(self.clicks_count / self.impressions_count * 100, 2)

    @property
    def is_currently_active(self) -> bool:
        """Vérifie si la pub est active aujourd'hui."""
        today = date.today()
        return (
            self.is_active
            and self.status == self.Status.ACTIVE
            and self.start_date <= today <= self.end_date
        )

    def increment_impressions(self):
        """Incrémente le compteur d'impressions de façon atomique."""
        Advertisement.objects.filter(pk=self.pk).update(
            impressions_count=models.F('impressions_count') + 1
        )

    def increment_clicks(self):
        """Incrémente le compteur de clics de façon atomique."""
        Advertisement.objects.filter(pk=self.pk).update(
            clicks_count=models.F('clicks_count') + 1
        )
