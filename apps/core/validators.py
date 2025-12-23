"""
Core Validators - Validateurs personnalisés
"""

import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


# =============================================================================
# COLOR VALIDATORS
# =============================================================================

hex_color_validator = RegexValidator(
    regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
    message='Entrez une couleur hexadécimale valide (ex: #FF5733 ou #F53)',
    code='invalid_hex_color'
)


def validate_hex_color(value: str) -> None:
    """Valide un code couleur hexadécimal (US-01)."""
    if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
        raise ValidationError(
            'Entrez une couleur hexadécimale valide (ex: #FF5733)',
            code='invalid_hex_color'
        )


# =============================================================================
# URL VALIDATORS
# =============================================================================

def validate_youtube_url(value: str) -> None:
    """Valide une URL YouTube (US-03)."""
    youtube_patterns = [
        r'^https?:\/\/(www\.)?youtube\.com\/watch\?v=[a-zA-Z0-9_-]{11}',
        r'^https?:\/\/(www\.)?youtu\.be\/[a-zA-Z0-9_-]{11}',
        r'^https?:\/\/(www\.)?youtube\.com\/embed\/[a-zA-Z0-9_-]{11}',
        r'^https?:\/\/(www\.)?youtube\.com\/shorts\/[a-zA-Z0-9_-]{11}',
    ]

    for pattern in youtube_patterns:
        if re.match(pattern, value):
            return

    raise ValidationError(
        'Entrez une URL YouTube valide',
        code='invalid_youtube_url'
    )


# =============================================================================
# IMAGE VALIDATORS
# =============================================================================

def validate_image_size(image, max_size_mb: int = 5) -> None:
    """Valide la taille d'une image."""
    max_size = max_size_mb * 1024 * 1024  # Convertir en bytes

    if image.size > max_size:
        raise ValidationError(
            f'La taille de l\'image ne doit pas dépasser {max_size_mb} MB',
            code='image_too_large'
        )


def validate_image_dimensions(image, max_width: int = 4096, max_height: int = 4096) -> None:
    """Valide les dimensions d'une image."""
    from PIL import Image as PILImage

    img = PILImage.open(image)
    width, height = img.size

    if width > max_width or height > max_height:
        raise ValidationError(
            f'Les dimensions de l\'image ne doivent pas dépasser {max_width}x{max_height} pixels',
            code='image_too_large'
        )


# =============================================================================
# CONTENT VALIDATORS
# =============================================================================

def validate_no_html(value: str) -> None:
    """Vérifie qu'une valeur ne contient pas de HTML."""
    if re.search(r'<[^>]+>', value):
        raise ValidationError(
            'Le HTML n\'est pas autorisé dans ce champ',
            code='html_not_allowed'
        )


def validate_min_words(value: str, min_words: int = 10) -> None:
    """Valide un nombre minimum de mots."""
    word_count = len(value.split())

    if word_count < min_words:
        raise ValidationError(
            f'Le contenu doit contenir au moins {min_words} mots',
            code='content_too_short'
        )
