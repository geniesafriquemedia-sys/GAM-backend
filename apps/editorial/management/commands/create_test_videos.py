"""
Commande pour créer des vidéos de test pour tester les notifications newsletter.
Usage: python manage.py create_test_videos
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.editorial.models import Video, Category
from unittest.mock import patch, MagicMock
import random


class Command(BaseCommand):
    help = 'Crée 2 vidéos de test pour tester les notifications newsletter'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Création de 2 vidéos de test...'))

        with patch('django_tasks.base.Task.enqueue', MagicMock(return_value=None)):
            # Récupérer les catégories
            categories = self._get_categories()

            # Créer les vidéos de test
            self._create_test_videos(categories)

        self.stdout.write(self.style.SUCCESS('Vidéos de test créées avec succès !'))

    def _get_categories(self):
        return list(Category.objects.filter(is_active=True))

    def _create_test_videos(self, categories):
        timestamp = int(timezone.now().timestamp())

        videos_data = [
            {
                'title': f'Interview exclusive : Les pionniers de la tech africaine',
                'slug': f'interview-pionniers-tech-africaine-{timestamp}',
                'description': 'Rencontre avec les entrepreneurs qui révolutionnent le paysage technologique africain. Innovation, défis et vision pour l\'avenir du continent.',
                'youtube_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'youtube_id': 'dQw4w9WgXcQ',
                'youtube_thumbnail': 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
                'video_type': 'interview',
                'category': random.choice(categories) if categories else None,
                'tags': 'Tech, Innovation, Afrique, Interview, Entrepreneurs',
                'is_featured': True,
                'duration': 1520,  # 25:20
            },
            {
                'title': f'Documentaire : L\'essor des énergies renouvelables en Afrique',
                'slug': f'documentaire-energies-renouvelables-afrique-{timestamp}',
                'description': 'Un voyage à travers le continent pour découvrir les projets d\'énergie solaire et éolienne qui transforment l\'Afrique. Du Maroc au Kenya, l\'avenir énergétique se dessine.',
                'youtube_url': 'https://www.youtube.com/watch?v=jNQXAC9IVRw',
                'youtube_id': 'jNQXAC9IVRw',
                'youtube_thumbnail': 'https://img.youtube.com/vi/jNQXAC9IVRw/maxresdefault.jpg',
                'video_type': 'documentary',
                'category': random.choice(categories) if categories else None,
                'tags': 'Énergie, Solaire, Renouvelables, Documentaire, Afrique',
                'is_featured': False,
                'duration': 2700,  # 45:00
            },
        ]

        for video_data in videos_data:
            video = Video.objects.create(
                **video_data,
                status='published',
                published_at=timezone.now(),
            )

            self.stdout.write(self.style.SUCCESS(f"  ✓ Vidéo créée: '{video.title[:50]}...'"))
            self.stdout.write(f"    → Notification devrait être envoyée automatiquement")
