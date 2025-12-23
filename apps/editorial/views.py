"""
Editorial Views - Vues pour le contenu éditorial
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.core.permissions import IsEditorOrReadOnly, CanPublish
from apps.core.mixins import MultiSerializerViewSetMixin
from .models import Author, Category, Article, Video
from .serializers import (
    AuthorListSerializer, AuthorDetailSerializer, AuthorCreateUpdateSerializer,
    CategoryListSerializer, CategoryDetailSerializer, CategoryCreateUpdateSerializer,
    ArticleListSerializer, ArticleDetailSerializer, ArticleCreateUpdateSerializer, ArticleAdminSerializer,
    VideoListSerializer, VideoDetailSerializer, VideoCreateUpdateSerializer, VideoAdminSerializer,
)
from .filters import ArticleFilter, VideoFilter


# =============================================================================
# AUTHOR VIEWS
# =============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Authors']),
    retrieve=extend_schema(tags=['Authors']),
    create=extend_schema(tags=['Authors']),
    update=extend_schema(tags=['Authors']),
    partial_update=extend_schema(tags=['Authors']),
    destroy=extend_schema(tags=['Authors']),
)
class AuthorViewSet(MultiSerializerViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des auteurs (US-01).
    """
    queryset = Author.objects.filter(is_active=True)
    permission_classes = [IsEditorOrReadOnly]
    lookup_field = 'slug'
    filterset_fields = ['is_active']
    search_fields = ['name', 'bio']
    ordering_fields = ['name', 'created_at']

    serializer_class = AuthorListSerializer
    serializer_action_classes = {
        'list': AuthorListSerializer,
        'retrieve': AuthorDetailSerializer,
        'create': AuthorCreateUpdateSerializer,
        'update': AuthorCreateUpdateSerializer,
        'partial_update': AuthorCreateUpdateSerializer,
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        # Admins voient tous les auteurs
        if self.request.user.is_authenticated and self.request.user.is_staff:
            queryset = Author.objects.all()
        # Annoter le count des articles pour éviter N+1
        return queryset.annotate(
            _articles_count=Count('articles', filter=Q(articles__status='published'))
        )

    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        """Liste des articles d'un auteur."""
        author = self.get_object()
        articles = author.articles.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author', 'category')
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)


# =============================================================================
# CATEGORY VIEWS
# =============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Categories']),
    retrieve=extend_schema(tags=['Categories']),
    create=extend_schema(tags=['Categories']),
    update=extend_schema(tags=['Categories']),
    partial_update=extend_schema(tags=['Categories']),
    destroy=extend_schema(tags=['Categories']),
)
class CategoryViewSet(MultiSerializerViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des catégories (US-01).
    """
    queryset = Category.objects.filter(is_active=True, parent__isnull=True)
    permission_classes = [IsEditorOrReadOnly]
    lookup_field = 'slug'
    filterset_fields = ['is_active', 'is_featured', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order', 'created_at']

    serializer_class = CategoryListSerializer
    serializer_action_classes = {
        'list': CategoryListSerializer,
        'retrieve': CategoryDetailSerializer,
        'create': CategoryCreateUpdateSerializer,
        'update': CategoryCreateUpdateSerializer,
        'partial_update': CategoryCreateUpdateSerializer,
    }

    def get_queryset(self):
        queryset = Category.objects.filter(is_active=True)
        # Filtrer par parent si spécifié
        parent = self.request.query_params.get('parent', None)
        if parent:
            queryset = queryset.filter(parent_id=parent)
        elif self.action == 'list':
            # Par défaut, ne montrer que les catégories racines
            queryset = queryset.filter(parent__isnull=True)
        # Annoter les counts pour éviter N+1
        return queryset.annotate(
            _articles_count=Count('articles', filter=Q(articles__status='published')),
            _videos_count=Count('videos', filter=Q(videos__status='published'))
        ).prefetch_related('children')

    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        """Liste des articles d'une catégorie."""
        category = self.get_object()
        articles = category.articles.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author', 'category')
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def videos(self, request, pk=None):
        """Liste des vidéos d'une catégorie."""
        category = self.get_object()
        videos = category.videos.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('category')
        serializer = VideoListSerializer(videos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Liste des catégories en vedette."""
        categories = self.get_queryset().filter(is_featured=True)
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data)


# =============================================================================
# ARTICLE VIEWS
# =============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Articles']),
    retrieve=extend_schema(tags=['Articles']),
    create=extend_schema(tags=['Articles']),
    update=extend_schema(tags=['Articles']),
    partial_update=extend_schema(tags=['Articles']),
    destroy=extend_schema(tags=['Articles']),
)
class ArticleViewSet(MultiSerializerViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des articles (US-02, US-04, US-05, US-06).
    """
    queryset = Article.objects.select_related('author', 'category')
    permission_classes = [IsEditorOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ArticleFilter
    search_fields = ['title', 'excerpt', 'content', 'tags']
    ordering_fields = ['published_at', 'created_at', 'views_count', 'reading_time']

    serializer_class = ArticleListSerializer
    serializer_action_classes = {
        'list': ArticleListSerializer,
        'retrieve': ArticleDetailSerializer,
        'create': ArticleCreateUpdateSerializer,
        'update': ArticleCreateUpdateSerializer,
        'partial_update': ArticleCreateUpdateSerializer,
    }

    def get_queryset(self):
        queryset = super().get_queryset()

        # Les visiteurs ne voient que les articles publiés
        if not self.request.user.is_authenticated or not self.request.user.is_editor:
            queryset = queryset.filter(
                status='published'
            ).filter(
                Q(published_at__isnull=True) | Q(published_at__lte=timezone.now())
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Incrémenter les vues pour les visiteurs
        if not request.user.is_authenticated or not request.user.is_editor:
            instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Articles à la Une (US-05)."""
        articles = self.get_queryset().filter(is_featured=True)[:3]
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Articles tendance."""
        articles = self.get_queryset().filter(is_trending=True)[:6]
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Articles récents."""
        articles = self.get_queryset().order_by('-published_at')[:10]
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[CanPublish])
    def publish(self, request, pk=None):
        """Publier un article (US-04)."""
        article = self.get_object()
        article.status = 'published'
        if not article.published_at:
            article.published_at = timezone.now()
        article.save()
        return Response({'message': 'Article publié'})

    @action(detail=True, methods=['post'], permission_classes=[CanPublish])
    def unpublish(self, request, pk=None):
        """Dépublier un article."""
        article = self.get_object()
        article.status = 'draft'
        article.save()
        return Response({'message': 'Article dépublié'})


# =============================================================================
# VIDEO VIEWS
# =============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Videos']),
    retrieve=extend_schema(tags=['Videos']),
    create=extend_schema(tags=['Videos']),
    update=extend_schema(tags=['Videos']),
    partial_update=extend_schema(tags=['Videos']),
    destroy=extend_schema(tags=['Videos']),
)
class VideoViewSet(MultiSerializerViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des vidéos Web TV (US-03, US-07).
    """
    queryset = Video.objects.select_related('category')
    permission_classes = [IsEditorOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_class = VideoFilter
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['published_at', 'created_at', 'views_count', 'duration']

    serializer_class = VideoListSerializer
    serializer_action_classes = {
        'list': VideoListSerializer,
        'retrieve': VideoDetailSerializer,
        'create': VideoCreateUpdateSerializer,
        'update': VideoCreateUpdateSerializer,
        'partial_update': VideoCreateUpdateSerializer,
    }

    def get_queryset(self):
        queryset = super().get_queryset()

        # Les visiteurs ne voient que les vidéos publiées
        if not self.request.user.is_authenticated or not self.request.user.is_editor:
            queryset = queryset.filter(
                status='published'
            ).filter(
                Q(published_at__isnull=True) | Q(published_at__lte=timezone.now())
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Incrémenter les vues pour les visiteurs
        if not request.user.is_authenticated or not request.user.is_editor:
            instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Vidéos en vedette (US-03)."""
        videos = self.get_queryset().filter(is_featured=True)[:4]
        serializer = VideoListSerializer(videos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def live(self, request):
        """Vidéos en direct."""
        videos = self.get_queryset().filter(is_live=True)
        serializer = VideoListSerializer(videos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Vidéos groupées par type (US-07)."""
        video_type = request.query_params.get('type', None)
        if video_type:
            videos = self.get_queryset().filter(video_type=video_type)
        else:
            videos = self.get_queryset()
        serializer = VideoListSerializer(videos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[CanPublish])
    def publish(self, request, pk=None):
        """Publier une vidéo."""
        video = self.get_object()
        video.status = 'published'
        if not video.published_at:
            video.published_at = timezone.now()
        video.save()
        return Response({'message': 'Vidéo publiée'})

    @action(detail=True, methods=['post'], permission_classes=[CanPublish])
    def unpublish(self, request, pk=None):
        """Dépublier une vidéo."""
        video = self.get_object()
        video.status = 'draft'
        video.save()
        return Response({'message': 'Vidéo dépubliée'})


# =============================================================================
# HOMEPAGE VIEW
# =============================================================================

@extend_schema(tags=['Homepage'])
class HomepageView(viewsets.ViewSet):
    """
    Vue pour la page d'accueil (US-05).
    Retourne toutes les données nécessaires en une seule requête.
    Cache de 5 minutes pour améliorer les performances.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    @method_decorator(cache_page(60 * 5))  # Cache 5 minutes
    def list(self, request):
        now = timezone.now()
        published_filter = Q(status='published') & (
            Q(published_at__isnull=True) | Q(published_at__lte=now)
        )

        # Articles à la Une - avec annotations pour éviter N+1
        featured_articles = Article.objects.filter(
            published_filter, is_featured=True
        ).select_related('author', 'category').only(
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'reading_time', 'is_featured', 'is_trending', 'published_at',
            'author__id', 'author__name', 'author__slug', 'author__photo',
            'category__id', 'category__name', 'category__slug', 'category__color'
        )[:3]

        # Articles récents
        recent_articles = Article.objects.filter(
            published_filter
        ).select_related('author', 'category').only(
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'reading_time', 'is_featured', 'is_trending', 'published_at',
            'author__id', 'author__name', 'author__slug', 'author__photo',
            'category__id', 'category__name', 'category__slug', 'category__color'
        ).order_by('-published_at')[:8]

        # Articles tendance
        trending_articles = Article.objects.filter(
            published_filter, is_trending=True
        ).select_related('author', 'category').only(
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'reading_time', 'is_featured', 'is_trending', 'published_at',
            'author__id', 'author__name', 'author__slug', 'author__photo',
            'category__id', 'category__name', 'category__slug', 'category__color'
        )[:6]

        # Vidéos en vedette
        featured_videos = Video.objects.filter(
            published_filter, is_featured=True
        ).select_related('category').only(
            'id', 'title', 'slug', 'description', 'youtube_id', 'thumbnail',
            'video_type', 'duration', 'is_featured', 'is_live', 'published_at',
            'category__id', 'category__name', 'category__slug', 'category__color'
        )[:4]

        # Catégories en vedette avec count annoté
        featured_categories = Category.objects.filter(
            is_active=True, is_featured=True
        ).annotate(
            _articles_count=Count('articles', filter=Q(articles__status='published')),
            _videos_count=Count('videos', filter=Q(videos__status='published'))
        )[:6]

        return Response({
            'featured_articles': ArticleListSerializer(featured_articles, many=True).data,
            'recent_articles': ArticleListSerializer(recent_articles, many=True).data,
            'trending_articles': ArticleListSerializer(trending_articles, many=True).data,
            'featured_videos': VideoListSerializer(featured_videos, many=True).data,
            'featured_categories': CategoryListSerializer(featured_categories, many=True).data,
        })
