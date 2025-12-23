"""
Users Serializers - Sérialiseurs pour l'authentification et les utilisateurs
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personnalisé pour JWT.
    Ajoute les informations utilisateur au token.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Ajouter des claims personnalisés
        token['email'] = user.email
        token['full_name'] = user.get_full_name()
        token['role'] = user.role

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Ajouter les informations utilisateur à la réponse
        data['user'] = UserSerializer(self.user).data

        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les informations utilisateur."""

    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'avatar', 'bio', 'role', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'role', 'is_active', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'utilisateur (inscription)."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas.'
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour du profil."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'avatar', 'bio']


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer pour le changement de mot de passe."""

    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Le mot de passe actuel est incorrect.')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Les nouveaux mots de passe ne correspondent pas.'
            })
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer pour la gestion des utilisateurs (admin)."""

    full_name = serializers.CharField(source='get_full_name', read_only=True)
    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'avatar', 'bio', 'role', 'is_active', 'is_staff',
            'created_at', 'last_login', 'articles_count'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']

    def get_articles_count(self, obj):
        """Compte le nombre d'articles de l'utilisateur."""
        if hasattr(obj, 'articles'):
            return obj.articles.count()
        return 0


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'utilisateur par un admin."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'email', 'password', 'first_name', 'last_name',
            'avatar', 'bio', 'role', 'is_active', 'is_staff'
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
