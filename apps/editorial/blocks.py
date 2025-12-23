"""
Wagtail StreamField Blocks pour les articles (US-02)
Blocs dynamiques : texte, image, citation, vidéo, tweet
"""

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock


class TextBlock(blocks.StructBlock):
    """Bloc de texte riche."""
    content = blocks.RichTextBlock(
        features=['h2', 'h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul', 'blockquote'],
        label="Contenu"
    )

    class Meta:
        template = 'editorial/blocks/text_block.html'
        icon = 'doc-full'
        label = 'Texte'


class ImageBlock(blocks.StructBlock):
    """Bloc image avec légende."""
    image = ImageChooserBlock(label="Image")
    caption = blocks.CharBlock(
        required=False,
        max_length=255,
        label="Légende"
    )
    attribution = blocks.CharBlock(
        required=False,
        max_length=255,
        label="Crédit photo"
    )

    class Meta:
        template = 'editorial/blocks/image_block.html'
        icon = 'image'
        label = 'Image'


class QuoteBlock(blocks.StructBlock):
    """Bloc citation."""
    quote = blocks.TextBlock(label="Citation")
    author = blocks.CharBlock(
        required=False,
        max_length=255,
        label="Auteur"
    )
    source = blocks.CharBlock(
        required=False,
        max_length=255,
        label="Source"
    )

    class Meta:
        template = 'editorial/blocks/quote_block.html'
        icon = 'openquote'
        label = 'Citation'


class VideoBlock(blocks.StructBlock):
    """Bloc vidéo YouTube."""
    video = EmbedBlock(
        label="URL de la vidéo",
        help_text="Collez l'URL YouTube, Vimeo ou autre"
    )
    caption = blocks.CharBlock(
        required=False,
        max_length=255,
        label="Légende"
    )

    class Meta:
        template = 'editorial/blocks/video_block.html'
        icon = 'media'
        label = 'Vidéo'


class TweetBlock(blocks.StructBlock):
    """Bloc Tweet/X intégré."""
    tweet_url = blocks.URLBlock(
        label="URL du Tweet",
        help_text="Collez l'URL du tweet (ex: https://twitter.com/user/status/123)"
    )

    class Meta:
        template = 'editorial/blocks/tweet_block.html'
        icon = 'social'
        label = 'Tweet'


class HeadingBlock(blocks.StructBlock):
    """Bloc titre/sous-titre."""
    heading = blocks.CharBlock(label="Titre")
    level = blocks.ChoiceBlock(
        choices=[
            ('h2', 'H2 - Titre principal'),
            ('h3', 'H3 - Sous-titre'),
            ('h4', 'H4 - Petit titre'),
        ],
        default='h2',
        label="Niveau"
    )

    class Meta:
        template = 'editorial/blocks/heading_block.html'
        icon = 'title'
        label = 'Titre'


class ListBlock(blocks.StructBlock):
    """Bloc liste à puces ou numérotée."""
    items = blocks.ListBlock(
        blocks.CharBlock(label="Élément"),
        label="Éléments de la liste"
    )
    list_type = blocks.ChoiceBlock(
        choices=[
            ('ul', 'Liste à puces'),
            ('ol', 'Liste numérotée'),
        ],
        default='ul',
        label="Type de liste"
    )

    class Meta:
        template = 'editorial/blocks/list_block.html'
        icon = 'list-ul'
        label = 'Liste'


class CodeBlock(blocks.StructBlock):
    """Bloc code source."""
    language = blocks.ChoiceBlock(
        choices=[
            ('python', 'Python'),
            ('javascript', 'JavaScript'),
            ('html', 'HTML'),
            ('css', 'CSS'),
            ('bash', 'Bash'),
            ('json', 'JSON'),
            ('other', 'Autre'),
        ],
        default='python',
        label="Langage"
    )
    code = blocks.TextBlock(label="Code")

    class Meta:
        template = 'editorial/blocks/code_block.html'
        icon = 'code'
        label = 'Code'


class CallToActionBlock(blocks.StructBlock):
    """Bloc appel à l'action."""
    text = blocks.CharBlock(label="Texte du bouton")
    url = blocks.URLBlock(label="Lien")
    style = blocks.ChoiceBlock(
        choices=[
            ('primary', 'Principal (bleu)'),
            ('secondary', 'Secondaire (gris)'),
            ('success', 'Succès (vert)'),
        ],
        default='primary',
        label="Style"
    )

    class Meta:
        template = 'editorial/blocks/cta_block.html'
        icon = 'link'
        label = 'Bouton'


# StreamField principal pour les articles
ArticleStreamBlock = [
    ('text', TextBlock()),
    ('image', ImageBlock()),
    ('quote', QuoteBlock()),
    ('video', VideoBlock()),
    ('tweet', TweetBlock()),
    ('heading', HeadingBlock()),
    ('list', ListBlock()),
    ('code', CodeBlock()),
    ('cta', CallToActionBlock()),
]
