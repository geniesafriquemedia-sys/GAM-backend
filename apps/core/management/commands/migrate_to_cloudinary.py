"""
Management command to migrate existing media files to Cloudinary.
Transfers all local media files to Cloudinary and updates database references.
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import models
import cloudinary
import cloudinary.uploader

from apps.editorial.models import Article, Author, Category, Video
from apps.users.models import User


class Command(BaseCommand):
    help = 'Migrate existing media files from local storage to Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN MODE ==='))

        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
            api_key=settings.CLOUDINARY_STORAGE.get('API_KEY'),
            api_secret=settings.CLOUDINARY_STORAGE.get('API_SECRET'),
        )

        self.stdout.write('Starting migration to Cloudinary...\n')

        # Migrate each model's images
        stats = {
            'articles': self.migrate_articles(dry_run),
            'authors': self.migrate_authors(dry_run),
            'categories': self.migrate_categories(dry_run),
            'videos': self.migrate_videos(dry_run),
            'users': self.migrate_users(dry_run),
        }

        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('Migration Summary:'))
        total = 0
        for model, count in stats.items():
            self.stdout.write(f'  {model}: {count} files migrated')
            total += count
        self.stdout.write(f'\nTotal: {total} files')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a dry run. No files were actually migrated.'))
            self.stdout.write('Run without --dry-run to perform the actual migration.')

    def upload_to_cloudinary(self, file_path, folder, public_id=None):
        """Upload a file to Cloudinary and return the URL."""
        try:
            result = cloudinary.uploader.upload(
                file_path,
                folder=f'gam/{folder}',
                public_id=public_id,
                overwrite=True,
                resource_type='image',
            )
            return result.get('secure_url')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error uploading {file_path}: {e}'))
            return None

    def get_local_path(self, field):
        """Get the local file path from an ImageField."""
        if not field or not field.name:
            return None
        try:
            # Try to get path directly
            return field.path
        except (ValueError, FileNotFoundError, NotImplementedError):
            # If using Cloudinary storage, construct path manually from MEDIA_ROOT
            local_path = os.path.join(settings.MEDIA_ROOT, field.name)
            if os.path.exists(local_path):
                return local_path
            return None

    def migrate_articles(self, dry_run):
        """Migrate article featured images."""
        self.stdout.write('\nMigrating Article images...')
        count = 0

        articles = Article.objects.exclude(featured_image='').exclude(featured_image__isnull=True)

        for article in articles:
            local_path = self.get_local_path(article.featured_image)

            if local_path and os.path.exists(local_path):
                self.stdout.write(f'  - {article.title[:50]}...')

                if not dry_run:
                    url = self.upload_to_cloudinary(
                        local_path,
                        'articles/featured',
                        public_id=f'article_{article.id}'
                    )
                    if url:
                        # Update the field with Cloudinary URL
                        article.featured_image = url.replace(
                            f'https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE["CLOUD_NAME"]}/image/upload/',
                            ''
                        )
                        article.save(update_fields=['featured_image'])
                        count += 1
                else:
                    count += 1

        return count

    def migrate_authors(self, dry_run):
        """Migrate author photos."""
        self.stdout.write('\nMigrating Author photos...')
        count = 0

        authors = Author.objects.exclude(photo='').exclude(photo__isnull=True)

        for author in authors:
            local_path = self.get_local_path(author.photo)

            if local_path and os.path.exists(local_path):
                self.stdout.write(f'  - {author.name}')

                if not dry_run:
                    url = self.upload_to_cloudinary(
                        local_path,
                        'authors/photos',
                        public_id=f'author_{author.id}'
                    )
                    if url:
                        author.photo = url.replace(
                            f'https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE["CLOUD_NAME"]}/image/upload/',
                            ''
                        )
                        author.save(update_fields=['photo'])
                        count += 1
                else:
                    count += 1

        return count

    def migrate_categories(self, dry_run):
        """Migrate category images."""
        self.stdout.write('\nMigrating Category images...')
        count = 0

        categories = Category.objects.exclude(image='').exclude(image__isnull=True)

        for category in categories:
            local_path = self.get_local_path(category.image)

            if local_path and os.path.exists(local_path):
                self.stdout.write(f'  - {category.name}')

                if not dry_run:
                    url = self.upload_to_cloudinary(
                        local_path,
                        'categories',
                        public_id=f'category_{category.id}'
                    )
                    if url:
                        category.image = url.replace(
                            f'https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE["CLOUD_NAME"]}/image/upload/',
                            ''
                        )
                        category.save(update_fields=['image'])
                        count += 1
                else:
                    count += 1

        return count

    def migrate_videos(self, dry_run):
        """Migrate video thumbnails."""
        self.stdout.write('\nMigrating Video thumbnails...')
        count = 0

        videos = Video.objects.exclude(thumbnail='').exclude(thumbnail__isnull=True)

        for video in videos:
            local_path = self.get_local_path(video.thumbnail)

            if local_path and os.path.exists(local_path):
                self.stdout.write(f'  - {video.title[:50]}...')

                if not dry_run:
                    url = self.upload_to_cloudinary(
                        local_path,
                        'videos/thumbnails',
                        public_id=f'video_{video.id}'
                    )
                    if url:
                        video.thumbnail = url.replace(
                            f'https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE["CLOUD_NAME"]}/image/upload/',
                            ''
                        )
                        video.save(update_fields=['thumbnail'])
                        count += 1
                else:
                    count += 1

        return count

    def migrate_users(self, dry_run):
        """Migrate user avatars."""
        self.stdout.write('\nMigrating User avatars...')
        count = 0

        users = User.objects.exclude(avatar='').exclude(avatar__isnull=True)

        for user in users:
            local_path = self.get_local_path(user.avatar)

            if local_path and os.path.exists(local_path):
                self.stdout.write(f'  - {user.email}')

                if not dry_run:
                    url = self.upload_to_cloudinary(
                        local_path,
                        'users/avatars',
                        public_id=f'user_{user.id}'
                    )
                    if url:
                        user.avatar = url.replace(
                            f'https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE["CLOUD_NAME"]}/image/upload/',
                            ''
                        )
                        user.save(update_fields=['avatar'])
                        count += 1
                else:
                    count += 1

        return count
