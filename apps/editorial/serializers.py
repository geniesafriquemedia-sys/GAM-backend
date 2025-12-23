"""
Editorial Serializers - Sérialiseurs pour le contenu éditorial
Compatible avec Wagtail StreamField
"""

from rest_framework import serializers
from wagtail.rich_text import RichText
from .models import Author, Category, Article, Video

# Note: ArticleBlock est remplacé par StreamField dans le modèle Article
# mais on garde la compatibilité pour l'ancienne API si nécessaire
try:
    from .models import ArticleBlock
except ImportError:
    ArticleBlock = None


# =============================================================================
# AUTHOR SERIALIZERS
# =============================================================================

class AuthorListSerializer(serializers.ModelSerializer):
    """Serializer minimal pour les listes d'auteurs."""

    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'name', 'slug', 'photo', 'articles_count']

    def get_articles_count(self, obj):
        # Utilise l'annotation si disponible, sinon la propriété
        return getattr(obj, '_articles_count', None) or obj.articles_count


class AuthorDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour les détails d'un auteur."""

    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'id', 'name', 'slug', 'photo', 'bio', 'email',
            'twitter', 'linkedin', 'website', 'is_active',
            'articles_count', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at']

    def get_articles_count(self, obj):
        return getattr(obj, '_articles_count', None) or obj.articles_count


class AuthorCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la création/modification d'auteur."""

    class Meta:
        model = Author
        fields = [
            'name', 'photo', 'bio', 'email',
            'twitter', 'linkedin', 'website', 'is_active', 'user'
        ]


# =============================================================================
# CATEGORY SERIALIZERS
# =============================================================================

class CategoryListSerializer(serializers.ModelSerializer):
    """Serializer minimal pour les listes de catégories."""

    articles_count = serializers.SerializerMethodField()
    videos_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'color', 'icon',
            'articles_count', 'videos_count'
        ]

    def get_articles_count(self, obj):
        return getattr(obj, '_articles_count', None) or obj.articles_count

    def get_videos_count(self, obj):
        return getattr(obj, '_videos_count', None) or obj.videos_count


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour les détails d'une catégorie."""

    articles_count = serializers.SerializerMethodField()
    videos_count = serializers.SerializerMethodField()
    children = CategoryListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'color', 'icon', 'image',
            'parent', 'is_active', 'is_featured', 'order',
            'articles_count', 'videos_count', 'children', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at']

    def get_articles_count(self, obj):
        return getattr(obj, '_articles_count', None) or obj.articles_count

    def get_videos_count(self, obj):
        return getattr(obj, '_videos_count', None) or obj.videos_count


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la création/modification de catégorie."""

    class Meta:
        model = Category
        fields = [
            'name', 'description', 'color', 'icon', 'image',
            'parent', 'is_active', 'is_featured', 'order'
        ]


# =============================================================================
# STREAMFIELD BLOCK SERIALIZERS (Wagtail)
# =============================================================================

class StreamFieldBlockSerializer(serializers.Serializer):
    """Serializer pour les blocs StreamField de Wagtail."""
    type = serializers.CharField(source='block_type')
    id = serializers.CharField(read_only=True)
    value = serializers.SerializerMethodField()

    def get_value(self, block):
        """Convertit le bloc en dictionnaire sérialisable."""
        block_type = block.block_type
        value = block.value

        if block_type == 'text':
            return {
                'content': str(value.get('content', '')) if value else ''
            }
        elif block_type == 'image':
            image = value.get('image') if value else None
            return {
                'image_url': image.file.url if image else None,
                'caption': value.get('caption', '') if value else '',
                'attribution': value.get('attribution', '') if value else ''
            }
        elif block_type == 'quote':
            return {
                'quote': value.get('quote', '') if value else '',
                'author': value.get('author', '') if value else '',
                'source': value.get('source', '') if value else ''
            }
        elif block_type == 'video':
            embed = value.get('video') if value else None
            return {
                'embed_url': embed.url if embed else '',
                'caption': value.get('caption', '') if value else ''
            }
        elif block_type == 'tweet':
            return {
                'tweet_url': value.get('tweet_url', '') if value else ''
            }
        elif block_type == 'heading':
            return {
                'heading': value.get('heading', '') if value else '',
                'level': value.get('level', 'h2') if value else 'h2'
            }
        elif block_type == 'list':
            return {
                'items': list(value.get('items', [])) if value else [],
                'list_type': value.get('list_type', 'ul') if value else 'ul'
            }
        elif block_type == 'code':
            return {
                'language': value.get('language', '') if value else '',
                'code': value.get('code', '') if value else ''
            }
        elif block_type == 'cta':
            return {
                'text': value.get('text', '') if value else '',
                'url': value.get('url', '') if value else '',
                'style': value.get('style', 'primary') if value else 'primary'
            }
        return dict(value) if value else {}


# Legacy serializer pour compatibilité avec l'ancienne API
class ArticleBlockSerializer(serializers.Serializer):
    """Serializer pour les anciens blocs d'article (compatibilité)."""
    id = serializers.IntegerField(read_only=True)
    block_type = serializers.CharField()
    order = serializers.IntegerField()
    content = serializers.CharField(allow_blank=True)
    image = serializers.ImageField(allow_null=True, required=False)
    image_caption = serializers.CharField(allow_blank=True, required=False)
    embed_url = serializers.URLField(allow_blank=True, required=False)
    metadata = serializers.JSONField(required=False)


# =============================================================================
# ARTICLE SERIALIZERS
# =============================================================================

class ArticleListSerializer(serializers.ModelSerializer):
    """Serializer minimal pour les listes d'articles (US-05)."""

    author = AuthorListSerializer(read_only=True)
    category = CategoryListSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'author', 'category', 'reading_time', 'views_count',
            'is_featured', 'is_trending', 'status', 'published_at'
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour les détails d'un article (US-06)."""

    author = AuthorDetailSerializer(read_only=True)
    category = CategoryDetailSerializer(read_only=True)
    body_blocks = serializers.SerializerMethodField()
    # Legacy: blocks pour compatibilité avec l'ancienne API
    blocks = ArticleBlockSerializer(many=True, read_only=True)
    tags_list = serializers.ListField(source='get_tags_list', read_only=True)
    related_articles = ArticleListSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'featured_image_caption', 'author', 'category', 'tags', 'tags_list',
            'content', 'body_blocks', 'blocks', 'reading_time', 'views_count',
            'is_featured', 'is_trending', 'status', 'published_at',
            'meta_title', 'meta_description', 'related_articles',
            'created_at', 'updated_at'
        ]

    def get_body_blocks(self, obj):
        """Sérialise les blocs StreamField du body."""
        if not obj.body:
            return []
        return StreamFieldBlockSerializer(obj.body, many=True).data


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la création/modification d'article."""

    blocks = ArticleBlockSerializer(many=True, required=False)

    class Meta:
        model = Article
        fields = [
            'title', 'excerpt', 'featured_image', 'featured_image_caption',
            'author', 'category', 'tags', 'content', 'blocks',
            'is_featured', 'is_trending', 'status', 'published_at',
            'meta_title', 'meta_description'
        ]

    def create(self, validated_data):
        blocks_data = validated_data.pop('blocks', [])
        article = Article.objects.create(**validated_data)

        for block_data in blocks_data:
            ArticleBlock.objects.create(article=article, **block_data)

        return article

    def update(self, instance, validated_data):
        blocks_data = validated_data.pop('blocks', None)

        # Mettre à jour l'article
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Mettre à jour les blocs si fournis
        if blocks_data is not None:
            # Supprimer les anciens blocs
            instance.blocks.all().delete()
            # Créer les nouveaux
            for block_data in blocks_data:
                ArticleBlock.objects.create(article=instance, **block_data)

        return instance


class ArticleAdminSerializer(serializers.ModelSerializer):
    """Serializer pour l'administration des articles."""

    author_name = serializers.CharField(source='author.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'author', 'author_name',
            'category', 'category_name', 'status', 'published_at',
            'is_featured', 'is_trending', 'views_count', 'reading_time',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'reading_time', 'created_at', 'updated_at']


# =============================================================================
# VIDEO SERIALIZERS
# =============================================================================

class VideoListSerializer(serializers.ModelSerializer):
    """Serializer minimal pour les listes de vidéos (US-07)."""

    category = CategoryListSerializer(read_only=True)
    thumbnail_url = serializers.CharField(read_only=True)
    duration_formatted = serializers.CharField(read_only=True)

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'slug', 'description', 'youtube_id',
            'thumbnail_url', 'duration_formatted',
            'video_type', 'category', 'views_count', 'is_featured',
            'is_live', 'status', 'published_at'
        ]


class VideoDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour les détails d'une vidéo."""

    category = CategoryDetailSerializer(read_only=True)
    thumbnail_url = serializers.CharField(read_only=True)
    embed_url = serializers.CharField(read_only=True)
    duration_formatted = serializers.CharField(read_only=True)
    tags_list = serializers.ListField(source='get_tags_list', read_only=True)
    related_videos = VideoListSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'slug', 'description', 'youtube_url', 'youtube_id',
            'thumbnail_url', 'embed_url', 'duration', 'duration_formatted',
            'video_type', 'category', 'tags', 'tags_list',
            'views_count', 'is_featured', 'is_live', 'status', 'published_at',
            'meta_title', 'meta_description', 'related_videos',
            'created_at', 'updated_at'
        ]


class VideoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la création/modification de vidéo."""

    class Meta:
        model = Video
        fields = [
            'title', 'description', 'youtube_url', 'thumbnail',
            'video_type', 'category', 'tags', 'duration',
            'is_featured', 'is_live', 'status', 'published_at',
            'meta_title', 'meta_description'
        ]


class VideoAdminSerializer(serializers.ModelSerializer):
    """Serializer pour l'administration des vidéos."""

    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    thumbnail_url = serializers.CharField(read_only=True)

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'slug', 'thumbnail_url', 'video_type',
            'category', 'category_name', 'status', 'published_at',
            'is_featured', 'is_live', 'views_count', 'duration',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'created_at', 'updated_at']
