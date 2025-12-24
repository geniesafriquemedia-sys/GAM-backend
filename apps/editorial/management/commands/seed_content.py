"""
Management command pour ajouter du contenu riche à la base de données
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.editorial.models import Category, Article, Author, Video


class Command(BaseCommand):
    help = 'Ajoute du contenu riche (catégories, auteurs, articles, vidéos)'

    def handle(self, *args, **options):
        self.stdout.write('Création du contenu...\n')

        # === CATÉGORIES ===
        categories_data = [
            {
                'name': 'Innovation & Tech',
                'slug': 'innovation-tech',
                'description': 'Les dernières avancées technologiques et innovations qui transforment le continent africain.',
                'color': '#6366F1',
                'is_featured': True,
                'is_active': True,
            },
            {
                'name': 'Culture & Patrimoine',
                'slug': 'culture-patrimoine',
                'description': 'Découvrez la richesse culturelle et le patrimoine africain à travers nos reportages.',
                'color': '#EC4899',
                'is_featured': True,
                'is_active': True,
            },
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat.slug] = cat
            status = 'Créée' if created else 'Existante'
            self.stdout.write(f'  Catégorie: {cat.name} ({status})')

        # Récupérer catégories existantes
        for cat in Category.objects.filter(is_active=True):
            categories[cat.slug] = cat

        # === AUTEURS ===
        authors_data = [
            {
                'name': 'Amina Diallo',
                'slug': 'amina-diallo',
                'bio': 'Journaliste spécialisée en économie et développement durable. Correspondante à Dakar depuis 10 ans.',
                'email': 'amina.diallo@gam.africa',
                'photo': 'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=400',
                'twitter': '@AminaDiaoGAM',
                'is_active': True,
            },
            {
                'name': 'Kwame Asante',
                'slug': 'kwame-asante',
                'bio': 'Expert en technologies et innovation africaine. Ancien directeur de recherche à l\'Université de Accra.',
                'email': 'kwame.asante@gam.africa',
                'photo': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400',
                'twitter': '@KwameAsanteGAM',
                'is_active': True,
            },
            {
                'name': 'Fatou Ndiaye',
                'slug': 'fatou-ndiaye',
                'bio': 'Rédactrice en chef adjointe. Spécialiste des questions sociales et culturelles en Afrique de l\'Ouest.',
                'email': 'fatou.ndiaye@gam.africa',
                'photo': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400',
                'linkedin': 'fatou-ndiaye-gam',
                'is_active': True,
            },
            {
                'name': 'Ibrahim Keita',
                'slug': 'ibrahim-keita',
                'bio': 'Correspondant régional pour l\'Afrique de l\'Est. Expert en géopolitique et relations internationales.',
                'email': 'ibrahim.keita@gam.africa',
                'photo': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400',
                'twitter': '@IbrahimKeitaGAM',
                'is_active': True,
            },
            {
                'name': 'Aïcha Mbeki',
                'slug': 'aicha-mbeki',
                'bio': 'Journaliste d\'investigation. Prix panafricain du journalisme 2023. Basée à Johannesburg.',
                'email': 'aicha.mbeki@gam.africa',
                'photo': 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400',
                'website': 'https://aichambeki.com',
                'is_active': True,
            },
        ]

        authors = {}
        for auth_data in authors_data:
            author, created = Author.objects.get_or_create(
                slug=auth_data['slug'],
                defaults=auth_data
            )
            authors[author.slug] = author
            status = 'Créé' if created else 'Existant'
            self.stdout.write(f'  Auteur: {author.name} ({status})')

        # === ARTICLES ===
        articles_data = [
            {
                'title': 'La révolution fintech en Afrique : 500 millions d\'utilisateurs d\'ici 2025',
                'slug': 'revolution-fintech-afrique-2025',
                'excerpt': 'L\'Afrique connaît une croissance exponentielle dans le secteur des technologies financières, transformant l\'accès aux services bancaires pour des millions de personnes.',
                'content': '''<p>L'Afrique est en train de devenir le terrain de jeu le plus dynamique pour les fintechs mondiales. Avec une population jeune et connectée, le continent voit émerger des solutions innovantes qui révolutionnent l'accès aux services financiers.</p>

<h2>Une croissance sans précédent</h2>
<p>Selon les dernières études, le nombre d'utilisateurs de services fintech en Afrique devrait atteindre 500 millions d'ici 2025, contre 300 millions aujourd'hui. Cette croissance est portée par l'adoption massive du mobile money et des solutions de paiement digital.</p>

<h2>Les acteurs clés</h2>
<p>Des entreprises comme M-Pesa au Kenya, Wave au Sénégal, et Flutterwave au Nigeria sont à l'avant-garde de cette révolution. Elles offrent des services qui répondent aux besoins spécifiques des populations africaines.</p>

<p>Les investissements dans le secteur ont dépassé les 3 milliards de dollars en 2024, un record historique qui témoigne de la confiance des investisseurs dans le potentiel africain.</p>''',
                'external_image_url': 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=1200',
                'author_slug': 'kwame-asante',
                'category_slug': 'innovation-tech',
                'reading_time': 6,
                'is_featured': True,
                'is_trending': True,
                'tags': 'fintech, innovation, mobile money, investissement',
            },
            {
                'title': 'Le Festival des Arts de Dakar célèbre 50 ans de création africaine',
                'slug': 'festival-arts-dakar-50-ans',
                'excerpt': 'Le plus grand événement culturel d\'Afrique de l\'Ouest rassemble cette année plus de 200 artistes venus de 30 pays pour célébrer un demi-siècle de création artistique.',
                'content': '''<p>Dakar s'apprête à accueillir la 50ème édition de son légendaire Festival des Arts, un événement qui a marqué l'histoire culturelle du continent africain.</p>

<h2>Un demi-siècle d'excellence artistique</h2>
<p>Depuis sa création en 1974, le Festival des Arts de Dakar a été le tremplin de nombreux artistes aujourd'hui reconnus internationalement. Cette édition anniversaire promet d'être exceptionnelle.</p>

<h2>Une programmation éclectique</h2>
<p>Plus de 200 artistes venus de 30 pays différents présenteront leurs œuvres dans les domaines de la peinture, la sculpture, la musique, la danse et les arts numériques. Une section spéciale sera dédiée aux jeunes talents émergents.</p>

<p>Le thème de cette année, "Racines et Horizons", invite à explorer le dialogue entre tradition et modernité dans l'art africain contemporain.</p>''',
                'external_image_url': 'https://images.unsplash.com/photo-1518611012118-696072aa579a?w=1200',
                'author_slug': 'fatou-ndiaye',
                'category_slug': 'culture-patrimoine',
                'reading_time': 5,
                'is_featured': True,
                'tags': 'culture, art, festival, dakar, patrimoine',
            },
            {
                'title': 'Énergies renouvelables : l\'Afrique du Sud atteint 30% de sa production',
                'slug': 'energies-renouvelables-afrique-sud-30-pourcent',
                'excerpt': 'Un cap historique franchi par la nation arc-en-ciel qui accélère sa transition énergétique malgré les défis économiques.',
                'content': '''<p>L'Afrique du Sud vient de franchir un cap symbolique majeur : 30% de son électricité provient désormais de sources renouvelables, principalement solaire et éolienne.</p>

<h2>Une transition accélérée</h2>
<p>Face aux défis de Eskom et aux délestages chroniques, le gouvernement sud-africain a massivement investi dans les énergies alternatives. Les résultats dépassent les attentes.</p>

<h2>Des investissements records</h2>
<p>Plus de 15 milliards de dollars ont été investis dans le secteur des énergies vertes au cours des cinq dernières années. De nouveaux parcs solaires et éoliens continuent d'être construits à travers le pays.</p>

<p>Cette réussite positionne l'Afrique du Sud comme un leader continental dans la transition énergétique et pourrait inspirer d'autres nations africaines.</p>''',
                'external_image_url': 'https://images.unsplash.com/photo-1509391366360-2e959784a276?w=1200',
                'author_slug': 'aicha-mbeki',
                'category_slug': 'innovation-tech',
                'reading_time': 4,
                'is_trending': True,
                'tags': 'énergie, renouvelable, afrique du sud, transition',
            },
            {
                'title': 'Les manuscrits de Tombouctou : un trésor numérisé pour l\'humanité',
                'slug': 'manuscrits-tombouctou-numerisation',
                'excerpt': 'Plus de 300 000 manuscrits anciens ont été numérisés, préservant un patrimoine intellectuel africain inestimable pour les générations futures.',
                'content': '''<p>Un projet ambitieux de numérisation vient de s'achever à Tombouctou, au Mali, préservant pour l'éternité l'un des plus grands trésors intellectuels de l'humanité.</p>

<h2>Un héritage intellectuel unique</h2>
<p>Les manuscrits de Tombouctou, datant du XIIe au XVIe siècle, couvrent des sujets aussi variés que l'astronomie, les mathématiques, la médecine, la jurisprudence et la philosophie. Ils témoignent de la richesse intellectuelle de l'Afrique médiévale.</p>

<h2>Une course contre le temps</h2>
<p>Face aux menaces climatiques et aux conflits, la numérisation de ces documents était devenue urgente. Grâce à la collaboration internationale, plus de 300 000 manuscrits sont désormais accessibles en ligne.</p>

<p>Cette initiative ouvre de nouvelles perspectives de recherche sur l'histoire intellectuelle africaine et remet en question de nombreux préjugés historiques.</p>''',
                'external_image_url': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200',
                'author_slug': 'ibrahim-keita',
                'category_slug': 'culture-patrimoine',
                'reading_time': 7,
                'is_featured': True,
                'tags': 'patrimoine, manuscrits, tombouctou, histoire, numérisation',
            },
            {
                'title': 'Agriculture intelligente : des drones pour surveiller les cultures au Kenya',
                'slug': 'agriculture-drones-kenya',
                'excerpt': 'Les agriculteurs kenyans adoptent massivement les technologies de surveillance par drone pour optimiser leurs rendements et réduire les pertes.',
                'content': '''<p>Au Kenya, une révolution silencieuse transforme l'agriculture traditionnelle. Les drones équipés de capteurs multispectraux permettent aux agriculteurs de surveiller leurs cultures avec une précision inégalée.</p>

<h2>Une technologie accessible</h2>
<p>Grâce à des startups locales comme Astral Aerial et Apollo Agriculture, les petits exploitants peuvent désormais accéder à ces technologies autrefois réservées aux grandes exploitations industrielles.</p>

<h2>Des résultats impressionnants</h2>
<p>Les premiers utilisateurs rapportent une augmentation de 30% de leurs rendements et une réduction de 40% de l'utilisation de pesticides, grâce à une détection précoce des maladies et des zones de stress hydrique.</p>

<p>Le gouvernement kenyan a annoncé un programme de subventions pour accélérer l'adoption de ces technologies dans l'ensemble du pays.</p>''',
                'external_image_url': 'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=1200',
                'author_slug': 'kwame-asante',
                'category_slug': 'innovation-tech',
                'reading_time': 5,
                'tags': 'agriculture, drones, kenya, technologie, innovation',
            },
            {
                'title': 'La mode africaine conquiert les podiums de Paris et Milan',
                'slug': 'mode-africaine-podiums-paris-milan',
                'excerpt': 'Les créateurs africains sont de plus en plus présents dans les grandes semaines de la mode, imposant leur vision unique et leur savoir-faire.',
                'content': '''<p>La mode africaine n'a jamais été aussi visible sur la scène internationale. De Paris à Milan, les créateurs du continent imposent leur vision créative et renouvellent les codes de la haute couture.</p>

<h2>Des talents reconnus mondialement</h2>
<p>Des designers comme Imane Ayissi, Thebe Magugu et Kenneth Ize ont su séduire les plus grandes maisons de couture et les médias internationaux par leur créativité unique et leur maîtrise des textiles traditionnels.</p>

<h2>Un marché en pleine expansion</h2>
<p>Le marché de la mode africaine est estimé à 31 milliards de dollars et devrait doubler d'ici 2030. Les marques de luxe s'intéressent de plus en plus aux collaborations avec des artisans africains.</p>

<p>Cette reconnaissance internationale ouvre de nouvelles perspectives économiques pour l'industrie textile africaine et ses millions d'artisans.</p>''',
                'external_image_url': 'https://images.unsplash.com/photo-1558171813-4c088753af8f?w=1200',
                'author_slug': 'amina-diallo',
                'category_slug': 'culture-patrimoine',
                'reading_time': 4,
                'is_trending': True,
                'tags': 'mode, fashion, créateurs, luxe, textile',
            },
            {
                'title': 'Intelligence artificielle : le Rwanda lance son centre d\'excellence continental',
                'slug': 'intelligence-artificielle-rwanda-centre-excellence',
                'excerpt': 'Kigali devient la capitale africaine de l\'IA avec l\'inauguration d\'un centre de recherche et d\'innovation de classe mondiale.',
                'content': '''<p>Le Rwanda confirme son statut de hub technologique africain avec l'inauguration du premier Centre d'Excellence en Intelligence Artificielle du continent, situé à Kigali.</p>

<h2>Une infrastructure de pointe</h2>
<p>Le centre, fruit d'un partenariat entre le gouvernement rwandais, Carnegie Mellon University Africa et des géants tech comme Google et Microsoft, dispose des équipements les plus avancés pour la recherche en IA.</p>

<h2>Former les talents de demain</h2>
<p>L'objectif est de former 10 000 spécialistes en IA d'ici 2030 et de développer des solutions adaptées aux défis africains dans les domaines de la santé, de l'agriculture et de l'éducation.</p>

<p>Plusieurs projets pilotes sont déjà en cours, notamment un système de diagnostic médical assisté par IA et une plateforme d'agriculture de précision.</p>''',
                'external_image_url': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200',
                'author_slug': 'ibrahim-keita',
                'category_slug': 'innovation-tech',
                'reading_time': 6,
                'is_featured': True,
                'tags': 'IA, intelligence artificielle, rwanda, technologie, formation',
            },
            {
                'title': 'Les griots du Sahel : gardiens de la mémoire collective',
                'slug': 'griots-sahel-memoire-collective',
                'excerpt': 'Un voyage au cœur de la tradition des griots, ces conteurs et musiciens qui perpétuent depuis des siècles l\'histoire orale de l\'Afrique de l\'Ouest.',
                'content': '''<p>Dans les villages du Sahel, les griots continuent de jouer un rôle essentiel dans la préservation de la mémoire collective et la transmission des savoirs ancestraux.</p>

<h2>Une tradition millénaire</h2>
<p>Les griots, ou "djélis" en mandingue, sont les dépositaires de l'histoire orale africaine. À travers leurs récits, leurs chants et leur musique, ils préservent les généalogies, les épopées et les leçons de sagesse transmises de génération en génération.</p>

<h2>Entre tradition et modernité</h2>
<p>Aujourd'hui, une nouvelle génération de griots utilise les réseaux sociaux et les plateformes de streaming pour toucher un public plus large, tout en préservant l'authenticité de leur art.</p>

<p>Des initiatives de sauvegarde ont été lancées par l'UNESCO pour documenter et préserver ce patrimoine immatériel unique de l'humanité.</p>''',
                'external_image_url': 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=1200',
                'author_slug': 'fatou-ndiaye',
                'category_slug': 'culture-patrimoine',
                'reading_time': 8,
                'tags': 'griots, tradition, sahel, culture, patrimoine oral',
            },
            {
                'title': 'E-commerce : Jumia dépasse les 10 millions de clients actifs',
                'slug': 'jumia-10-millions-clients-actifs',
                'excerpt': 'La plateforme de commerce en ligne panafricaine franchit un cap symbolique et annonce son expansion dans cinq nouveaux pays.',
                'content': '''<p>Jumia, souvent surnommée "l'Amazon africain", vient d'annoncer avoir franchi le cap des 10 millions de clients actifs, un record pour le e-commerce sur le continent.</p>

<h2>Une croissance soutenue</h2>
<p>Malgré les défis logistiques et infrastructurels, la plateforme a su adapter son modèle aux réalités africaines, notamment avec son réseau de points de collecte et ses solutions de paiement mobile.</p>

<h2>Une expansion ambitieuse</h2>
<p>Fort de ce succès, Jumia annonce son expansion dans cinq nouveaux marchés : la RDC, l'Angola, le Mozambique, la Zambie et le Zimbabwe. L'entreprise prévoit d'investir 200 millions de dollars dans le développement de ses infrastructures logistiques.</p>

<p>Cette croissance témoigne de l'appétit des consommateurs africains pour le commerce en ligne et du potentiel immense de ce marché.</p>''',
                'external_image_url': 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200',
                'author_slug': 'amina-diallo',
                'category_slug': 'innovation-tech',
                'reading_time': 5,
                'is_trending': True,
                'tags': 'e-commerce, jumia, business, digital, expansion',
            },
            {
                'title': 'Archéologie : découverte d\'une cité antique au Soudan',
                'slug': 'archeologie-cite-antique-soudan',
                'excerpt': 'Des archéologues ont mis au jour les vestiges d\'une importante cité méroïtique, révélant de nouveaux secrets sur la civilisation nubienne.',
                'content': '''<p>Une équipe internationale d'archéologues a fait une découverte majeure dans le désert du Soudan : les vestiges d'une cité méroïtique jusqu'alors inconnue, datant de plus de 2000 ans.</p>

<h2>Une civilisation méconnue</h2>
<p>Le royaume de Méroé, qui a prospéré entre le VIIIe siècle avant J.-C. et le IVe siècle après J.-C., reste encore largement méconnu du grand public. Cette découverte promet de révéler de nouveaux aspects de cette brillante civilisation nubienne.</p>

<h2>Des trésors exceptionnels</h2>
<p>Les premières fouilles ont révélé des temples ornés de fresques, des tombes royales et des milliers d'objets du quotidien. Les archéologues estiment qu'il faudra plusieurs décennies pour explorer entièrement le site.</p>

<p>Cette découverte pourrait réécrire certains chapitres de l'histoire africaine et attirer l'attention internationale sur le patrimoine archéologique du Soudan.</p>''',
                'external_image_url': 'https://images.unsplash.com/photo-1539650116574-8efeb43e2750?w=1200',
                'author_slug': 'aicha-mbeki',
                'category_slug': 'culture-patrimoine',
                'reading_time': 6,
                'is_featured': True,
                'tags': 'archéologie, soudan, méroé, histoire, découverte',
            },
        ]

        for art_data in articles_data:
            author = authors.get(art_data.pop('author_slug'))
            if not author:
                author = Author.objects.first()

            category = categories.get(art_data.pop('category_slug'))
            if not category:
                category = Category.objects.first()

            article, created = Article.objects.get_or_create(
                slug=art_data['slug'],
                defaults={
                    **art_data,
                    'author': author,
                    'category': category,
                    'status': 'published',
                    'published_at': timezone.now(),
                }
            )
            status = 'Créé' if created else 'Existant'
            self.stdout.write(f'  Article: {article.title[:50]}... ({status})')

        # === VIDÉOS ===
        videos_data = [
            {
                'title': 'Documentaire : Les startups qui transforment l\'Afrique',
                'slug': 'documentaire-startups-afrique',
                'description': 'Un voyage au cœur de l\'écosystème tech africain, à la rencontre des entrepreneurs qui façonnent le futur du continent.',
                'youtube_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'video_type': 'documentary',
                'category_slug': 'innovation-tech',
                'duration': 2700,
                'is_featured': True,
                'tags': 'startup, tech, entrepreneurs, innovation',
            },
            {
                'title': 'Interview : Ngozi Okonjo-Iweala sur l\'avenir du commerce africain',
                'slug': 'interview-ngozi-okonjo-iweala',
                'description': 'La directrice générale de l\'OMC partage sa vision pour le développement du commerce intra-africain.',
                'youtube_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'video_type': 'interview',
                'category_slug': 'innovation-tech',
                'duration': 1800,
                'is_featured': True,
                'tags': 'commerce, OMC, économie, ZLECAF',
            },
        ]

        for vid_data in videos_data:
            category = categories.get(vid_data.pop('category_slug'))
            video, created = Video.objects.get_or_create(
                slug=vid_data['slug'],
                defaults={
                    **vid_data,
                    'category': category,
                    'status': 'published',
                    'published_at': timezone.now(),
                }
            )
            status = 'Créée' if created else 'Existante'
            self.stdout.write(f'  Vidéo: {video.title[:50]}... ({status})')

        self.stdout.write(self.style.SUCCESS('\nContenu créé avec succès!'))
        self.stdout.write(f'  - {Category.objects.count()} catégories')
        self.stdout.write(f'  - {Author.objects.count()} auteurs')
        self.stdout.write(f'  - {Article.objects.count()} articles')
        self.stdout.write(f'  - {Video.objects.count()} vidéos')
