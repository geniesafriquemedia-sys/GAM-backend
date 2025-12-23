"""
URL Configuration for GAM Backend
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

# =============================================================================
# API URL PATTERNS
# =============================================================================
api_v1_patterns = [
    # Auth & Users
    path('auth/', include('apps.users.urls')),

    # Editorial (Articles, Videos, Categories, Authors)
    path('editorial/', include('apps.editorial.urls')),

    # Engagement (Newsletter)
    path('engagement/', include('apps.engagement.urls')),

    # Search
    path('search/', include('apps.search.urls')),
]

# =============================================================================
# MAIN URL PATTERNS
# =============================================================================
urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Wagtail CMS Admin
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    # API v1
    path('api/v1/', include(api_v1_patterns)),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Wagtail pages (catch-all, doit être en dernier)
    path('', include(wagtail_urls)),
]

# =============================================================================
# STATIC & MEDIA (Development)
# =============================================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug Toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# =============================================================================
# ADMIN CUSTOMIZATION
# =============================================================================
admin.site.site_header = 'GAM - Administration'
admin.site.site_title = 'GAM Admin'
admin.site.index_title = 'Génies Afrique Médias - Back Office'
