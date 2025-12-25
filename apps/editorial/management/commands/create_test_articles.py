"""
Commande pour créer 2 articles de test pour tester les notifications newsletter.
Usage: python manage.py create_test_articles
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.editorial.models import Article, Author, Category
from unittest.mock import patch, MagicMock
import json
import random


class Command(BaseCommand):
    help = 'Crée 2 articles de test pour tester les notifications newsletter'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Création de 2 articles de test...'))

        with patch('django_tasks.base.Task.enqueue', MagicMock(return_value=None)):
            # Récupérer ou créer l'auteur et les catégories
            author = self._get_or_create_author()
            categories = self._get_categories()

            if not categories:
                self.stdout.write(self.style.ERROR('Aucune catégorie trouvée. Exécutez d\'abord seed_articles.'))
                return

            # Créer les 2 articles de test
            self._create_test_articles(author, categories)

        self.stdout.write(self.style.SUCCESS('Articles de test créés avec succès !'))

    def _get_or_create_author(self):
        author, _ = Author.objects.get_or_create(
            slug='redaction-gam',
            defaults={
                'name': 'Rédaction GAM',
                'bio': 'L\'équipe éditoriale de Geniesdafriquemedia.',
                'email': 'geniesdafriquemedia@gmail.com',
                'is_active': True,
            }
        )
        return author

    def _get_categories(self):
        return list(Category.objects.filter(is_active=True))

    def _create_test_articles(self, author, categories):
        timestamp = int(timezone.now().timestamp())

        articles_data = [
            {
                'title': f'Innovation africaine : Les startups qui transforment le continent en 2025',
                'slug': f'innovation-africaine-startups-{timestamp}',
                'excerpt': 'Découvrez les startups africaines les plus prometteuses qui révolutionnent les secteurs de la santé, de l\'agriculture et de l\'éducation.',
                'category': random.choice(categories),
                'tags': 'Innovation, Startups, Afrique, Tech, 2025',
                'is_featured': True,
                'is_trending': True,
                'reading_time': 5,
                'external_image_url': 'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1200',
                'body': json.dumps([
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p class="text-2xl font-medium leading-relaxed mb-8">L\'Afrique connaît une véritable révolution entrepreneuriale. Des startups innovantes émergent dans tous les secteurs, portées par une jeunesse créative et déterminée à transformer le continent.</p>'
                        },
                        'id': 'block-1'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading': 'La santé digitale en plein essor',
                            'level': 'h2'
                        },
                        'id': 'block-2'
                    },
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p>Des applications de télémédecine aux plateformes de gestion hospitalière, les healthtechs africaines révolutionnent l\'accès aux soins. mPharma, Helium Health et Vezeeta ouvrent la voie à une santé plus accessible.</p>'
                        },
                        'id': 'block-3'
                    },
                    {
                        'type': 'quote',
                        'value': {
                            'quote': 'L\'Afrique ne copie plus, elle innove. Nos solutions sont conçues pour nos réalités et inspirent le monde entier.',
                            'author': 'Rebecca Enonchong',
                            'source': 'Entrepreneure tech camerounaise'
                        },
                        'id': 'block-4'
                    },
                ]),
            },
            {
                'title': f'Énergie solaire : L\'Afrique devient le leader mondial des renouvelables',
                'slug': f'energie-solaire-afrique-leader-{timestamp}',
                'excerpt': 'Avec un ensoleillement exceptionnel et des projets ambitieux, l\'Afrique s\'impose comme le nouveau hub mondial de l\'énergie solaire.',
                'category': random.choice(categories),
                'tags': 'Énergie, Solaire, Renouvelables, Afrique, Climat',
                'is_featured': False,
                'is_trending': True,
                'reading_time': 6,
                'external_image_url': 'https://images.unsplash.com/photo-1509391366360-2e959784a276?w=1200',
                'body': json.dumps([
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p class="text-2xl font-medium leading-relaxed mb-8">Le Sahara, longtemps perçu comme un obstacle au développement, devient le plus grand atout énergétique du continent. Des méga-projets solaires transforment l\'Afrique en puissance énergétique mondiale.</p>'
                        },
                        'id': 'block-1'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading': 'Des projets titanesques',
                            'level': 'h2'
                        },
                        'id': 'block-2'
                    },
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p>Le projet Noor au Maroc, les fermes solaires du Kenya et les initiatives égyptiennes démontrent l\'ambition africaine. Ces installations fournissent de l\'électricité à des millions de foyers tout en réduisant l\'empreinte carbone du continent.</p>'
                        },
                        'id': 'block-3'
                    },
                    {
                        'type': 'quote',
                        'value': {
                            'quote': 'L\'Afrique a le potentiel de devenir la batterie verte du monde. Notre soleil est notre pétrole du 21ème siècle.',
                            'author': 'Amina J. Mohammed',
                            'source': 'Vice-Secrétaire générale de l\'ONU'
                        },
                        'id': 'block-4'
                    },
                ]),
            },
        ]

        for article_data in articles_data:
            body_data = article_data.pop('body')

            article = Article.objects.create(
                **article_data,
                author=author,
                status='published',
                published_at=timezone.now(),
            )

            # Mettre à jour le body StreamField
            article.body = body_data
            article.save()

            self.stdout.write(self.style.SUCCESS(f"  ✓ Article créé: '{article.title[:50]}...'"))
            self.stdout.write(f"    → Notification devrait être envoyée automatiquement")
