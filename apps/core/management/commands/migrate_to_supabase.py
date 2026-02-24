"""
Commande de migration des images Cloudinary → Supabase Storage.

Usage :
    python manage.py migrate_to_supabase --dry-run     # Prévisualiser sans modifier
    python manage.py migrate_to_supabase               # Migrer tout
    python manage.py migrate_to_supabase --model article
    python manage.py migrate_to_supabase --model author
    python manage.py migrate_to_supabase --model category
    python manage.py migrate_to_supabase --model video
    python manage.py migrate_to_supabase --model user
"""

import requests
import boto3
from botocore.exceptions import ClientError

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from decouple import config as env_config


# ─── Correspondance modèles → champs images ──────────────────────────────────

MODEL_MAP = {
    'article':  ('apps.editorial.models.Article',  'featured_image'),
    'author':   ('apps.editorial.models.Author',   'photo'),
    'category': ('apps.editorial.models.Category', 'image'),
    'video':    ('apps.editorial.models.Video',    'thumbnail'),
    'user':     ('apps.users.models.User',         'avatar'),
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def get_model(dotted_path):
    """Importe dynamiquement un modèle Django depuis son chemin pointé."""
    parts = dotted_path.rsplit('.', 1)
    module = __import__(parts[0], fromlist=[parts[1]])
    return getattr(module, parts[1])


def build_cloudinary_url(name: str, cloud_name: str) -> str:
    """Construit l'URL publique Cloudinary pour un nom de fichier stocké."""
    return f"https://res.cloudinary.com/{cloud_name}/image/upload/{name}"


def get_s3_client():
    """Retourne un client boto3 configuré pour Supabase S3."""
    return boto3.client(
        's3',
        region_name=settings.AWS_S3_REGION_NAME,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def file_exists_on_supabase(s3_client, key: str) -> bool:
    """Vérifie si un fichier existe déjà dans le bucket Supabase."""
    try:
        s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise


def download_from_cloudinary(url: str) -> bytes | None:
    """Télécharge une image Cloudinary. Retourne None si inaccessible."""
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return resp.content
        return None
    except requests.RequestException:
        return None


def upload_to_supabase(s3_client, key: str, content: bytes, content_type: str = 'image/jpeg'):
    """Upload un fichier dans le bucket Supabase S3."""
    s3_client.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        Body=content,
        ContentType=content_type,
    )


def guess_content_type(name: str) -> str:
    """Déduit le Content-Type depuis l'extension du fichier."""
    name_lower = name.lower()
    if name_lower.endswith('.png'):
        return 'image/png'
    if name_lower.endswith('.gif'):
        return 'image/gif'
    if name_lower.endswith('.webp'):
        return 'image/webp'
    if name_lower.endswith('.svg'):
        return 'image/svg+xml'
    return 'image/jpeg'


# ─── Commande principale ──────────────────────────────────────────────────────

class Command(BaseCommand):
    help = 'Migre les images Cloudinary vers Supabase Storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui serait migré sans rien modifier',
        )
        parser.add_argument(
            '--model',
            type=str,
            choices=list(MODEL_MAP.keys()),
            help='Migrer uniquement ce modèle (article, author, category, video, user)',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            default=True,
            help='Ignorer les fichiers déjà présents sur Supabase (défaut: activé)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        model_filter = options.get('model')
        skip_existing = options['skip_existing']

        # Vérification des settings Supabase
        cloud_name = self._check_settings()

        if dry_run:
            self.stdout.write(self.style.WARNING('=== MODE DRY-RUN : aucune modification ===\n'))

        s3_client = None if dry_run else get_s3_client()

        # Sélection des modèles à migrer
        models_to_migrate = (
            {model_filter: MODEL_MAP[model_filter]}
            if model_filter
            else MODEL_MAP
        )

        total_migrated = 0
        total_skipped = 0
        total_missing = 0
        total_errors = 0

        for key, (model_path, field_name) in models_to_migrate.items():
            m, s, e = self._migrate_model(
                key, model_path, field_name,
                s3_client, dry_run, skip_existing, cloud_name,
            )
            total_migrated += m
            total_skipped += s
            total_errors += e

        # Résumé final
        self.stdout.write('\n' + '─' * 50)
        self.stdout.write(self.style.SUCCESS(f'✅ Migrés   : {total_migrated}'))
        self.stdout.write(self.style.WARNING(f'⏭  Ignorés  : {total_skipped}'))
        self.stdout.write(self.style.ERROR(f'❌ Erreurs  : {total_errors}'))

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\nDry-run terminé. Relancez sans --dry-run pour appliquer.'
            ))

    def _check_settings(self) -> str:
        """Vérifie que tous les paramètres requis sont présents. Retourne le cloud_name Cloudinary."""
        required = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_STORAGE_BUCKET_NAME',
            'AWS_S3_ENDPOINT_URL',
            'AWS_S3_REGION_NAME',
        ]
        missing = [s for s in required if not getattr(settings, s, None)]
        if missing:
            raise CommandError(
                f"Paramètres Supabase manquants dans les settings : {', '.join(missing)}\n"
                "Vérifiez USE_SUPABASE=True et les variables SUPABASE_* dans Railway."
            )

        # Cloud name Cloudinary : depuis settings ou env var directement (transition)
        cloud_name = (
            getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME')
            or env_config('CLOUDINARY_CLOUD_NAME', default='')
        )
        if not cloud_name:
            raise CommandError(
                "CLOUDINARY_CLOUD_NAME introuvable.\n"
                "Ajoutez CLOUDINARY_CLOUD_NAME dans les variables d'environnement "
                "pendant la période de migration."
            )
        return cloud_name

    def _migrate_model(self, label, model_path, field_name, s3_client, dry_run, skip_existing, cloud_name):
        """Migre toutes les images d'un modèle donné."""
        self.stdout.write(f'\n📦 {label.upper()} → champ `{field_name}`')

        Model = get_model(model_path)
        # Seulement les objets avec une image non vide
        qs = Model.objects.exclude(**{f'{field_name}__isnull': True}).exclude(
            **{f'{field_name}__exact': ''}
        )

        count = qs.count()
        self.stdout.write(f'   {count} objet(s) avec image trouvé(s)')

        migrated = skipped = errors = 0

        for obj in qs.iterator():
            field_value = getattr(obj, field_name)
            stored_name = field_value.name  # Chemin stocké en base (ex: articles/featured/img.jpg)

            if not stored_name:
                continue

            cloudinary_url = build_cloudinary_url(stored_name, cloud_name)

            # Vérifier si déjà sur Supabase
            if not dry_run and skip_existing:
                if file_exists_on_supabase(s3_client, stored_name):
                    self.stdout.write(
                        f'   ⏭  [{label} id={obj.pk}] déjà sur Supabase : {stored_name}'
                    )
                    skipped += 1
                    continue

            if dry_run:
                self.stdout.write(
                    f'   🔍 [{label} id={obj.pk}] {stored_name}\n'
                    f'      Cloudinary : {cloudinary_url}'
                )
                migrated += 1
                continue

            # Téléchargement depuis Cloudinary
            content = download_from_cloudinary(cloudinary_url)
            if content is None:
                self.stdout.write(
                    self.style.WARNING(
                        f'   ⚠️  [{label} id={obj.pk}] introuvable sur Cloudinary : {cloudinary_url}'
                    )
                )
                errors += 1
                continue

            # Upload vers Supabase
            try:
                content_type = guess_content_type(stored_name)
                upload_to_supabase(s3_client, stored_name, content, content_type)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'   ✅ [{label} id={obj.pk}] {stored_name} ({len(content) // 1024} Ko)'
                    )
                )
                migrated += 1
            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f'   ❌ [{label} id={obj.pk}] erreur upload : {exc}'
                    )
                )
                errors += 1

        return migrated, skipped, errors