"""
User Forms - Formulaires personnalisés pour Wagtail
"""

from django import forms
from wagtail.users.forms import UserEditForm, UserCreationForm
from .models import User


class CustomUserEditForm(UserEditForm):
    """Formulaire d'édition utilisateur personnalisé pour Wagtail."""

    role = forms.ChoiceField(
        choices=User.Role.choices,
        required=True,
        label='Rôle'
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Biographie'
    )
    avatar = forms.ImageField(
        required=False,
        label='Avatar'
    )


class CustomUserCreationForm(UserCreationForm):
    """Formulaire de création utilisateur personnalisé pour Wagtail."""

    role = forms.ChoiceField(
        choices=User.Role.choices,
        required=True,
        label='Rôle',
        initial=User.Role.VIEWER
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Biographie'
    )
    avatar = forms.ImageField(
        required=False,
        label='Avatar'
    )
