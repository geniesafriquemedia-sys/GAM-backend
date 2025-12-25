"""
Custom Cloudinary Storage Backends for GAM
Organise les médias dans des dossiers structurés sur Cloudinary.
"""

from django.conf import settings
from cloudinary_storage.storage import MediaCloudinaryStorage, RawMediaCloudinaryStorage
import cloudinary


class GAMCloudinaryStorage(MediaCloudinaryStorage):
    """
    Storage personnalisé pour GAM sans préfixe 'media/'.
    Les fichiers sont stockés directement avec leur chemin upload_to.
    """

    def url(self, name):
        """Retourne l'URL Cloudinary sans le préfixe media."""
        if not name:
            return ''
        # Construire l'URL directement sans préfixe
        cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{name}"


class ArticleImageStorage(MediaCloudinaryStorage):
    """Storage pour les images d'articles."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder = 'gam/articles'
        self.resource_type = 'image'


class AuthorPhotoStorage(MediaCloudinaryStorage):
    """Storage pour les photos d'auteurs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder = 'gam/authors'
        self.resource_type = 'image'


class CategoryImageStorage(MediaCloudinaryStorage):
    """Storage pour les images de catégories."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder = 'gam/categories'
        self.resource_type = 'image'


class VideoThumbnailStorage(MediaCloudinaryStorage):
    """Storage pour les miniatures de vidéos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder = 'gam/videos/thumbnails'
        self.resource_type = 'image'


class UserAvatarStorage(MediaCloudinaryStorage):
    """Storage pour les avatars utilisateurs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder = 'gam/users/avatars'
        self.resource_type = 'image'


def get_cloudinary_storage(folder: str):
    """
    Factory pour créer un storage Cloudinary avec un dossier spécifique.

    Usage:
        storage = get_cloudinary_storage('articles/featured')
    """
    class DynamicCloudinaryStorage(MediaCloudinaryStorage):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.folder = f'gam/{folder}'
            self.resource_type = 'image'

    return DynamicCloudinaryStorage()
