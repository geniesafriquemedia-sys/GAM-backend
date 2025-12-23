"""
Core Permissions - Permissions personnalisées pour l'API
"""

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permet l'accès en lecture à tous, modification uniquement pour les admins.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsEditorOrReadOnly(permissions.BasePermission):
    """
    Permet l'accès en lecture à tous, modification pour les éditeurs.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_editor


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permet la modification uniquement par le propriétaire de l'objet.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Vérifie si l'objet a un champ 'author' ou 'user' ou 'owner'
        owner = getattr(obj, 'author', None) or getattr(obj, 'user', None) or getattr(obj, 'owner', None)
        return owner == request.user


class IsEditorOrOwner(permissions.BasePermission):
    """
    Permet la modification par les éditeurs ou le propriétaire.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_staff or request.user.is_editor:
            return True

        owner = getattr(obj, 'author', None) or getattr(obj, 'user', None)
        return owner == request.user


class CanPublish(permissions.BasePermission):
    """
    Vérifie si l'utilisateur peut publier du contenu (Rédacteur en chef ou Admin).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        # Seuls les admins et rédacteurs en chef peuvent publier
        return request.user.is_staff or request.user.is_chief_editor
