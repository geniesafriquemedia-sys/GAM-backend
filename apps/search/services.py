"""
Search Services - Services de recherche de contenu (US-08)
Recherche dans titres, descriptions et contenus avec résultats paginés
"""

from typing import List, Dict, Any, Optional
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from django.utils import timezone
from django.core.cache import cache

from apps.editorial.models import Article, Video, Category, Author


class SearchService:
    """
    Service de recherche unifié pour tous les contenus.
    US-08: Recherche dans titres, descriptions et contenus.
    """

    CACHE_TIMEOUT = 60 * 5  # 5 minutes

    def __init__(self, query: str):
        self.query = query.strip()
        self.cache_key = f'search:{self.query.lower()}'

    def search_all(self, limit: int = 20) -> Dict[str, List]:
        """
        Recherche dans tous les types de contenu.
        Retourne les résultats groupés par type.
        """
        # Vérifier le cache
        cached = cache.get(self.cache_key)
        if cached:
            return cached

        results = {
            'articles': self.search_articles(limit=limit),
            'videos': self.search_videos(limit=limit),
            'categories': self.search_categories(limit=5),
            'authors': self.search_authors(limit=5),
            'total_count': 0,
        }

        results['total_count'] = (
            len(results['articles']) +
            len(results['videos']) +
            len(results['categories']) +
            len(results['authors'])
        )

        # Mettre en cache
        cache.set(self.cache_key, results, self.CACHE_TIMEOUT)

        return results

    def search_articles(self, limit: int = 20) -> List[Dict]:
        """
        Recherche dans les articles.
        """
        if not self.query:
            return []

        now = timezone.now()

        queryset = Article.objects.filter(
            status='published'
        ).filter(
            Q(published_at__isnull=True) | Q(published_at__lte=now)
        ).filter(
            Q(title__icontains=self.query) |
            Q(excerpt__icontains=self.query) |
            Q(content__icontains=self.query) |
            Q(tags__icontains=self.query)
        ).select_related('author', 'category').order_by('-published_at')[:limit]

        return [
            {
                'id': article.id,
                'type': 'article',
                'title': article.title,
                'slug': article.slug,
                'excerpt': article.excerpt,
                'featured_image': article.featured_image.url if article.featured_image else None,
                'author': {
                    'name': article.author.name,
                    'slug': article.author.slug,
                },
                'category': {
                    'name': article.category.name,
                    'slug': article.category.slug,
                    'color': article.category.color,
                },
                'reading_time': article.reading_time,
                'published_at': article.published_at,
            }
            for article in queryset
        ]

    def search_videos(self, limit: int = 20) -> List[Dict]:
        """
        Recherche dans les vidéos.
        """
        if not self.query:
            return []

        now = timezone.now()

        queryset = Video.objects.filter(
            status='published'
        ).filter(
            Q(published_at__isnull=True) | Q(published_at__lte=now)
        ).filter(
            Q(title__icontains=self.query) |
            Q(description__icontains=self.query) |
            Q(tags__icontains=self.query)
        ).select_related('category').order_by('-published_at')[:limit]

        return [
            {
                'id': video.id,
                'type': 'video',
                'title': video.title,
                'slug': video.slug,
                'description': video.description[:200] if video.description else '',
                'thumbnail_url': video.thumbnail_url,
                'video_type': video.video_type,
                'duration_formatted': video.duration_formatted,
                'category': {
                    'name': video.category.name if video.category else None,
                    'slug': video.category.slug if video.category else None,
                    'color': video.category.color if video.category else None,
                },
                'published_at': video.published_at,
            }
            for video in queryset
        ]

    def search_categories(self, limit: int = 5) -> List[Dict]:
        """
        Recherche dans les catégories.
        """
        if not self.query:
            return []

        queryset = Category.objects.filter(
            is_active=True
        ).filter(
            Q(name__icontains=self.query) |
            Q(description__icontains=self.query)
        ).order_by('name')[:limit]

        return [
            {
                'id': category.id,
                'type': 'category',
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'color': category.color,
                'icon': category.icon,
                'articles_count': category.articles_count,
            }
            for category in queryset
        ]

    def search_authors(self, limit: int = 5) -> List[Dict]:
        """
        Recherche dans les auteurs.
        """
        if not self.query:
            return []

        queryset = Author.objects.filter(
            is_active=True
        ).filter(
            Q(name__icontains=self.query) |
            Q(bio__icontains=self.query)
        ).order_by('name')[:limit]

        return [
            {
                'id': author.id,
                'type': 'author',
                'name': author.name,
                'slug': author.slug,
                'photo': author.photo.url if author.photo else None,
                'bio': author.bio[:150] if author.bio else '',
                'articles_count': author.articles_count,
            }
            for author in queryset
        ]


def get_trending_tags(limit: int = 10) -> List[str]:
    """
    Retourne les tags les plus utilisés.
    """
    cache_key = 'trending_tags'
    cached = cache.get(cache_key)
    if cached:
        return cached

    now = timezone.now()

    # Récupérer tous les tags des articles récents
    articles = Article.objects.filter(
        status='published',
        tags__isnull=False
    ).filter(
        Q(published_at__isnull=True) | Q(published_at__lte=now)
    ).order_by('-published_at')[:100]

    tag_counts = {}
    for article in articles:
        for tag in article.get_tags_list():
            tag_lower = tag.lower()
            tag_counts[tag_lower] = tag_counts.get(tag_lower, 0) + 1

    # Trier par fréquence
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    trending = [tag for tag, count in sorted_tags[:limit]]

    cache.set(cache_key, trending, 60 * 15)  # 15 minutes
    return trending


def get_search_suggestions(query: str, limit: int = 5) -> List[str]:
    """
    Retourne des suggestions de recherche basées sur les titres existants.
    """
    if not query or len(query) < 2:
        return []

    now = timezone.now()

    # Titres d'articles correspondants
    article_titles = list(
        Article.objects.filter(
            status='published',
            title__icontains=query
        ).filter(
            Q(published_at__isnull=True) | Q(published_at__lte=now)
        ).values_list('title', flat=True)[:limit]
    )

    # Titres de vidéos correspondants
    video_titles = list(
        Video.objects.filter(
            status='published',
            title__icontains=query
        ).filter(
            Q(published_at__isnull=True) | Q(published_at__lte=now)
        ).values_list('title', flat=True)[:limit]
    )

    # Combiner et dédupliquer
    suggestions = list(set(article_titles + video_titles))[:limit]

    return suggestions
