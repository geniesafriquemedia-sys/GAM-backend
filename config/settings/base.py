"""
Django Base Settings for GAM Backend
Génies Afrique Médias - Pan-African Media Platform
"""

from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

# =============================================================================
# PATHS
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# SECURITY
# =============================================================================
SECRET_KEY = config('SECRET_KEY', default='change-me-in-production')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Cloudflare Tunnel Support
# Ajouter les Workers Cloudflare aux hosts autorisés
ALLOWED_HOSTS += [
    'gam-tunnel-front.geniesafriquemedia.workers.dev',
    'gam-tunnel-back.geniesafriquemedia.workers.dev',
    '.trycloudflare.com',  # Tunnels éphémères
    '.workers.dev',  # Tous les workers
]

# Confiance envers le proxy Cloudflare
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CSRF - Origines de confiance pour les tunnels
CSRF_TRUSTED_ORIGINS = [
    'https://gam-tunnel-front.geniesafriquemedia.workers.dev',
    'https://gam-tunnel-back.geniesafriquemedia.workers.dev',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# =============================================================================
# APPLICATIONS
# =============================================================================
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'taggit',
    'modelcluster',
    'cloudinary',
    'cloudinary_storage',
]

# Wagtail CMS Apps
WAGTAIL_APPS = [
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
]

# Apps Core - Fonctionnalités partagées
CORE_APPS = [
    'apps.core',
    'apps.users',
]

# Apps Métier - Domaine business
BUSINESS_APPS = [
    'apps.editorial',
    'apps.engagement',
    'apps.search',
    'apps.kpi',
]

INSTALLED_APPS = DJANGO_APPS + WAGTAIL_APPS + THIRD_PARTY_APPS + CORE_APPS + BUSINESS_APPS

# =============================================================================
# MIDDLEWARE
# =============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

# =============================================================================
# URL CONFIGURATION
# =============================================================================
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# =============================================================================
# TEMPLATES
# =============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# =============================================================================
# DATABASE
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='gam_db'),
        'USER': config('DB_USER', default='gam_user'),
        'PASSWORD': config('DB_PASSWORD', default='gam_password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# =============================================================================
# CACHE (Redis)
# =============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# =============================================================================
# AUTHENTICATION
# =============================================================================
AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Douala'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC & MEDIA FILES
# =============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# CLOUDINARY SETTINGS (Media Storage)
# =============================================================================
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default='dxe2sh4cb'),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

# Utiliser Cloudinary pour le stockage des médias en production
USE_CLOUDINARY = config('USE_CLOUDINARY', default=False, cast=bool)

if USE_CLOUDINARY:
    DEFAULT_FILE_STORAGE = 'apps.core.storage.GAMCloudinaryStorage'


# =============================================================================
# DEFAULT PRIMARY KEY
# =============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# DJANGO REST FRAMEWORK
# =============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'newsletter': '10/hour',  # Limite pour les inscriptions newsletter
        'contact': '5/hour',  # Limite pour les messages de contact
    },
}

# =============================================================================
# JWT SETTINGS
# =============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# =============================================================================
# CORS SETTINGS
# =============================================================================
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)
CORS_ALLOW_CREDENTIALS = True

# CORS - Support des tunnels Cloudflare via regex
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.workers\.dev$",
    r"^https://.*\.trycloudflare\.com$",
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-forwarded-host',
    'x-forwarded-proto',
]

# =============================================================================
# API DOCUMENTATION (drf-spectacular)
# =============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'GAM API - Génies Afrique Médias',
    'DESCRIPTION': 'API Backend pour la plateforme média panafricaine GAM',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Auth', 'description': 'Authentification et gestion des utilisateurs'},
        {'name': 'Articles', 'description': 'Gestion éditoriale des articles'},
        {'name': 'Videos', 'description': 'Gestion Web TV'},
        {'name': 'Categories', 'description': 'Taxonomies et catégories'},
        {'name': 'Authors', 'description': 'Gestion des auteurs'},
        {'name': 'Search', 'description': 'Recherche de contenu'},
        {'name': 'Newsletter', 'description': 'Inscription newsletter'},
    ],
}

# =============================================================================
# EDITORIAL SETTINGS
# =============================================================================
# Temps de lecture moyen (mots par minute)
READING_SPEED_WPM = 200

# Catégories de vidéos par défaut
VIDEO_CATEGORIES = [
    ('emissions', 'Émissions'),
    ('reportages', 'Reportages'),
    ('interviews', 'Interviews'),
    ('documentaires', 'Documentaires'),
]

# =============================================================================
# NEWSLETTER SETTINGS
# =============================================================================
NEWSLETTER_PROVIDER = config('NEWSLETTER_PROVIDER', default='brevo')  # brevo or mailchimp
BREVO_API_KEY = config('BREVO_API_KEY', default='')
BREVO_LIST_ID = config('BREVO_LIST_ID', default='')
MAILCHIMP_API_KEY = config('MAILCHIMP_API_KEY', default='')
MAILCHIMP_LIST_ID = config('MAILCHIMP_LIST_ID', default='')

# Activer l'envoi automatique de newsletters à la publication d'articles
ENABLE_ARTICLE_NOTIFICATIONS = config('ENABLE_ARTICLE_NOTIFICATIONS', default=True, cast=bool)

# URL du frontend pour les liens dans les emails
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')
BACKEND_URL = config('BACKEND_URL', default='http://localhost:8000')

# =============================================================================
# WAGTAIL SETTINGS
# =============================================================================
WAGTAIL_SITE_NAME = 'Génies Afrique Médias'
WAGTAILADMIN_BASE_URL = config('WAGTAILADMIN_BASE_URL', default='http://localhost:8000')

# Utiliser le modèle User personnalisé
WAGTAIL_USER_EDIT_FORM = 'apps.users.forms.CustomUserEditForm'
WAGTAIL_USER_CREATION_FORM = 'apps.users.forms.CustomUserCreationForm'
WAGTAIL_USER_CUSTOM_FIELDS = ['role', 'bio', 'avatar']

# Search backend
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}

# Images
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
WAGTAILIMAGES_MAX_IMAGE_PIXELS = 128000000  # 128 megapixels

# Documents
WAGTAILDOCS_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv']

# Embeds (YouTube, Vimeo, etc.)
WAGTAILEMBEDS_RESPONSIVE_HTML = True

# =============================================================================
# DJANGO TASKS (utilisé par Wagtail pour les tâches asynchrones)
# =============================================================================
# Backend personnalisé pour contourner le bug Python 3.12 avec TaskResult[T]
# En production avec Python < 3.12, utiliser 'django_tasks.backends.database.DatabaseBackend'
TASKS = {
    "default": {
        "BACKEND": "apps.core.tasks_backend.ImmediateBackend",
    }
}
