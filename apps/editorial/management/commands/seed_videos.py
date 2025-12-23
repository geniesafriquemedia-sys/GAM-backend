"""
Commande Django pour peupler la base de données avec des vidéos.
Usage: python manage.py seed_videos
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.editorial.models import Video, Category
from apps.core.utils import extract_youtube_id, get_youtube_thumbnail


class Command(BaseCommand):
    help = 'Peuple la base de données avec des vidéos YouTube'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Création des vidéos...'))

        # 1. S'assurer que la catégorie Actualité existe
        category = self._get_or_create_category()

        # 2. Créer les vidéos
        self._create_videos(category)

        self.stdout.write(self.style.SUCCESS('Vidéos créées avec succès !'))

    def _get_or_create_category(self):
        """Récupère ou crée la catégorie Actualité."""
        category, created = Category.objects.get_or_create(
            slug='actualite',
            defaults={
                'name': 'Actualité',
                'description': 'Les dernières nouvelles et analyses sur l\'actualité africaine et internationale.',
                'color': '#EF4444',  # Rouge pour l'actualité
                'icon': 'newspaper',
                'is_active': True,
                'is_featured': True,
            }
        )
        status = 'créée' if created else 'existante'
        self.stdout.write(f"  Catégorie '{category.name}' {status}")
        return category

    def _create_videos(self, category):
        """Crée les vidéos."""

        videos_data = [
            # France 24 - Direct (Live Stream)
            {
                'title': 'France 24 - Le Direct',
                'slug': 'france-24-direct',
                'description': '''France 24, la chaîne d'information internationale en continu.

Suivez l'actualité française et internationale 24h/24 avec France 24. Analyses, reportages, débats et éditions spéciales sur les grands événements qui façonnent le monde.

France 24 propose une couverture unique de l'actualité africaine avec des correspondants sur tout le continent.''',
                'youtube_url': 'https://www.youtube.com/watch?v=l8PMl7tUDIE',
                'video_type': Video.VideoType.EMISSION,
                'category': category,
                'tags': 'France 24, Direct, Live, Actualité, Info, International, Afrique',
                'duration': 0,  # Live = durée indéfinie
                'is_featured': True,
                'is_live': True,
                'status': Video.PublicationStatus.PUBLISHED,
                'published_at': timezone.now(),
                'meta_title': 'France 24 en Direct - Actualités en continu',
                'meta_description': 'Regardez France 24 en direct. Actualités françaises et internationales 24h/24.',
            },

            # Reportage BR-319 Amazonie
            {
                'title': 'Brésil : la BR-319, une route au coeur de l\'Amazonie',
                'slug': 'bresil-br319-route-amazonie',
                'description': '''Alors que le Brésil s'apprête à présider la COP30 à Belem, la construction d'une route dans une Amazonie en pleine mutation suscite la polémique.

Autorisée par le président brésilien Lula, la BR-319 est en train d'être goudronnée au cœur du poumon vert de la planète.

Reportage de Fanny Lothaire et Marine Resse.''',
                'youtube_url': 'https://www.youtube.com/watch?v=DxAQqfa1wrg',
                'video_type': Video.VideoType.REPORTAGE,
                'category': category,
                'tags': 'Brésil, Amazonie, COP30, Environnement, Lula, BR-319, Déforestation',
                'duration': 0,
                'is_featured': True,
                'is_live': False,
                'status': Video.PublicationStatus.PUBLISHED,
                'published_at': timezone.now(),
                'meta_title': 'BR-319 : une route controversée en Amazonie',
                'meta_description': 'Reportage sur la construction de la BR-319 au Brésil, une route goudronnée au coeur de l\'Amazonie.',
            },

            # Reportage Tanzanie pierres précieuses
            {
                'title': 'Tanzanie : à la recherche du rubis parfait',
                'slug': 'tanzanie-rubis-pierres-precieuses',
                'description': '''Derrière l'éclat des pierres précieuses, une réalité brute.

En Tanzanie, un chercheur de gemmes sillonne les mines et les routes à la poursuite d'un rouge parfait.

Un voyage au coeur des mines tanzaniennes où se cache la beauté des rubis.''',
                'youtube_url': 'https://www.youtube.com/watch?v=KE0ao89x0t0',
                'video_type': Video.VideoType.REPORTAGE,
                'category': category,
                'tags': 'Tanzanie, Rubis, Pierres précieuses, Mines, Afrique, Gemmes',
                'duration': 0,
                'is_featured': False,
                'is_live': False,
                'status': Video.PublicationStatus.PUBLISHED,
                'published_at': timezone.now(),
                'meta_title': 'Tanzanie : la quête du rubis parfait',
                'meta_description': 'Reportage sur un chercheur de gemmes en Tanzanie, à la poursuite du rubis parfait.',
            },

            # Documentaire Gabon
            {
                'title': 'Gabon, les sentinelles de la forêt',
                'slug': 'gabon-sentinelles-foret-documentaire',
                'description': '''Les sentinelles de l'Afrique - Episode : Gabon, les sentinelles de la forêt.

Cachés sous un épais manteau vert, se trouvent le cœur et l'âme du Gabon. De cette forêt équatoriale qui couvre 80% de leur territoire, les Gabonais tirent l'essentiel de leurs traditions, de leur médecine, de leur spiritualité et de leurs ressources.

Un patrimoine précieux et fragile, que quelques femmes et hommes veillent à protéger.

Réalisation : Julien Naar
Production : Bo Travail ! et Voyage pour TV5 Monde''',
                'youtube_url': 'https://youtu.be/Tnt7xMbJTBw',
                'video_type': Video.VideoType.DOCUMENTARY,
                'category': category,
                'tags': 'Gabon, Documentaire, Forêt, Afrique, Environnement, TV5 Monde, Nature, Traditions',
                'duration': 0,
                'is_featured': True,
                'is_live': False,
                'status': Video.PublicationStatus.PUBLISHED,
                'published_at': timezone.now(),
                'meta_title': 'Gabon, les sentinelles de la forêt - Documentaire',
                'meta_description': 'Documentaire sur les gardiens de la forêt équatoriale gabonaise et leurs traditions ancestrales.',
            },
        ]

        for video_data in videos_data:
            youtube_url = video_data['youtube_url']
            youtube_id = extract_youtube_id(youtube_url)
            youtube_thumbnail = get_youtube_thumbnail(youtube_id) if youtube_id else ''

            video, created = Video.objects.get_or_create(
                slug=video_data['slug'],
                defaults={
                    **video_data,
                    'youtube_id': youtube_id,
                    'youtube_thumbnail': youtube_thumbnail,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f"  [OK] Video '{video.title}' creee"
                ))
                self.stdout.write(f"    YouTube ID: {video.youtube_id}")
                self.stdout.write(f"    Type: {'LIVE' if video.is_live else video.video_type}")
                self.stdout.write(f"    URL: /web-tv/{video.slug}")
            else:
                self.stdout.write(self.style.WARNING(
                    f"  [SKIP] Video '{video.title}' existe deja"
                ))
