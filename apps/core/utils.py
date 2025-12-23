"""
Core Utilities - Fonctions utilitaires partagées
"""

import re
import math
from typing import Optional
from django.conf import settings


def calculate_reading_time(content: str) -> int:
    """
    Calcule le temps de lecture estimé en minutes (US-02).

    Args:
        content: Le texte du contenu

    Returns:
        Temps de lecture en minutes (minimum 1)
    """
    if not content:
        return 1

    # Nettoyer le HTML si présent
    clean_text = re.sub(r'<[^>]+>', '', content)

    # Compter les mots
    words = len(clean_text.split())

    # Calculer le temps de lecture
    reading_speed = getattr(settings, 'READING_SPEED_WPM', 200)
    minutes = math.ceil(words / reading_speed)

    return max(1, minutes)


def extract_youtube_id(url: str) -> Optional[str]:
    """
    Extrait l'ID YouTube d'une URL (US-03).

    Args:
        url: URL YouTube

    Returns:
        ID de la vidéo ou None
    """
    if not url:
        return None

    # Patterns pour les URLs YouTube
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def get_youtube_thumbnail(video_id: str, quality: str = 'maxresdefault') -> str:
    """
    Génère l'URL de la miniature YouTube (US-03).

    Args:
        video_id: ID de la vidéo YouTube
        quality: Qualité de l'image (default, mqdefault, hqdefault, sddefault, maxresdefault)

    Returns:
        URL de la miniature
    """
    if not video_id:
        return ''

    return f'https://img.youtube.com/vi/{video_id}/{quality}.jpg'


def get_youtube_embed_url(video_id: str) -> str:
    """
    Génère l'URL d'embed YouTube.

    Args:
        video_id: ID de la vidéo YouTube

    Returns:
        URL d'embed
    """
    if not video_id:
        return ''

    return f'https://www.youtube.com/embed/{video_id}'


def truncate_text(text: str, max_length: int = 160, suffix: str = '...') -> str:
    """
    Tronque un texte à une longueur maximale.

    Args:
        text: Texte à tronquer
        max_length: Longueur maximale
        suffix: Suffixe à ajouter si tronqué

    Returns:
        Texte tronqué
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)].rsplit(' ', 1)[0] + suffix


def sanitize_html(html: str) -> str:
    """
    Nettoie le HTML pour éviter les attaques XSS.

    Args:
        html: HTML à nettoyer

    Returns:
        HTML nettoyé
    """
    import bleach

    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 's', 'a', 'ul', 'ol', 'li',
        'blockquote', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'figure',
        'figcaption', 'iframe', 'div', 'span'
    ]

    allowed_attrs = {
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height', 'loading'],
        'iframe': ['src', 'width', 'height', 'frameborder', 'allowfullscreen'],
        'div': ['class'],
        'span': ['class'],
    }

    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)


def generate_excerpt(content: str, max_length: int = 200) -> str:
    """
    Génère un extrait à partir du contenu.

    Args:
        content: Contenu HTML ou texte
        max_length: Longueur maximale de l'extrait

    Returns:
        Extrait généré
    """
    if not content:
        return ''

    # Nettoyer le HTML
    clean_text = re.sub(r'<[^>]+>', '', content)

    # Supprimer les espaces multiples
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    return truncate_text(clean_text, max_length)
