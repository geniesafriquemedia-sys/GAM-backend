"""
Supabase Storage Backends for GAM
Stockage des médias sur Supabase Storage (compatible S3).
"""

from storages.backends.s3boto3 import S3Boto3Storage


class GAMBaseStorage(S3Boto3Storage):
    """Storage de base Supabase S3 pour GAM."""
    bucket_name = 'gam-media'
    file_overwrite = False


class ArticleImageStorage(GAMBaseStorage):
    """Storage pour les images d'articles."""
    location = 'gam/articles'


class AuthorPhotoStorage(GAMBaseStorage):
    """Storage pour les photos d'auteurs."""
    location = 'gam/authors'


class CategoryImageStorage(GAMBaseStorage):
    """Storage pour les images de catégories."""
    location = 'gam/categories'


class VideoThumbnailStorage(GAMBaseStorage):
    """Storage pour les miniatures de vidéos."""
    location = 'gam/videos/thumbnails'


class UserAvatarStorage(GAMBaseStorage):
    """Storage pour les avatars utilisateurs."""
    location = 'gam/users/avatars'