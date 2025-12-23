"""
Django Development Settings for GAM Backend
"""

from .base import *

# =============================================================================
# DEBUG
# =============================================================================
DEBUG = True

# =============================================================================
# ALLOWED HOSTS
# =============================================================================
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# =============================================================================
# DATABASE (PostgreSQL Supabase - uses .env configuration from base.py)
# =============================================================================
# La configuration de la base de données est héritée de base.py
# qui utilise les variables d'environnement du fichier .env

# =============================================================================
# CACHE (Local Memory for development)
# =============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# =============================================================================
# EMAIL (Console for development)
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# DEBUG TOOLBAR
# =============================================================================
INSTALLED_APPS += ['debug_toolbar', 'django_extensions']
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ['127.0.0.1']

# =============================================================================
# CORS (Allow all in development)
# =============================================================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# SESSION & CSRF COOKIES (Cross-Origin pour frontend Next.js)
# =============================================================================
# Permet aux cookies de session d'être envoyés cross-origin
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True

# CSRF settings pour cross-origin
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# =============================================================================
# STATIC & MEDIA
# =============================================================================
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# =============================================================================
# LOGGING
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

