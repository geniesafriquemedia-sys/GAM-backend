"""
Article Model - Gestion des articles (US-02, US-04)
Wagtail Snippet avec StreamField pour blocs dynamiques
"""

from django.db import models
from django.conf import settings
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel
from wagtail.search import index
from apps.core.models import (
    TimeStampedModel,
    SluggedModel,
    PublishableModel,
    SEOModel
)
from apps.editorial.blocks import ArticleStreamBlock


# Note: Enregistré comme snippet via EditorialViewSetGroup dans wagtail_hooks.py
class Article(index.Indexed, TimeStampedModel, SluggedModel, PublishableModel, SEOModel):
    """
    Modèle Article avec contenu riche.
    US-02: Composition d'article à l'aide de blocs dynamiques.
    US-04: Workflow de publication (Brouillon / Publié).
    """

    # Informations principales
    title = models.CharField(
        'Titre',
        max_length=255,
        db_index=True
    )
    excerpt = models.TextField(
        'Extrait',
        max_length=300,
        blank=True,
        help_text='Résumé court de l\'article (max 300 caractères)'
    )
    featured_image = models.ImageField(
        'Image principale',
        upload_to='articles/featured/',
        blank=True,
        null=True
    )
    featured_image_caption = models.CharField(
        'Légende de l\'image',
        max_length=255,
        blank=True
    )

    # Relations
    author = models.ForeignKey(
        'editorial.Author',
        on_delete=models.PROTECT,
        related_name='articles',
        verbose_name='Auteur'
    )
    category = models.ForeignKey(
        'editorial.Category',
        on_delete=models.PROTECT,
        related_name='articles',
        verbose_name='Catégorie'
    )
    tags = models.CharField(
        'Tags',
        max_length=500,
        blank=True,
        help_text='Tags séparés par des virgules'
    )

    # Contenu avec StreamField (Wagtail)
    body = StreamField(
        ArticleStreamBlock,
        blank=True,
        null=True,
        use_json_field=True,
        verbose_name='Contenu',
        help_text='Composez votre article avec les blocs disponibles'
    )

    # Contenu legacy (pour compatibilité ou migration)
    content = models.TextField(
        'Contenu HTML (legacy)',
        blank=True,
        help_text='Ancien contenu HTML - utilisez le champ "Contenu" ci-dessus'
    )

    # Métadonnées calculées
    reading_time = models.PositiveIntegerField(
        'Temps de lecture',
        default=1,
        help_text='Temps de lecture estimé en minutes'
    )
    views_count = models.PositiveIntegerField(
        'Nombre de vues',
        default=0
    )

    # Mise en avant
    is_featured = models.BooleanField(
        'À la Une',
        default=False,
        db_index=True,
        help_text='Afficher dans la section À la Une (US-05)'
    )
    is_trending = models.BooleanField(
        'Tendance',
        default=False,
        help_text='Marquer comme article tendance'
    )

    # Utilisateur qui a créé/modifié
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_articles',
        verbose_name='Créé par'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_articles',
        verbose_name='Modifié par'
    )

    # Configuration du slug
    slug_source_field = 'title'

    # Wagtail Panels pour l'interface admin
    panels = [
        MultiFieldPanel([
            FieldPanel('title'),
            FieldPanel('excerpt'),
            FieldPanel('featured_image'),
            FieldPanel('featured_image_caption'),
        ], heading="Informations principales"),
        MultiFieldPanel([
            FieldPanel('author'),
            FieldPanel('category'),
            FieldPanel('tags'),
        ], heading="Classification"),
        FieldPanel('body'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('status'),
                FieldPanel('published_at'),
            ]),
            FieldRowPanel([
                FieldPanel('is_featured'),
                FieldPanel('is_trending'),
            ]),
        ], heading="Publication"),
        MultiFieldPanel([
            FieldPanel('meta_title'),
            FieldPanel('meta_description'),
        ], heading="SEO", classname="collapsed"),
    ]

    # Wagtail Search Index
    search_fields = [
        index.SearchField('title', boost=10),
        index.SearchField('excerpt', boost=5),
        index.FilterField('status'),
        index.FilterField('category'),
        index.FilterField('author'),
        index.FilterField('is_featured'),
    ]

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['category', 'status']),
        ]

    def __str__(self):
        return self.title

    def get_tags_list(self) -> list:
        """Retourne les tags sous forme de liste."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def get_full_content(self) -> str:
        """
        Retourne le contenu complet de l'article.
        Utilise StreamField body ou le contenu legacy.
        """
        if self.body:
            # Extraire le texte des blocs StreamField
            text_content = []
            for block in self.body:
                if block.block_type == 'text':
                    text_content.append(str(block.value.get('content', '')))
                elif block.block_type == 'quote':
                    text_content.append(str(block.value.get('quote', '')))
                elif block.block_type == 'heading':
                    text_content.append(str(block.value.get('heading', '')))
            return '\n'.join(text_content)
        return self.content

    def increment_views(self):
        """Incrémente le compteur de vues."""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    @property
    def related_articles(self):
        """Retourne les articles liés (même catégorie, US-06)."""
        return Article.objects.filter(
            category=self.category,
            status=self.PublicationStatus.PUBLISHED
        ).exclude(pk=self.pk)[:4]


class ArticleBlock(TimeStampedModel):
    """
    Bloc de contenu pour les articles (US-02).
    Permet une mise en page riche sans HTML direct.
    Types: texte, image, citation, vidéo, tweet.
    """

    class BlockType(models.TextChoices):
        TEXT = 'text', 'Texte'
        IMAGE = 'image', 'Image'
        QUOTE = 'quote', 'Citation'
        VIDEO = 'video', 'Vidéo'
        TWEET = 'tweet', 'Tweet'
        HEADING = 'heading', 'Titre'
        LIST = 'list', 'Liste'
        CODE = 'code', 'Code'

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='blocks',
        verbose_name='Article'
    )
    block_type = models.CharField(
        'Type de bloc',
        max_length=20,
        choices=BlockType.choices,
        default=BlockType.TEXT
    )
    order = models.PositiveIntegerField(
        'Ordre',
        default=0,
        db_index=True
    )

    # Contenu selon le type
    content = models.TextField(
        'Contenu',
        blank=True,
        help_text='Contenu textuel du bloc'
    )
    image = models.ImageField(
        'Image',
        upload_to='articles/blocks/',
        blank=True,
        null=True
    )
    image_caption = models.CharField(
        'Légende',
        max_length=255,
        blank=True
    )
    embed_url = models.URLField(
        'URL embed',
        blank=True,
        help_text='URL YouTube ou Twitter'
    )

    # Métadonnées du bloc
    metadata = models.JSONField(
        'Métadonnées',
        default=dict,
        blank=True,
        help_text='Données supplémentaires (niveau de titre, langue du code, etc.)'
    )

    class Meta:
        verbose_name = 'Bloc d\'article'
        verbose_name_plural = 'Blocs d\'article'
        ordering = ['order']

    def __str__(self):
        return f'{self.article.title} - Bloc {self.order} ({self.get_block_type_display()})'

    def render(self) -> str:
        """Génère le HTML du bloc."""
        renderers = {
            self.BlockType.TEXT: self._render_text,
            self.BlockType.IMAGE: self._render_image,
            self.BlockType.QUOTE: self._render_quote,
            self.BlockType.VIDEO: self._render_video,
            self.BlockType.TWEET: self._render_tweet,
            self.BlockType.HEADING: self._render_heading,
            self.BlockType.LIST: self._render_list,
            self.BlockType.CODE: self._render_code,
        }
        renderer = renderers.get(self.block_type, self._render_text)
        return renderer()

    def _render_text(self) -> str:
        return f'<div class="article-text">{self.content}</div>'

    def _render_image(self) -> str:
        if self.image:
            caption = f'<figcaption>{self.image_caption}</figcaption>' if self.image_caption else ''
            return f'<figure class="article-image"><img src="{self.image.url}" alt="{self.image_caption}" loading="lazy" />{caption}</figure>'
        return ''

    def _render_quote(self) -> str:
        author = self.metadata.get('author', '')
        author_html = f'<cite>— {author}</cite>' if author else ''
        return f'<blockquote class="article-quote"><p>{self.content}</p>{author_html}</blockquote>'

    def _render_video(self) -> str:
        from apps.core.utils import extract_youtube_id, get_youtube_embed_url
        video_id = extract_youtube_id(self.embed_url)
        if video_id:
            embed_url = get_youtube_embed_url(video_id)
            return f'<div class="article-video"><iframe src="{embed_url}" frameborder="0" allowfullscreen loading="lazy"></iframe></div>'
        return ''

    def _render_tweet(self) -> str:
        return f'<div class="article-tweet" data-tweet-url="{self.embed_url}"></div>'

    def _render_heading(self) -> str:
        level = self.metadata.get('level', 2)
        return f'<h{level} class="article-heading">{self.content}</h{level}>'

    def _render_list(self) -> str:
        list_type = self.metadata.get('type', 'ul')
        items = self.content.split('\n')
        items_html = ''.join(f'<li>{item}</li>' for item in items if item.strip())
        return f'<{list_type} class="article-list">{items_html}</{list_type}>'

    def _render_code(self) -> str:
        language = self.metadata.get('language', '')
        return f'<pre class="article-code"><code class="language-{language}">{self.content}</code></pre>'
