"""
Management command to download external images to Cloudinary.
Downloads images from external_image_url and stores them in Cloudinary.
"""

import requests
from io import BytesIO
from django.core.management.base import BaseCommand
from django.conf import settings
import cloudinary
import cloudinary.uploader

from apps.editorial.models import Article


class Command(BaseCommand):
    help = 'Download external images to Cloudinary and update articles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be downloaded without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN MODE ===\n'))

        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
            api_key=settings.CLOUDINARY_STORAGE.get('API_KEY'),
            api_secret=settings.CLOUDINARY_STORAGE.get('API_SECRET'),
        )

        self.stdout.write('Downloading external images to Cloudinary...\n')

        # Find articles with external_image_url but no featured_image
        articles = Article.objects.exclude(
            external_image_url__isnull=True
        ).exclude(
            external_image_url=''
        )

        success_count = 0
        error_count = 0
        skipped_count = 0

        for article in articles:
            # Skip if already has a Cloudinary image
            if article.featured_image and 'gam/' in str(article.featured_image.name):
                self.stdout.write(f'  [SKIP] {article.id}: Already has Cloudinary image')
                skipped_count += 1
                continue

            self.stdout.write(f'  [{article.id}] {article.title[:50]}...')
            self.stdout.write(f'      URL: {article.external_image_url[:60]}...')

            if dry_run:
                success_count += 1
                continue

            try:
                # Download image
                response = requests.get(
                    article.external_image_url,
                    timeout=30,
                    headers={'User-Agent': 'GAM Media Bot/1.0'}
                )
                response.raise_for_status()

                # Determine format from content-type or URL
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = 'jpg'
                elif 'png' in content_type:
                    ext = 'png'
                elif 'webp' in content_type:
                    ext = 'webp'
                elif 'avif' in content_type:
                    ext = 'avif'
                else:
                    # Try to get from URL
                    url_lower = article.external_image_url.lower()
                    if '.png' in url_lower:
                        ext = 'png'
                    elif '.webp' in url_lower:
                        ext = 'webp'
                    else:
                        ext = 'jpg'

                # Upload to Cloudinary
                public_id = f'gam/articles/featured/article_{article.id}'

                result = cloudinary.uploader.upload(
                    BytesIO(response.content),
                    public_id=public_id,
                    folder='',  # Already in public_id
                    overwrite=True,
                    resource_type='image',
                    format=ext,
                )

                # Update article
                new_path = f"{public_id}.{result.get('format', ext)}"
                article.featured_image = new_path
                article.save(update_fields=['featured_image'])

                self.stdout.write(self.style.SUCCESS(f'      -> Uploaded: {new_path}'))
                success_count += 1

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f'      -> Download error: {e}'))
                error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'      -> Upload error: {e}'))
                error_count += 1

        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('Summary:'))
        self.stdout.write(f'  Success: {success_count}')
        self.stdout.write(f'  Skipped: {skipped_count}')
        self.stdout.write(f'  Errors:  {error_count}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a dry run. No images were downloaded.'))
            self.stdout.write('Run without --dry-run to perform the actual download.')
