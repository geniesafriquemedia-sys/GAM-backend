"""
Users URLs - Routes pour l'authentification et les utilisateurs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    RegisterView,
    LogoutView,
    ProfileView,
    PasswordChangeView,
    AdminUserViewSet,
    SessionLoginView,
    SessionLogoutView,
)

app_name = 'users'

# Router pour les viewsets
router = DefaultRouter()
router.register('users', AdminUserViewSet, basename='admin-users')

urlpatterns = [
    # Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),

    # Admin User Management
    path('admin/', include(router.urls)),

    # Session-based auth (for Wagtail CMS)
    path('session/login/', SessionLoginView.as_view(), name='session-login'),
    path('session/logout/', SessionLogoutView.as_view(), name='session-logout'),
]
