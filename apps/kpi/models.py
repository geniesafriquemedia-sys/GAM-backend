"""
KPI Models - Indicateurs de Performance Clés
"""

from django.db import models
from django.core.exceptions import ValidationError


class PlatformKPI(models.Model):
    """
    Modèle singleton pour stocker les KPI de la plateforme.
    Un seul enregistrement actif à la fois.
    """
    
    # Métriques éditoriales
    total_articles = models.PositiveIntegerField(
        'Total Articles Publiés',
        default=0,
        help_text='Nombre total d\'articles publiés'
    )
    total_videos = models.PositiveIntegerField(
        'Total Vidéos Publiées',
        default=0,
        help_text='Nombre total de vidéos publiées'
    )
    
    # Métriques d'audience
    monthly_readers = models.PositiveIntegerField(
        'Lecteurs Mensuels',
        default=0,
        help_text='Nombre de lecteurs uniques par mois'
    )
    total_views = models.PositiveIntegerField(
        'Vues Totales',
        default=0,
        help_text='Nombre total de vues de contenu'
    )
    
    # Métriques géographiques
    countries_covered = models.PositiveIntegerField(
        'Pays Couverts',
        default=0,
        help_text='Nombre de pays africains couverts'
    )
    
    # Métriques équipe
    tv_experts = models.PositiveIntegerField(
        'Experts TV',
        default=0,
        help_text='Nombre d\'experts et contributeurs TV'
    )
    total_authors = models.PositiveIntegerField(
        'Total Auteurs',
        default=0,
        help_text='Nombre total d\'auteurs actifs'
    )
    
    # Métadonnées
    last_updated = models.DateTimeField(
        'Dernière Mise à Jour',
        auto_now=True
    )
    is_active = models.BooleanField(
        'Actif',
        default=True,
        help_text='Seul un enregistrement peut être actif'
    )
    
    class Meta:
        verbose_name = "KPI Plateforme"
        verbose_name_plural = "KPIs Plateforme"
        ordering = ['-last_updated']
    
    def __str__(self):
        return f"KPI Plateforme - {self.last_updated.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        """Assure qu'un seul enregistrement est actif"""
        if self.is_active:
            # Désactiver tous les autres enregistrements
            PlatformKPI.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    def update_from_database(self):
        """
        Calcule automatiquement les KPIs depuis les données réelles.
        Appelé manuellement ou via une tâche planifiée.
        """
        from apps.editorial.models import Article, Video, Author
        
        # Compter les articles publiés
        self.total_articles = Article.objects.filter(
            status='published'
        ).count()
        
        # Compter les vidéos publiées
        self.total_videos = Video.objects.filter(
            status='published'
        ).count()
        
        # Compter les auteurs actifs
        self.total_authors = Author.objects.filter(
            is_active=True
        ).count()
        
        # Les experts TV sont les auteurs actifs pour l'instant
        self.tv_experts = self.total_authors

        # Calculer les pays couverts via les tags
        from apps.core.constants import AFRICAN_COUNTRIES
        
        # Récupérer tous les tags uniques des articles publiés
        article_tags = set()
        for article in Article.objects.filter(status='published').only('tags'):
            if article.tags:
                tags = [t.strip().lower() for t in article.tags.split(',')]
                article_tags.update(tags)
        
        # Récupérer tous les tags uniques des vidéos publiées
        video_tags = set()
        for video in Video.objects.filter(status='published').only('tags'):
            if video.tags:
                tags = [t.strip().lower() for t in video.tags.split(',')]
                video_tags.update(tags)
                
        # Fusionner tous les tags
        all_tags = article_tags.union(video_tags)
        
        # Compter les pays trouvés
        found_countries = set()
        for tag in all_tags:
            if tag in AFRICAN_COUNTRIES:
                found_countries.add(tag)
                
        # Mettre à jour le KPI
        # Si aucun pays détecté (cas initial), on garde la valeur par défaut ou 0 selon la logique métier
        # Ici on met le nombre réel trouvé
        self.countries_covered = len(found_countries)
        
        self.save()
        
        return self
    
    @classmethod
    def get_active(cls):
        """Retourne l'instance active ou en crée une"""
        kpi = cls.objects.filter(is_active=True).first()
        if not kpi:
            kpi = cls.objects.create()
            kpi.update_from_database()
        return kpi
