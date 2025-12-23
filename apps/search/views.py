"""
Search Views - Vues pour la recherche de contenu (US-08)
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .services import SearchService, get_trending_tags, get_search_suggestions


class SearchResultsPagination(PageNumberPagination):
    """Pagination pour les résultats de recherche."""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50


@extend_schema(
    tags=['Search'],
    parameters=[
        OpenApiParameter(
            name='q',
            description='Terme de recherche',
            required=True,
            type=str
        ),
        OpenApiParameter(
            name='type',
            description='Type de contenu (article, video, all)',
            required=False,
            type=str
        ),
        OpenApiParameter(
            name='limit',
            description='Nombre maximum de résultats',
            required=False,
            type=int
        ),
    ]
)
class SearchView(generics.GenericAPIView):
    """
    Recherche de contenu (US-08).
    Recherche dans titres, descriptions et contenus.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        content_type = request.query_params.get('type', 'all')
        limit = int(request.query_params.get('limit', 20))

        if not query:
            return Response(
                {'error': 'Le paramètre "q" est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(query) < 2:
            return Response(
                {'error': 'Le terme de recherche doit contenir au moins 2 caractères.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        search_service = SearchService(query)

        if content_type == 'article':
            results = {
                'articles': search_service.search_articles(limit=limit),
                'total_count': 0,
            }
            results['total_count'] = len(results['articles'])
        elif content_type == 'video':
            results = {
                'videos': search_service.search_videos(limit=limit),
                'total_count': 0,
            }
            results['total_count'] = len(results['videos'])
        else:
            results = search_service.search_all(limit=limit)

        return Response({
            'query': query,
            'results': results,
        })


@extend_schema(
    tags=['Search'],
    parameters=[
        OpenApiParameter(
            name='q',
            description='Début du terme de recherche',
            required=True,
            type=str
        ),
    ]
)
class SearchSuggestionsView(generics.GenericAPIView):
    """
    Suggestions de recherche en temps réel.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()

        if len(query) < 2:
            return Response({'suggestions': []})

        suggestions = get_search_suggestions(query, limit=5)

        return Response({'suggestions': suggestions})


@extend_schema(tags=['Search'])
class TrendingTagsView(generics.GenericAPIView):
    """
    Tags populaires / tendances.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        tags = get_trending_tags(limit=limit)

        return Response({'tags': tags})


@extend_schema(tags=['Search'])
class GlobalSearchView(generics.GenericAPIView):
    """
    Recherche globale avec résultats paginés.
    """
    permission_classes = [AllowAny]
    pagination_class = SearchResultsPagination

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        content_type = request.query_params.get('type', 'all')
        category = request.query_params.get('category', None)
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)

        if not query:
            return Response(
                {'error': 'Le paramètre "q" est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        search_service = SearchService(query)

        # Recherche de base
        if content_type in ['article', 'all']:
            articles = search_service.search_articles(limit=50)
        else:
            articles = []

        if content_type in ['video', 'all']:
            videos = search_service.search_videos(limit=50)
        else:
            videos = []

        # Combiner les résultats
        all_results = []

        for article in articles:
            article['result_type'] = 'article'
            all_results.append(article)

        for video in videos:
            video['result_type'] = 'video'
            all_results.append(video)

        # Trier par date de publication
        all_results.sort(
            key=lambda x: x.get('published_at') or '',
            reverse=True
        )

        # Pagination manuelle
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 12))
        start = (page - 1) * page_size
        end = start + page_size

        paginated_results = all_results[start:end]
        total_count = len(all_results)
        total_pages = (total_count + page_size - 1) // page_size

        return Response({
            'query': query,
            'results': paginated_results,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
            },
            'filters': {
                'type': content_type,
                'category': category,
            }
        })
