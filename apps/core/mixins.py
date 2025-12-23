"""
Core Mixins - Mixins réutilisables pour les vues et serializers
"""

from rest_framework import status
from rest_framework.response import Response


class MultiSerializerViewSetMixin:
    """
    Mixin permettant d'utiliser différents serializers selon l'action.

    Usage:
        class ArticleViewSet(MultiSerializerViewSetMixin, viewsets.ModelViewSet):
            serializer_class = ArticleSerializer
            serializer_action_classes = {
                'list': ArticleListSerializer,
                'create': ArticleCreateSerializer,
                'retrieve': ArticleDetailSerializer,
            }
    """
    serializer_action_classes = {}

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()


class PublishedQuerySetMixin:
    """
    Mixin pour filtrer les contenus publiés pour les utilisateurs anonymes.
    Les admins/éditeurs voient tous les contenus.
    """
    def get_queryset(self):
        queryset = super().get_queryset()

        # Les admins et éditeurs voient tout
        if self.request.user.is_authenticated:
            if self.request.user.is_staff or getattr(self.request.user, 'is_editor', False):
                return queryset

        # Les autres ne voient que les contenus publiés
        from django.utils import timezone

        return queryset.filter(
            status='published',
        ).filter(
            models.Q(published_at__isnull=True) |
            models.Q(published_at__lte=timezone.now())
        )


class CacheResponseMixin:
    """
    Mixin pour mettre en cache les réponses API.
    """
    cache_timeout = 60 * 15  # 15 minutes par défaut

    def get_cache_key(self, request):
        """Génère une clé de cache unique."""
        return f"{self.__class__.__name__}:{request.get_full_path()}"

    def dispatch(self, request, *args, **kwargs):
        from django.core.cache import cache

        # Ne pas cacher les requêtes authentifiées ou non-GET
        if request.method != 'GET' or request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        cache_key = self.get_cache_key(request)
        cached_response = cache.get(cache_key)

        if cached_response:
            return Response(cached_response)

        response = super().dispatch(request, *args, **kwargs)

        if response.status_code == 200:
            cache.set(cache_key, response.data, self.cache_timeout)

        return response


class BulkActionMixin:
    """
    Mixin pour les actions en masse (bulk actions).
    """
    def bulk_destroy(self, request, *args, **kwargs):
        """Suppression en masse."""
        ids = request.data.get('ids', [])

        if not ids:
            return Response(
                {'error': 'Aucun ID fourni'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.filter_queryset(self.get_queryset())
        deleted_count = queryset.filter(pk__in=ids).delete()[0]

        return Response(
            {'deleted': deleted_count},
            status=status.HTTP_200_OK
        )

    def bulk_update_status(self, request, *args, **kwargs):
        """Mise à jour du statut en masse."""
        ids = request.data.get('ids', [])
        new_status = request.data.get('status')

        if not ids or not new_status:
            return Response(
                {'error': 'IDs et statut requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.filter_queryset(self.get_queryset())
        updated_count = queryset.filter(pk__in=ids).update(status=new_status)

        return Response(
            {'updated': updated_count},
            status=status.HTTP_200_OK
        )


class NestedWriteSerializerMixin:
    """
    Mixin pour gérer l'écriture des relations imbriquées dans les serializers.
    """
    def create(self, validated_data):
        nested_data = {}

        # Extraire les données imbriquées
        for field_name, field in self.fields.items():
            if hasattr(field, 'many') and field_name in validated_data:
                nested_data[field_name] = validated_data.pop(field_name)

        # Créer l'instance principale
        instance = super().create(validated_data)

        # Créer les instances imbriquées
        for field_name, data_list in nested_data.items():
            field = self.fields[field_name]
            related_model = field.child.Meta.model
            for data in data_list:
                data[self.get_nested_foreign_key(field_name)] = instance
                related_model.objects.create(**data)

        return instance

    def get_nested_foreign_key(self, field_name):
        """Retourne le nom de la clé étrangère pour un champ imbriqué."""
        # Par défaut, utilise le nom du modèle parent en snake_case
        return self.Meta.model.__name__.lower()
