"""
Wagtail Hooks - Enregistrement du CustomUserViewSet
"""

from wagtail import hooks
from .viewsets import CustomUserViewSet


@hooks.register("register_user_viewset")
def register_user_viewset():
    return CustomUserViewSet("users")
