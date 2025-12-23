# GAM Backend - Génies Afrique Médias

Backend API Django REST pour la plateforme média panafricaine GAM.

## 🏗️ Architecture

Le projet est organisé selon une architecture modulaire avec séparation claire entre :

### Apps Core (Fonctionnalités partagées)
- **`apps.core`** - Modèles de base, permissions, utilitaires
- **`apps.users`** - Gestion des utilisateurs et authentification JWT

### Apps Métier (Domaine business)
- **`apps.editorial`** - Gestion éditoriale (articles, catégories, auteurs, vidéos)
- **`apps.engagement`** - Engagement utilisateur (newsletter, contact)
- **`apps.search`** - Recherche de contenu

## 📋 User Stories Implémentées

| US | Description | Status |
|----|-------------|--------|
| US-01 | Gestion des taxonomies (Auteurs & Catégories) | ✅ |
| US-02 | Rédaction d'article riche (blocs dynamiques) | ✅ |
| US-03 | Gestion des vidéos Web TV (YouTube) | ✅ |
| US-04 | Workflow de publication | ✅ |
| US-05 | Page d'accueil dynamique | ✅ |
| US-06 | Lecture d'article | ✅ |
| US-07 | Consultation Web TV | ✅ |
| US-08 | Recherche de contenu | ✅ |
| US-10 | Inscription à la newsletter | ✅ |

## 🚀 Installation

### Prérequis
- Python 3.11+
- PostgreSQL 15+ (production)
- Redis (pour le cache)

### Setup

```bash
# Cloner et créer l'environnement virtuel
cd GAM-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements/development.txt

# Configuration environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# Migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema OpenAPI**: http://localhost:8000/api/schema/

## 🔐 Authentification

L'API utilise JWT (JSON Web Tokens) pour l'authentification.

```bash
# Obtenir un token
POST /api/v1/auth/login/
{
    "email": "user@example.com",
    "password": "password"
}

# Utiliser le token
Authorization: Bearer <access_token>

# Rafraîchir le token
POST /api/v1/auth/refresh/
{
    "refresh": "<refresh_token>"
}
```

## 📡 Endpoints API

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login/` | Connexion |
| POST | `/api/v1/auth/register/` | Inscription |
| POST | `/api/v1/auth/logout/` | Déconnexion |
| POST | `/api/v1/auth/refresh/` | Rafraîchir token |
| GET | `/api/v1/auth/profile/` | Profil utilisateur |

### Editorial
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/editorial/articles/` | Liste articles |
| GET | `/api/v1/editorial/articles/{slug}/` | Détail article |
| GET | `/api/v1/editorial/articles/featured/` | Articles à la Une |
| GET | `/api/v1/editorial/videos/` | Liste vidéos |
| GET | `/api/v1/editorial/videos/featured/` | Vidéos en vedette |
| GET | `/api/v1/editorial/categories/` | Catégories |
| GET | `/api/v1/editorial/authors/` | Auteurs |
| GET | `/api/v1/editorial/homepage/` | Données page d'accueil |

### Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/search/?q=query` | Recherche |
| GET | `/api/v1/search/suggestions/?q=query` | Suggestions |
| GET | `/api/v1/search/trending-tags/` | Tags populaires |

### Engagement
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/engagement/newsletter/subscribe/` | Inscription newsletter |
| POST | `/api/v1/engagement/contact/` | Message contact |

## 🔧 Configuration

### Variables d'environnement

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=gam_db
DB_USER=gam_user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://127.0.0.1:6379/1

# Newsletter (brevo ou mailchimp)
NEWSLETTER_PROVIDER=brevo
BREVO_API_KEY=your-api-key
BREVO_LIST_ID=your-list-id
```

## 🧪 Tests

```bash
# Lancer les tests
pytest

# Avec couverture
pytest --cov=apps --cov-report=html
```

## 📦 Structure du Projet

```
GAM-backend/
├── config/
│   ├── settings/
│   │   ├── base.py          # Settings communs
│   │   ├── development.py   # Dev settings
│   │   └── production.py    # Prod settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/                 # App Core
│   │   ├── models.py        # Modèles de base
│   │   ├── permissions.py   # Permissions custom
│   │   ├── utils.py         # Utilitaires
│   │   └── mixins.py        # Mixins réutilisables
│   ├── users/                # Utilisateurs
│   │   ├── models.py        # User model
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── admin.py
│   ├── editorial/            # Éditorial
│   │   ├── models/
│   │   │   ├── article.py   # Articles + blocs
│   │   │   ├── video.py     # Vidéos Web TV
│   │   │   ├── category.py  # Catégories
│   │   │   └── author.py    # Auteurs
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── filters.py
│   │   └── admin.py
│   ├── engagement/           # Engagement
│   │   ├── models.py        # Newsletter, Contact
│   │   ├── services.py      # Brevo/Mailchimp
│   │   ├── serializers.py
│   │   └── views.py
│   └── search/               # Recherche
│       ├── services.py      # Logique de recherche
│       ├── views.py
│       └── urls.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── manage.py
└── .env.example
```

## 🚀 Déploiement Production

```bash
# Installer les dépendances production
pip install -r requirements/production.txt

# Collecter les fichiers statiques
python manage.py collectstatic

# Migrer la base de données
python manage.py migrate

# Lancer avec Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 📄 Licence

Propriétaire - GAM © 2024
