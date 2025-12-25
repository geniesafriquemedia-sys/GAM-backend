"""
Users Views - Vues pour l'authentification et la gestion des utilisateurs
"""

from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, login as django_login, logout as django_logout
from drf_spectacular.utils import extend_schema, extend_schema_view

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    AdminUserSerializer,
    AdminUserCreateSerializer,
)

User = get_user_model()


# =============================================================================
# AUTHENTICATION VIEWS
# =============================================================================

@extend_schema(tags=['Auth'])
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Obtention d'un token JWT.
    Retourne access token, refresh token et informations utilisateur.
    Crée également une session Django pour accéder à Wagtail CMS.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Appel de la méthode parente pour obtenir les tokens JWT
        response = super().post(request, *args, **kwargs)

        # Si l'authentification a réussi, créer une session Django
        if response.status_code == 200:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user

            # Créer la session Django pour Wagtail CMS
            django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return response


@extend_schema(tags=['Auth'])
class CustomTokenRefreshView(TokenRefreshView):
    """Rafraîchissement du token JWT."""
    pass


@extend_schema(tags=['Auth'])
class RegisterView(generics.CreateAPIView):
    """
    Inscription d'un nouvel utilisateur.
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Générer les tokens pour l'utilisateur créé
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Auth'])
class LogoutView(generics.GenericAPIView):
    """
    Déconnexion - Blacklist le refresh token et détruit la session Django.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Blacklist le refresh token JWT
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            # Détruire la session Django (déconnexion Wagtail)
            django_logout(request)

            return Response(
                {'message': 'Déconnexion réussie'},
                status=status.HTTP_200_OK
            )
        except Exception:
            # Même en cas d'erreur JWT, déconnecter la session Django
            django_logout(request)
            return Response(
                {'error': 'Token invalide, mais session Django fermée'},
                status=status.HTTP_400_BAD_REQUEST
            )


# =============================================================================
# USER PROFILE VIEWS
# =============================================================================

@extend_schema(tags=['Auth'])
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Récupération et mise à jour du profil de l'utilisateur connecté.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Auth'])
class PasswordChangeView(generics.GenericAPIView):
    """
    Changement de mot de passe.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'message': 'Mot de passe modifié avec succès'},
            status=status.HTTP_200_OK
        )


# =============================================================================
# ADMIN USER MANAGEMENT VIEWS
# =============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Admin - Users']),
    create=extend_schema(tags=['Admin - Users']),
    retrieve=extend_schema(tags=['Admin - Users']),
    update=extend_schema(tags=['Admin - Users']),
    partial_update=extend_schema(tags=['Admin - Users']),
    destroy=extend_schema(tags=['Admin - Users']),
)
class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Gestion des utilisateurs (administration).
    Réservé aux administrateurs.
    """
    queryset = User.objects.all().order_by('-created_at')
    permission_classes = [IsAdminUser]
    filterset_fields = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'last_login', 'email']

    def get_serializer_class(self):
        if self.action == 'create':
            return AdminUserCreateSerializer
        return AdminUserSerializer

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Active un utilisateur."""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'message': 'Utilisateur activé'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Désactive un utilisateur."""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'message': 'Utilisateur désactivé'})

    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """Change le rôle d'un utilisateur."""
        user = self.get_object()
        new_role = request.data.get('role')

        if new_role not in dict(User.Role.choices):
            return Response(
                {'error': 'Rôle invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.role = new_role
        user.save()

        return Response({
            'message': f'Rôle modifié en {user.get_role_display()}',
            'user': AdminUserSerializer(user).data
        })


# =============================================================================
# SESSION LOGIN VIEW (for Wagtail CMS access)
# =============================================================================

from django.views import View
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings


@method_decorator(csrf_exempt, name='dispatch')
class SessionLoginView(View):
    """
    Vue de connexion par session Django.
    Authentifie l'utilisateur et redirige vers Wagtail CMS.
    """

    def post(self, request):
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', '/cms/')

        user = authenticate(request, username=email, password=password)

        if user is not None and user.is_active:
            django_login(request, user)
            return HttpResponseRedirect(next_url)
        else:
            # Rediriger vers la page login frontend avec erreur
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            return HttpResponseRedirect(f'{frontend_url}/login?error=invalid_credentials')

    def get(self, request):
        # Rediriger GET vers la page login frontend
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return HttpResponseRedirect(f'{frontend_url}/login')


class SessionLogoutView(View):
    """
    Vue de déconnexion.
    Détruit la session et redirige vers la page login frontend.
    """

    def get(self, request):
        django_logout(request)
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return HttpResponseRedirect(f'{frontend_url}/login')

    def post(self, request):
        return self.get(request)
