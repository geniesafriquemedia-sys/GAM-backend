"""
Engagement Serializers - Sérialiseurs pour l'engagement
"""

from rest_framework import serializers
from .models import NewsletterSubscription, ContactMessage


class NewsletterSubscribeSerializer(serializers.Serializer):
    """Serializer pour l'inscription newsletter (US-10)."""

    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    source = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_email(self, value):
        """Normalise l'email."""
        return value.lower().strip()


class NewsletterUnsubscribeSerializer(serializers.Serializer):
    """Serializer pour le désabonnement newsletter."""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Vérifie que l'email existe et normalise."""
        email = value.lower().strip()
        if not NewsletterSubscription.objects.filter(email=email).exists():
            raise serializers.ValidationError('Cette adresse email n\'est pas inscrite.')
        return email


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer pour l'administration des inscriptions."""

    class Meta:
        model = NewsletterSubscription
        fields = [
            'id', 'email', 'status', 'source', 'ip_address',
            'external_id', 'synced_at', 'sync_error',
            'confirmed_at', 'unsubscribed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'synced_at']


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de message de contact."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

    def validate_message(self, value):
        """Vérifie la longueur minimale du message."""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                'Le message doit contenir au moins 10 caractères.'
            )
        return value


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer complet pour les messages de contact."""

    replied_by_name = serializers.CharField(
        source='replied_by.get_full_name',
        read_only=True
    )

    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'subject', 'message',
            'status', 'ip_address', 'replied_at', 'replied_by',
            'replied_by_name', 'created_at'
        ]
        read_only_fields = [
            'id', 'ip_address', 'replied_at', 'replied_by', 'created_at'
        ]
