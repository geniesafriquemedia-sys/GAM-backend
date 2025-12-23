"""
Category Model - Gestion des catégories (US-01)
Wagtail Snippet pour interface unifiée
"""

from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from apps.core.models import TimeStampedModel, SluggedModel, OrderedModel
from apps.core.validators import validate_hex_color


# Note: Enregistré comme snippet via EditorialViewSetGroup dans wagtail_hooks.py
class Category(TimeStampedModel, SluggedModel, OrderedModel):
    """
    Modèle Catégorie pour organiser les contenus.
    US-01: Définition d'une couleur (code hexadécimal) pour chaque catégorie.
    """

    name = models.CharField(
        'Nom',
        max_length=100,
        unique=True,
        db_index=True
    )
    description = models.TextField(
        'Description',
        blank=True,
        help_text='Description de la catégorie'
    )
    color = models.CharField(
        'Couleur',
        max_length=7,
        default='#3B82F6',
        validators=[validate_hex_color],
        help_text='Code couleur hexadécimal (ex: #FF5733)'
    )
    icon = models.CharField(
        'Icône',
        max_length=50,
        blank=True,
        help_text='Nom de l\'icône (ex: globe, briefcase, cpu)'
    )
    image = models.ImageField(
        'Image',
        upload_to='categories/',
        blank=True,
        null=True,
        help_text='Image de couverture de la catégorie'
    )

    # Catégorie parente (pour hiérarchie)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Catégorie parente'
    )

    # Statut
    is_active = models.BooleanField(
        'Active',
        default=True,
        help_text='Les catégories inactives ne sont pas affichées'
    )
    is_featured = models.BooleanField(
        'En vedette',
        default=False,
        help_text='Afficher dans la section vedette de l\'accueil'
    )

    # Configuration du slug
    slug_source_field = 'name'

    # Wagtail Panels pour l'interface admin
    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('description'),
            FieldPanel('color'),
            FieldPanel('icon'),
            FieldPanel('image'),
        ], heading="Informations de la catégorie"),
        MultiFieldPanel([
            FieldPanel('parent'),
            FieldPanel('order'),
        ], heading="Hiérarchie"),
        MultiFieldPanel([
            FieldPanel('is_active'),
            FieldPanel('is_featured'),
        ], heading="Options"),
    ]

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['order', 'name']

    def __str__(self):
        if self.parent:
            return f'{self.parent.name} > {self.name}'
        return self.name

    @property
    def articles_count(self) -> int:
        """Nombre d'articles publiés dans cette catégorie."""
        return self.articles.filter(status='published').count()

    @property
    def videos_count(self) -> int:
        """Nombre de vidéos publiées dans cette catégorie."""
        return self.videos.filter(status='published').count()

    @property
    def total_content_count(self) -> int:
        """Nombre total de contenus dans cette catégorie."""
        return self.articles_count + self.videos_count

    def get_all_children(self):
        """Retourne toutes les sous-catégories (récursif)."""
        children = list(self.children.filter(is_active=True))
        for child in self.children.filter(is_active=True):
            children.extend(child.get_all_children())
        return children
