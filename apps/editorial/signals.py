"""
Editorial Signals - Signaux pour les opérations automatiques
"""

import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings

from apps.core.utils import calculate_reading_time, extract_youtube_id, get_youtube_thumbnail
from .models import Article, Video

logger = logging.getLogger(__name__)


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


@receiver(post_save, sender=Article)
def send_newsletter_on_publish(sender, instance, created, **kwargs):
    """
    Envoie une notification newsletter quand un article est publié.
    Déclenché uniquement quand le statut passe à 'published'.
    """
    from apps.core.models import PublishableModel

    # Vérifier si l'article est publié
    if instance.status != PublishableModel.PublicationStatus.PUBLISHED:
        return

    # Vérifier si les notifications sont activées
    if not getattr(settings, 'ENABLE_ARTICLE_NOTIFICATIONS', True):
        return

    # Importer ici pour éviter les imports circulaires
    from apps.engagement.services import send_article_notification

    try:
        # Envoyer la notification (la fonction vérifie les doublons)
        result = send_article_notification(instance)

        if result.get('already_sent'):
            logger.debug(f'Notification already sent for article: {instance.title}')
        elif result.get('success'):
            logger.info(f'Newsletter notification sent for article: {instance.title}')
        else:
            logger.warning(f'Failed to send notification for article: {instance.title}')

    except Exception as e:
        # Ne pas bloquer la sauvegarde de l'article en cas d'erreur
        logger.error(f'Error sending newsletter notification: {e}')


@receiver(post_save, sender=Video)
def send_newsletter_on_video_publish(sender, instance, created, **kwargs):
    """
    Envoie une notification newsletter quand une vidéo est publiée.
    Déclenché uniquement quand le statut passe à 'published'.
    """
    from apps.core.models import PublishableModel

    # Vérifier si la vidéo est publiée
    if instance.status != PublishableModel.PublicationStatus.PUBLISHED:
        return

    # Vérifier si les notifications sont activées
    if not getattr(settings, 'ENABLE_ARTICLE_NOTIFICATIONS', True):
        return

    # Importer ici pour éviter les imports circulaires
    from apps.engagement.services import send_video_notification

    try:
        # Envoyer la notification (la fonction vérifie les doublons)
        result = send_video_notification(instance)

        if result.get('already_sent'):
            logger.debug(f'Notification already sent for video: {instance.title}')
        elif result.get('success'):
            logger.info(f'Newsletter notification sent for video: {instance.title}')
        else:
            logger.warning(f'Failed to send notification for video: {instance.title}')

    except Exception as e:
        # Ne pas bloquer la sauvegarde de la vidéo en cas d'erreur
        logger.error(f'Error sending video newsletter notification: {e}')
