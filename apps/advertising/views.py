"""
Advertising Views - API publicitaire GAM
"""

from datetime import date
from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Advertisement
from .serializers import AdvertisementPublicSerializer, AdvertisementAdminSerializer


class ActiveAdsView(APIView):
    """
    GET /api/v1/advertising/active/
    Retourne les publicités actives, optionnellement filtrées par position.
    Aucune authentification requise (endpoint public).
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Advertising'],
        parameters=[
            OpenApiParameter(
                name='position',
                description='Filtrer par position (ex: HOMEPAGE_TOP)',
                required=False,
                type=str,
            )
        ],
        responses={200: AdvertisementPublicSerializer(many=True)},
    )
    def get(self, request):
        today = date.today()
        queryset = Advertisement.objects.filter(
            is_active=True,
            status=Advertisement.Status.ACTIVE,
            start_date__lte=today,
            end_date__gte=today,
        )

        position = request.query_params.get('position')
        if position:
            queryset = queryset.filter(position=position)

        serializer = AdvertisementPublicSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)


class TrackAdView(APIView):
    """
    POST /api/v1/advertising/track/
    Enregistre une impression ou un clic sur une publicité.

    Body: {"ad_id": 1, "event": "impression"} ou {"ad_id": 1, "event": "click"}
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Advertising'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'ad_id': {'type': 'integer'},
                    'event': {'type': 'string', 'enum': ['impression', 'click']},
                },
                'required': ['ad_id', 'event'],
            }
        },
        responses={200: {'type': 'object', 'properties': {'status': {'type': 'string'}}}},
    )
    def post(self, request):
        ad_id = request.data.get('ad_id')
        event = request.data.get('event')

        if not ad_id or event not in ('impression', 'click'):
            return Response(
                {'error': 'Paramètres invalides. Attendu: ad_id (int) et event (impression|click)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ad = Advertisement.objects.get(pk=ad_id)
        except Advertisement.DoesNotExist:
            return Response({'error': 'Publicité introuvable'}, status=status.HTTP_404_NOT_FOUND)

        if event == 'impression':
            ad.increment_impressions()
        else:
            ad.increment_clicks()

        return Response({'status': 'ok'})


class AdvertisementAdminViewSet(viewsets.ModelViewSet):
    """
    CRUD complet pour les administrateurs.
    GET/POST /api/v1/advertising/admin/
    GET/PUT/PATCH/DELETE /api/v1/advertising/admin/{id}/
    """
    queryset = Advertisement.objects.all().order_by('-created_at')
    serializer_class = AdvertisementAdminSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(tags=['Advertising Admin'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=['Advertising Admin'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(tags=['Advertising Admin'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(tags=['Advertising Admin'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(tags=['Advertising Admin'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(tags=['Advertising Admin'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
