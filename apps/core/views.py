"""
Core Views - Endpoints publics pour les paramètres du site
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from .models import SocialNetwork
from .serializers import SocialNetworkSerializer


class SocialNetworkListView(APIView):
    """
    GET /api/v1/core/social-networks/
    Retourne les réseaux sociaux actifs, triés par ordre d'affichage.
    Aucune authentification requise (endpoint public).
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Site Settings'],
        responses={200: SocialNetworkSerializer(many=True)},
        summary='Liste des réseaux sociaux actifs',
    )
    def get(self, request):
        networks = SocialNetwork.objects.filter(is_active=True)
        serializer = SocialNetworkSerializer(networks, many=True)
        return Response(serializer.data)
