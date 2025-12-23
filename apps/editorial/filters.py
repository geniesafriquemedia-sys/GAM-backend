"""
Editorial Filters - Filtres pour les articles et vidéos
"""

import django_filters
from .models import Article, Video


class ArticleFilter(django_filters.FilterSet):
    """Filtres pour les articles."""

    # Filtres de base
    category = django_filters.NumberFilter(field_name='category__id')
    category_slug = django_filters.CharFilter(field_name='category__slug')
    author = django_filters.NumberFilter(field_name='author__id')
    author_slug = django_filters.CharFilter(field_name='author__slug')
    status = django_filters.ChoiceFilter(choices=Article.PublicationStatus.choices)

    # Filtres booléens
    is_featured = django_filters.BooleanFilter()
    is_trending = django_filters.BooleanFilter()

    # Filtres de date
    published_after = django_filters.DateTimeFilter(
        field_name='published_at',
        lookup_expr='gte'
    )
    published_before = django_filters.DateTimeFilter(
        field_name='published_at',
        lookup_expr='lte'
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )

    # Recherche par tag
    tag = django_filters.CharFilter(
        field_name='tags',
        lookup_expr='icontains'
    )

    # Tri
    ordering = django_filters.OrderingFilter(
        fields=(
            ('published_at', 'published_at'),
            ('created_at', 'created_at'),
            ('views_count', 'views'),
            ('reading_time', 'reading_time'),
            ('title', 'title'),
        )
    )

    class Meta:
        model = Article
        fields = [
            'category', 'category_slug', 'author', 'author_slug',
            'status', 'is_featured', 'is_trending', 'tag'
        ]


class VideoFilter(django_filters.FilterSet):
    """Filtres pour les vidéos."""

    # Filtres de base
    category = django_filters.NumberFilter(field_name='category__id')
    category_slug = django_filters.CharFilter(field_name='category__slug')
    video_type = django_filters.ChoiceFilter(choices=Video.VideoType.choices)
    status = django_filters.ChoiceFilter(choices=Video.PublicationStatus.choices)

    # Filtres booléens
    is_featured = django_filters.BooleanFilter()
    is_live = django_filters.BooleanFilter()

    # Filtres de date
    published_after = django_filters.DateTimeFilter(
        field_name='published_at',
        lookup_expr='gte'
    )
    published_before = django_filters.DateTimeFilter(
        field_name='published_at',
        lookup_expr='lte'
    )

    # Filtres de durée
    min_duration = django_filters.NumberFilter(
        field_name='duration',
        lookup_expr='gte'
    )
    max_duration = django_filters.NumberFilter(
        field_name='duration',
        lookup_expr='lte'
    )

    # Recherche par tag
    tag = django_filters.CharFilter(
        field_name='tags',
        lookup_expr='icontains'
    )

    # Tri
    ordering = django_filters.OrderingFilter(
        fields=(
            ('published_at', 'published_at'),
            ('created_at', 'created_at'),
            ('views_count', 'views'),
            ('duration', 'duration'),
            ('title', 'title'),
        )
    )

    class Meta:
        model = Video
        fields = [
            'category', 'category_slug', 'video_type',
            'status', 'is_featured', 'is_live', 'tag'
        ]
