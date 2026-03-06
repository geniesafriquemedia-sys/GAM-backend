"""
Core Serializers
"""

from rest_framework import serializers
from .models import SocialNetwork


class SocialNetworkSerializer(serializers.ModelSerializer):
    """Sérialiseur public pour les réseaux sociaux."""

    display_label = serializers.SerializerMethodField()

    class Meta:
        model = SocialNetwork
        fields = ['id', 'network', 'display_label', 'url', 'order']

    def get_display_label(self, obj):
        return obj.label or obj.get_network_display()
