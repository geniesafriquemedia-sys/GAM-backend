"""
Commande Django pour peupler la base de données avec des articles de démonstration.
Usage: python manage.py seed_articles
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.editorial.models import Article, Author, Category
from unittest.mock import patch, MagicMock
import json


class Command(BaseCommand):
    help = 'Peuple la base de données avec 3 articles de démonstration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Création des données de démonstration...'))

        # Contourner le bug de django_tasks avec Python 3.12
        # en remplaçant la méthode enqueue par un no-op
        with patch('django_tasks.base.Task.enqueue', MagicMock(return_value=None)):
            # 1. Créer les catégories
            categories = self._create_categories()

            # 2. Créer l'auteur
            author = self._create_author()

            # 3. Créer les articles
            self._create_articles(author, categories)

        self.stdout.write(self.style.SUCCESS('Données de démonstration créées avec succès !'))

    def _create_categories(self):
        """Crée les catégories nécessaires."""
        categories_data = [
            {
                'name': 'Sport',
                'slug': 'sport',
                'description': 'Actualités sportives africaines : football, athlétisme, basketball et plus encore.',
                'color': '#10B981',
                'icon': 'trophy',
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Actualité',
                'slug': 'actualite',
                'description': 'Les dernières nouvelles et analyses sur l\'actualité africaine.',
                'color': '#3B82F6',
                'icon': 'newspaper',
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Technologie',
                'slug': 'technologie',
                'description': 'Innovation, startups et transformation digitale en Afrique.',
                'color': '#8B5CF6',
                'icon': 'cpu',
                'is_active': True,
                'is_featured': True,
            },
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            status = 'créée' if created else 'existante'
            self.stdout.write(f"  Catégorie '{category.name}' {status}")

        return categories

    def _create_author(self):
        """Crée un auteur par défaut."""
        author, created = Author.objects.get_or_create(
            slug='redaction-gam',
            defaults={
                'name': 'Rédaction GAM',
                'bio': 'L\'équipe éditoriale de Génies Afrique Médias, dédiée à mettre en lumière le génie africain à travers des analyses approfondies et des reportages exclusifs.',
                'email': 'redaction@gam.africa',
                'is_active': True,
            }
        )
        status = 'créé' if created else 'existant'
        self.stdout.write(f"  Auteur '{author.name}' {status}")
        return author

    def _create_articles(self, author, categories):
        """Crée les 3 articles de démonstration."""

        articles_data = [
            # Article 1: CAN 2025 au Maroc
            {
                'title': 'CAN 2025 : Le Maroc accueille la plus grande compétition africaine de football',
                'slug': 'can-2025-maroc-coupe-afrique-nations',
                'excerpt': 'La Coupe d\'Afrique des Nations 2025 bat son plein au Maroc. Entre performances exceptionnelles et ambiance électrique, retour sur les temps forts de cette édition historique.',
                'category': categories['sport'],
                'tags': 'CAN 2025, Football, Maroc, Afrique, Sport',
                'is_featured': True,
                'is_trending': True,
                'reading_time': 7,
                'body': json.dumps([
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p class="text-2xl font-medium leading-relaxed mb-8">Le Maroc accueille actuellement la 35ème édition de la Coupe d\'Afrique des Nations, un événement qui rassemble les meilleures équipes du continent dans une compétition féroce pour le titre suprême du football africain.</p>'
                        },
                        'id': 'block-1'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading': 'Une organisation exemplaire',
                            'level': 'h2'
                        },
                        'id': 'block-2'
                    },
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p>Les stades marocains, modernisés pour l\'occasion, offrent une expérience spectateur de classe mondiale. De Casablanca à Marrakech, en passant par Rabat et Tanger, les infrastructures sont à la hauteur de l\'événement.</p><p>Les supporters affluent de tout le continent, créant une atmosphère unique qui témoigne de la passion africaine pour le ballon rond. Les chants, les couleurs et l\'enthousiasme transforment chaque match en une véritable fête populaire.</p>'
                        },
                        'id': 'block-3'
                    },
                    {
                        'type': 'quote',
                        'value': {
                            'quote': 'Cette CAN au Maroc montre au monde entier que l\'Afrique peut organiser des événements sportifs de niveau international. C\'est une fierté pour tout le continent.',
                            'author': 'Patrice Motsepe',
                            'source': 'Président de la CAF'
                        },
                        'id': 'block-4'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading': 'Les favoris en lice',
                            'level': 'h2'
                        },
                        'id': 'block-5'
                    },
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p>Le Maroc, pays hôte et demi-finaliste de la Coupe du Monde 2022, fait figure de favori aux côtés du Sénégal, champion en titre, et du Nigeria, toujours redoutable. L\'Égypte et l\'Algérie restent également des prétendants sérieux au sacre final.</p><p>Les jeunes talents africains brillent sur la scène continentale, confirmant la richesse du vivier de footballeurs que produit l\'Afrique année après année.</p>'
                        },
                        'id': 'block-6'
                    },
                ]),
            },

            # Article 2: Actualité courante
            {
                'title': 'L\'Afrique en 2025 : Les grandes transformations économiques en cours',
                'slug': 'afrique-2025-transformations-economiques',
                'excerpt': 'De la Zone de libre-échange continentale africaine aux investissements massifs dans les infrastructures, le continent connaît des mutations profondes qui redessinent son avenir économique.',
                'category': categories['actualite'],
                'tags': 'Économie, Afrique, ZLECAf, Développement, 2025',
                'is_featured': False,
                'is_trending': True,
                'reading_time': 6,
                'body': json.dumps([
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p class="text-2xl font-medium leading-relaxed mb-8">L\'année 2025 marque un tournant décisif pour l\'économie africaine. Avec la montée en puissance de la Zone de libre-échange continentale africaine (ZLECAf), le continent s\'affirme comme un acteur incontournable de l\'économie mondiale.</p>'
                        },
                        'id': 'block-1'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading': 'La ZLECAf change la donne',
                            'level': 'h2'
                        },
                        'id': 'block-2'
                    },
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p>Entrée en vigueur il y a quelques années, la Zone de libre-échange continentale africaine commence à produire ses effets. Les échanges intra-africains sont en hausse significative, créant de nouvelles opportunités pour les entreprises locales.</p><p>Les barrières tarifaires s\'estompent progressivement, facilitant la circulation des biens et des services entre les 54 pays du continent.</p>'
                        },
                        'id': 'block-3'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading': 'Investissements dans les infrastructures',
                            'level': 'h2'
                        },
                        'id': 'block-4'
                    },
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p>Des projets d\'envergure transforment le paysage africain : nouvelles lignes ferroviaires, ports modernisés, réseaux électriques étendus. Ces investissements, soutenus par des partenariats internationaux diversifiés, jettent les bases d\'une croissance durable.</p><p>L\'énergie renouvelable occupe une place centrale dans cette stratégie, avec des parcs solaires et éoliens qui fleurissent du Sahara à l\'Afrique australe.</p>'
                        },
                        'id': 'block-5'
                    },
                    {
                        'type': 'quote',
                        'value': {
                            'quote': 'L\'Afrique n\'est plus le continent du futur, c\'est le continent du présent. Nous assistons à une transformation historique.',
                            'author': 'Akinwumi Adesina',
                            'source': 'Président de la BAD'
                        },
                        'id': 'block-6'
                    },
                ]),
            },

            # Article 3: Tech/Innovation
            {
                'title': 'La révolution fintech africaine : Comment l\'Afrique réinvente la finance',
                'slug': 'revolution-fintech-africaine-finance-mobile',
                'excerpt': 'Du mobile money aux néobanques, l\'Afrique est devenue un laboratoire mondial de l\'innovation financière. Découvrez les acteurs qui transforment le paysage bancaire continental.',
                'category': categories['technologie'],
                'tags': 'Fintech, Innovation, Mobile Money, Startups, Finance',
                'is_featured': True,
                'is_trending': False,
                'reading_time': 8,
                'body': json.dumps([
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p class="text-2xl font-medium leading-relaxed mb-8">Avec plus de 500 millions d\'utilisateurs de services financiers mobiles, l\'Afrique s\'est imposée comme le leader mondial de la finance digitale. Une révolution silencieuse qui transforme la vie de millions de personnes.</p>'
                        },
                        'id': 'block-1'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading': 'L\'héritage de M-Pesa',
                            'level': 'h2'
                        },
                        'id': 'block-2'
                    },
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p>Lancé au Kenya en 2007, M-Pesa a ouvert la voie à une nouvelle ère de services financiers accessibles. Aujourd\'hui, cette innovation a essaimé à travers tout le continent, inspirant des dizaines de solutions locales adaptées aux réalités africaines.</p><p>Orange Money, MTN Mobile Money, Wave... les acteurs se multiplient, intensifiant la concurrence et améliorant les services offerts aux utilisateurs.</p>'
                        },
                        'id': 'block-3'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading': 'Les licornes africaines',
                            'level': 'h2'
                        },
                        'id': 'block-4'
                    },
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p>Flutterwave, Chipper Cash, OPay... les startups fintech africaines attirent des investissements records et atteignent des valorisations de plusieurs milliards de dollars. Ces "licornes" démontrent la capacité d\'innovation du continent et sa place dans l\'écosystème tech mondial.</p>'
                        },
                        'id': 'block-5'
                    },
                    {
                        'type': 'quote',
                        'value': {
                            'quote': 'En Afrique, nous n\'adaptons pas les solutions occidentales, nous créons les solutions du futur que le monde entier finira par adopter.',
                            'author': 'Olugbenga Agboola',
                            'source': 'CEO de Flutterwave'
                        },
                        'id': 'block-6'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading': 'L\'inclusion financière en marche',
                            'level': 'h2'
                        },
                        'id': 'block-7'
                    },
                    {
                        'type': 'text',
                        'value': {
                            'content': '<p>Au-delà des success stories, c\'est l\'impact social qui impressionne le plus. Des millions d\'Africains, auparavant exclus du système bancaire traditionnel, accèdent désormais à des services d\'épargne, de crédit et d\'assurance via leur téléphone portable.</p><p>Les femmes entrepreneures, les agriculteurs des zones rurales, les petits commerçants... tous bénéficient de cette démocratisation des services financiers.</p>'
                        },
                        'id': 'block-8'
                    },
                ]),
            },
        ]

        for article_data in articles_data:
            body_data = article_data.pop('body')
            article, created = Article.objects.get_or_create(
                slug=article_data['slug'],
                defaults={
                    **article_data,
                    'author': author,
                    'status': 'published',
                    'published_at': timezone.now(),
                }
            )

            if created:
                # Mettre à jour le body StreamField
                article.body = body_data
                article.save()

            status = 'créé' if created else 'existant'
            self.stdout.write(f"  Article '{article.title[:50]}...' {status}")
