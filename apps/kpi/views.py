"""
KPI Views
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import PlatformKPI
from .serializers import PlatformKPISerializer


class PlatformKPIView(APIView):
    """
    Endpoint pour récupérer les KPI de la plateforme.
    Accessible publiquement (pas d'authentification requise).
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Récupérer les KPI de la plateforme",
        description="Retourne les indicateurs de performance clés de GAM (articles, vidéos, audience, etc.)",
        responses={
            200: OpenApiResponse(
                response=PlatformKPISerializer,
                description="KPI de la plateforme"
            ),
        },
        tags=['KPI']
    )
    def get(self, request):
        """Retourne les KPI actifs de la plateforme"""
        kpi = PlatformKPI.get_active()
        serializer = PlatformKPISerializer(kpi)
        return Response(serializer.data)
