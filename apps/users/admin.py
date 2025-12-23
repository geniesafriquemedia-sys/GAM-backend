"""
Users Admin - Configuration de l'administration des utilisateurs
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administration personnalisée des utilisateurs."""

    # Champs affichés dans la liste
    list_display = [
        'email', 'get_full_name', 'role', 'is_active',
        'is_staff', 'avatar_preview', 'created_at'
    ]
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']

    # Configuration des fieldsets pour le formulaire d'édition
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'avatar', 'bio')
        }),
        ('Rôle et permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Dates', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Configuration pour la création d'utilisateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'first_name', 'last_name', 'role', 'is_active', 'is_staff'
            ),
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'last_login']

    def avatar_preview(self, obj):
        """Affiche une miniature de l'avatar."""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.avatar.url
            )
        return '-'
    avatar_preview.short_description = 'Avatar'

    def get_full_name(self, obj):
        """Affiche le nom complet."""
        return obj.get_full_name() or '-'
    get_full_name.short_description = 'Nom complet'

    # Actions personnalisées
    actions = ['activate_users', 'deactivate_users', 'make_editors', 'make_chief_editors']

    @admin.action(description='Activer les utilisateurs sélectionnés')
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} utilisateur(s) activé(s).')

    @admin.action(description='Désactiver les utilisateurs sélectionnés')
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} utilisateur(s) désactivé(s).')

    @admin.action(description='Définir comme Rédacteur')
    def make_editors(self, request, queryset):
        updated = queryset.update(role=User.Role.EDITOR)
        self.message_user(request, f'{updated} utilisateur(s) défini(s) comme rédacteur.')

    @admin.action(description='Définir comme Rédacteur en chef')
    def make_chief_editors(self, request, queryset):
        updated = queryset.update(role=User.Role.CHIEF_EDITOR)
        self.message_user(request, f'{updated} utilisateur(s) défini(s) comme rédacteur en chef.')
