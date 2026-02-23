"""
User ViewSet - Remplacement des settings dépréciés Wagtail 7.x
"""

from wagtail.users.views.users import UserViewSet as WagtailUserViewSet
from .forms import CustomUserEditForm, CustomUserCreationForm


class CustomUserViewSet(WagtailUserViewSet):
    """
    ViewSet personnalisé pour remplacer WAGTAIL_USER_CREATION_FORM,
    WAGTAIL_USER_EDIT_FORM et WAGTAIL_USER_CUSTOM_FIELDS (dépréciés en Wagtail 7.x).
    """

    def get_form_class(self, for_update=False):
        if for_update:
            return CustomUserEditForm
        return CustomUserCreationForm
