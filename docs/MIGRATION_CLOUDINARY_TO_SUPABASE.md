# Migration du stockage médias : Cloudinary → Supabase Storage

**Date :** 2026-02-24
**Statut :** À implémenter
**Projet :** GAM Backend (Django/Wagtail)

---

## Contexte

Le stockage des médias (images d'articles, photos d'auteurs, miniatures vidéos, avatars) est actuellement sur **Cloudinary**. On migre vers **Supabase Storage** (plan Pro) qui est compatible S3, donc utilisable directement avec `django-storages` déjà présent dans le projet.

---

## Architecture actuelle (Cloudinary)

```
apps/core/storage.py         ← Backends Cloudinary personnalisés
config/settings/base.py      ← CLOUDINARY_STORAGE, USE_CLOUDINARY
config/settings/production.py ← USE_S3 (inactif)
```

**Variables d'env actuelles :**
```
USE_CLOUDINARY=True
CLOUDINARY_CLOUD_NAME=dxe2sh4cb
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

**Chemins de stockage :**
| Usage                  | Chemin Cloudinary               |
|------------------------|---------------------------------|
| Images articles        | `gam/articles/`                 |
| Photos auteurs         | `gam/authors/`                  |
| Images catégories      | `gam/categories/`               |
| Miniatures vidéos      | `gam/videos/thumbnails/`        |
| Avatars utilisateurs   | `gam/users/avatars/`            |

---

## Architecture cible (Supabase Storage)

Supabase Storage expose une **API S3 compatible**. On utilise `django-storages` (déjà installé) avec `S3Boto3Storage`, ce qui évite d'ajouter de nouvelles dépendances.

**URL publique :** `https://<ref>.supabase.co/storage/v1/object/public/<bucket>/<path>`

---

## Étapes de migration

### 1. Récupérer les credentials Supabase S3

Dans le dashboard Supabase → **Storage** → **S3 Connection** :

| Variable              | Où trouver                                      |
|-----------------------|-------------------------------------------------|
| `SUPABASE_URL`        | Settings → API → Project URL                   |
| `SUPABASE_S3_REGION`  | Storage → S3 Connection → Region (`eu-west-3`) |
| `SUPABASE_S3_ENDPOINT`| `https://<ref>.supabase.co/storage/v1/s3`      |
| `SUPABASE_S3_KEY`     | Storage → S3 Connection → Access Key ID        |
| `SUPABASE_S3_SECRET`  | Storage → S3 Connection → Secret Access Key    |

### 2. Créer le bucket Supabase

Dans Supabase → Storage → **New bucket** :
- Nom : `gam-media`
- **Public** : ✅ (pour que les images soient accessibles sans auth)
- Policies : lecture publique, écriture authentifiée

### 3. Mettre à jour les dépendances

**`requirements/base.txt`** — aucun changement requis (`django-storages` et `boto3` sont déjà présents). Supprimer les dépendances Cloudinary devenues inutiles :

```diff
- cloudinary>=1.36,<2.0
- django-cloudinary-storage>=0.3,<1.0
```

### 4. Mettre à jour `apps/core/storage.py`

Remplacer tous les backends `MediaCloudinaryStorage` par des backends `S3Boto3Storage` avec préfixes de dossiers :

```python
# apps/core/storage.py
from storages.backends.s3boto3 import S3Boto3Storage

class GAMBaseStorage(S3Boto3Storage):
    """Storage de base Supabase pour GAM."""
    bucket_name = 'gam-media'
    file_overwrite = False
    default_acl = 'public-read'

class ArticleImageStorage(GAMBaseStorage):
    location = 'gam/articles'

class AuthorPhotoStorage(GAMBaseStorage):
    location = 'gam/authors'

class CategoryImageStorage(GAMBaseStorage):
    location = 'gam/categories'

class VideoThumbnailStorage(GAMBaseStorage):
    location = 'gam/videos/thumbnails'

class UserAvatarStorage(GAMBaseStorage):
    location = 'gam/users/avatars'
```

### 5. Mettre à jour `config/settings/base.py`

Remplacer le bloc Cloudinary :

```python
# AVANT
CLOUDINARY_STORAGE = { ... }
USE_CLOUDINARY = config('USE_CLOUDINARY', default=False, cast=bool)
if USE_CLOUDINARY:
    DEFAULT_FILE_STORAGE = 'apps.core.storage.GAMCloudinaryStorage'

# APRÈS
USE_SUPABASE = config('USE_SUPABASE', default=False, cast=bool)

if USE_SUPABASE:
    AWS_ACCESS_KEY_ID = config('SUPABASE_S3_KEY')
    AWS_SECRET_ACCESS_KEY = config('SUPABASE_S3_SECRET')
    AWS_STORAGE_BUCKET_NAME = 'gam-media'
    AWS_S3_REGION_NAME = config('SUPABASE_S3_REGION', default='eu-west-3')
    AWS_S3_ENDPOINT_URL = config('SUPABASE_S3_ENDPOINT')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False  # URLs publiques sans signature
    SUPABASE_URL = config('SUPABASE_URL')
    MEDIA_URL = f"{SUPABASE_URL}/storage/v1/object/public/gam-media/"
    DEFAULT_FILE_STORAGE = 'apps.core.storage.GAMBaseStorage'
```

### 6. Mettre à jour les variables d'environnement Railway

**Supprimer :**
```
USE_CLOUDINARY
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
```

**Ajouter :**
```
USE_SUPABASE=True
SUPABASE_URL=https://<ref>.supabase.co
SUPABASE_S3_ENDPOINT=https://<ref>.supabase.co/storage/v1/s3
SUPABASE_S3_REGION=eu-west-3
SUPABASE_S3_KEY=<access-key-id>
SUPABASE_S3_SECRET=<secret-access-key>
```

### 7. Mettre à jour le frontend (Railway)

```
NEXT_PUBLIC_MEDIA_URL=https://<ref>.supabase.co/storage/v1/object/public/gam-media
```

### 8. Migration des images existantes (Cloudinary → Supabase)

Écrire une commande de management Django pour migrer les fichiers :

```bash
python manage.py migrate_to_supabase --dry-run   # Prévisualiser
python manage.py migrate_to_supabase              # Exécuter
```

La commande doit :
1. Lister tous les articles/auteurs/catégories avec des images
2. Télécharger chaque image depuis Cloudinary
3. La re-uploader dans Supabase avec le même chemin
4. Mettre à jour le champ en base de données si l'URL change

---

## Fichiers à modifier

| Fichier                               | Action                                      |
|---------------------------------------|---------------------------------------------|
| `requirements/base.txt`              | Supprimer cloudinary, django-cloudinary-storage |
| `apps/core/storage.py`               | Réécrire avec S3Boto3Storage               |
| `config/settings/base.py`            | Remplacer bloc Cloudinary par Supabase      |
| `config/settings/production.py`      | Supprimer le bloc USE_S3 redondant          |
| Railway env vars (backend)            | Nouvelles variables Supabase                |
| Railway env vars (frontend)           | Mettre à jour NEXT_PUBLIC_MEDIA_URL         |

---

## Points d'attention

### URLs des images existantes
Les images en base de données ont des URLs Cloudinary (`res.cloudinary.com/...`). Après migration :
- Les **nouvelles** images iront sur Supabase automatiquement
- Les **anciennes** images resteront accessibles via Cloudinary tant que le compte est actif
- Prévoir la commande de migration pour transférer les anciennes images

### Pas de transformation d'images
Cloudinary offre des transformations à la volée (redimensionnement via URL). Supabase Storage ne le fait pas nativement. Solutions :
- **Option A :** Utiliser `next/image` qui optimise déjà les images côté frontend
- **Option B :** Ajouter Imgproxy ou Cloudflare Image Resizing si nécessaire

### Politique du bucket
Le bucket doit être **public** pour que le frontend puisse afficher les images sans token d'authentification.

---

## Ordre d'implémentation recommandé

1. ✅ Créer le bucket `gam-media` dans Supabase (public)
2. ✅ Récupérer les credentials S3 Supabase
3. ✅ Modifier `storage.py`
4. ✅ Modifier `settings/base.py`
5. ✅ Mettre à jour `requirements/base.txt`
6. ✅ Mettre à jour les variables Railway (backend + frontend)
7. ✅ Déployer et tester l'upload d'une nouvelle image
8. ✅ Écrire et exécuter la commande de migration des images existantes
