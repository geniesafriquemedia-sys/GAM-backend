"""
Advertising Serializers
"""

from rest_framework import serializers
from .models import Advertisement


class AdvertisementPublicSerializer(serializers.ModelSerializer):
    """
    Sérialiseur public : uniquement les champs visibles par les visiteurs.
    Pas d'infos client ni de prix.
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
            'id',
            'image_url',
            'external_url',
            'alt_text',
            'ad_type',
            'position',
        ]

    def get_image_url(self, obj) -> str:
        """Retourne l'URL absolue de l'image."""
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return ''


class AdvertisementAdminSerializer(serializers.ModelSerializer):
    """
    Sérialiseur admin : tous les champs + métriques calculées.
    """
    image_url = serializers.SerializerMethodField()
    ctr = serializers.FloatField(read_only=True)
    is_currently_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Advertisement
        fields = [
            'id',
            'title',
            'advertiser_name',
            'advertiser_email',
            'advertiser_phone',
            'notes',
            'image',
            'image_url',
            'external_url',
            'alt_text',
            'ad_type',
            'position',
            'start_date',
            'end_date',
            'is_active',
            'status',
            'impressions_count',
            'clicks_count',
            'ctr',
            'is_currently_active',
            'price_per_month',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['impressions_count', 'clicks_count', 'created_at', 'updated_at']

    def get_image_url(self, obj) -> str:
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return ''
