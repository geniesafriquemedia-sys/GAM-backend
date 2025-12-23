"""
Editorial Signals - Signaux pour les opérations automatiques
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.core.utils import calculate_reading_time, extract_youtube_id, get_youtube_thumbnail
from .models import Article, Video


@receiver(pre_save, sender=Article)
def update_article_reading_time(sender, instance, **kwargs):
    """
    Calcule automatiquement le temps de lecture avant la sauvegarde (US-02).
    """
    # Calculer le temps de lecture à partir du contenu
    content = instance.get_full_content() if instance.pk else instance.content
    instance.reading_time = calculate_reading_time(content)


@receiver(pre_save, sender=Video)
def update_video_youtube_data(sender, instance, **kwargs):
    """
    Extrait l'ID YouTube et la miniature automatiquement (US-03).
    """
    if instance.youtube_url:
        # Extraire l'ID YouTube
        video_id = extract_youtube_id(instance.youtube_url)
        if video_id:
            instance.youtube_id = video_id

            # Générer la miniature si pas déjà définie
            if not instance.youtube_thumbnail:
                instance.youtube_thumbnail = get_youtube_thumbnail(video_id)


@receiver(post_save, sender=Article)
def generate_article_excerpt(sender, instance, created, **kwargs):
    """
    Génère un extrait automatique si non défini.
    """
    if not instance.excerpt and instance.content:
        from apps.core.utils import generate_excerpt

        excerpt = generate_excerpt(instance.content, max_length=300)
        if excerpt:
            # Utiliser update pour éviter une boucle infinie
            Article.objects.filter(pk=instance.pk).update(excerpt=excerpt)
