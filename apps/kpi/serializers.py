"""
KPI Serializers
"""

from rest_framework import serializers
from .models import PlatformKPI


class PlatformKPISerializer(serializers.ModelSerializer):
    """Serializer pour les KPI de la plateforme"""
    
    class Meta:
        model = PlatformKPI
        fields = [
            'total_articles',
            'total_videos',
            'monthly_readers',
            'total_views',
            'countries_covered',
            'tv_experts',
            'total_authors',
            'last_updated',
        ]
        read_only_fields = fields
