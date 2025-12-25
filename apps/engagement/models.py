"""
Engagement Models - Modèles pour l'engagement utilisateur
Newsletter (US-10)
"""

from django.db import models
from apps.core.models import TimeStampedModel


class NewsletterSubscription(TimeStampedModel):
    """
    Modèle pour les inscriptions à la newsletter (US-10).
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        CONFIRMED = 'confirmed', 'Confirmé'
        UNSUBSCRIBED = 'unsubscribed', 'Désabonné'

    email = models.EmailField(
        'Email',
        unique=True,
        db_index=True
    )
    status = models.CharField(
        'Statut',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    ip_address = models.GenericIPAddressField(
        'Adresse IP',
        null=True,
        blank=True
    )
    source = models.CharField(
        'Source',
        max_length=100,
        blank=True,
        help_text='Page ou formulaire d\'origine'
    )

    # Synchronisation avec le provider externe
    external_id = models.CharField(
        'ID externe',
        max_length=100,
        blank=True,
        help_text='ID dans Brevo/Mailchimp'
    )
    synced_at = models.DateTimeField(
        'Dernière synchronisation',
        null=True,
        blank=True
    )
    sync_error = models.TextField(
        'Erreur de synchronisation',
        blank=True
    )

    # Dates
    confirmed_at = models.DateTimeField(
        'Date de confirmation',
        null=True,
        blank=True
    )
    unsubscribed_at = models.DateTimeField(
        'Date de désabonnement',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Inscription newsletter'
        verbose_name_plural = 'Inscriptions newsletter'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} ({self.get_status_display()})'

    def confirm(self):
        """Confirme l'inscription."""
        from django.utils import timezone
        self.status = self.Status.CONFIRMED
        self.confirmed_at = timezone.now()
        self.save(update_fields=['status', 'confirmed_at'])

    def unsubscribe(self):
        """Désabonne l'utilisateur."""
        from django.utils import timezone
        self.status = self.Status.UNSUBSCRIBED
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['status', 'unsubscribed_at'])


class ContactMessage(TimeStampedModel):
    """
    Modèle pour les messages de contact.
    """

    class Status(models.TextChoices):
        NEW = 'new', 'Nouveau'
        READ = 'read', 'Lu'
        REPLIED = 'replied', 'Répondu'
        ARCHIVED = 'archived', 'Archivé'

    name = models.CharField(
        'Nom',
        max_length=100
    )
    email = models.EmailField(
        'Email'
    )
    subject = models.CharField(
        'Sujet',
        max_length=200
    )
    message = models.TextField(
        'Message'
    )
    status = models.CharField(
        'Statut',
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )
    ip_address = models.GenericIPAddressField(
        'Adresse IP',
        null=True,
        blank=True
    )

    # Réponse
    replied_at = models.DateTimeField(
        'Date de réponse',
        null=True,
        blank=True
    )
    replied_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_replies',
        verbose_name='Répondu par'
    )

    class Meta:
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name}: {self.subject}'

    def mark_as_read(self):
        """Marque le message comme lu."""
        if self.status == self.Status.NEW:
            self.status = self.Status.READ
            self.save(update_fields=['status'])

    def mark_as_replied(self, user):
        """Marque le message comme répondu."""
        from django.utils import timezone
        self.status = self.Status.REPLIED
        self.replied_at = timezone.now()
        self.replied_by = user
        self.save(update_fields=['status', 'replied_at', 'replied_by'])


class ContentNotificationStatus(models.TextChoices):
    """Statuts partagés pour les notifications de contenu."""
    PENDING = 'pending', 'En attente'
    SENT = 'sent', 'Envoyé'
    FAILED = 'failed', 'Échoué'


class ArticleNotification(TimeStampedModel):
    """
    Modèle pour tracker les notifications d'articles envoyées.
    Évite les doublons et permet le suivi des campagnes.
    """

    article_id = models.PositiveBigIntegerField(
        'ID Article',
        unique=True,
        db_index=True,
        help_text='ID de l\'article notifié'
    )
    campaign_id = models.CharField(
        'ID Campagne',
        max_length=100,
        blank=True,
        help_text='ID de la campagne Brevo'
    )
    status = models.CharField(
        'Statut',
        max_length=20,
        choices=ContentNotificationStatus.choices,
        default=ContentNotificationStatus.PENDING
    )
    error_message = models.TextField(
        'Message d\'erreur',
        blank=True
    )
    sent_at = models.DateTimeField(
        'Date d\'envoi',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Notification article'
        verbose_name_plural = 'Notifications articles'
        ordering = ['-sent_at']

    def __str__(self):
        return f'Notification article {self.article_id} ({self.get_status_display()})'


class VideoNotification(TimeStampedModel):
    """
    Modèle pour tracker les notifications de vidéos envoyées.
    Évite les doublons et permet le suivi des campagnes.
    """

    video_id = models.PositiveBigIntegerField(
        'ID Vidéo',
        unique=True,
        db_index=True,
        help_text='ID de la vidéo notifiée'
    )
    campaign_id = models.CharField(
        'ID Campagne',
        max_length=100,
        blank=True,
        help_text='ID de la campagne Brevo'
    )
    status = models.CharField(
        'Statut',
        max_length=20,
        choices=ContentNotificationStatus.choices,
        default=ContentNotificationStatus.PENDING
    )
    error_message = models.TextField(
        'Message d\'erreur',
        blank=True
    )
    sent_at = models.DateTimeField(
        'Date d\'envoi',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Notification vidéo'
        verbose_name_plural = 'Notifications vidéos'
        ordering = ['-sent_at']

    def __str__(self):
        return f'Notification vidéo {self.video_id} ({self.get_status_display()})'
