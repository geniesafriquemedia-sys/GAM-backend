"""
Users Models - Modèle utilisateur personnalisé
Gestion des rôles : Administrateur, Rédacteur en chef, Rédacteur (US-01, US-04)
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User."""

    def create_user(self, email, password=None, **extra_fields):
        """Crée et retourne un utilisateur standard."""
        if not email:
            raise ValueError('L\'adresse email est obligatoire')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Crée et retourne un superutilisateur."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, TimeStampedModel):
    """
    Modèle utilisateur personnalisé.
    Utilise l'email comme identifiant principal.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrateur'
        CHIEF_EDITOR = 'chief_editor', 'Rédacteur en chef'
        EDITOR = 'editor', 'Rédacteur'
        VIEWER = 'viewer', 'Lecteur'

    # Supprimer le champ username et utiliser email
    username = None
    email = models.EmailField(
        'Adresse email',
        unique=True,
        db_index=True
    )

    # Informations personnelles
    first_name = models.CharField('Prénom', max_length=150)
    last_name = models.CharField('Nom', max_length=150)
    avatar = models.ImageField(
        'Avatar',
        upload_to='users/avatars/',
        blank=True,
        null=True
    )
    bio = models.TextField(
        'Biographie',
        blank=True,
        max_length=500
    )

    # Rôle dans la plateforme
    role = models.CharField(
        'Rôle',
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        db_index=True
    )

    # Configuration du manager et du champ d'authentification
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-created_at']

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        """Retourne le nom complet."""
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        """Retourne le prénom."""
        return self.first_name

    # ==========================================================================
    # Propriétés de rôle
    # ==========================================================================

    @property
    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est administrateur."""
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_chief_editor(self) -> bool:
        """Vérifie si l'utilisateur est rédacteur en chef."""
        return self.role == self.Role.CHIEF_EDITOR or self.is_admin

    @property
    def is_editor(self) -> bool:
        """Vérifie si l'utilisateur est rédacteur (ou rôle supérieur)."""
        return self.role in [self.Role.EDITOR, self.Role.CHIEF_EDITOR, self.Role.ADMIN] or self.is_superuser

    @property
    def can_publish(self) -> bool:
        """Vérifie si l'utilisateur peut publier du contenu (US-04)."""
        return self.is_chief_editor

    @property
    def can_edit_content(self) -> bool:
        """Vérifie si l'utilisateur peut éditer du contenu."""
        return self.is_editor
