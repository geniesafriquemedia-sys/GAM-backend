"""
KPI Signals - Automatisation des mises à jour
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.editorial.models import Article, Video, Author
from .models import PlatformKPI

@receiver(post_save, sender=Article)
@receiver(post_delete, sender=Article)
@receiver(post_save, sender=Video)
@receiver(post_delete, sender=Video)
@receiver(post_save, sender=Author)
@receiver(post_delete, sender=Author)
def auto_update_kpi(sender, instance, **kwargs):
    """
    Déclenche le recalcul des KPIs à chaque mofidication 
    d'un Article, Vidéo ou Auteur.
    """
    # On met à jour uniquement si c'est un changement de statut/publication
    # Pour simplifier, on recalcule à chaque sauvegarde pour l'instant
    # Idéalement, on pourrait le faire en tâche asynchrone (Celery) plus tard
    
    kpi = PlatformKPI.get_active()
    kpi.update_from_database()
