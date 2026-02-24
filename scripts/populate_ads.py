import os
import django
import sys

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

from apps.advertising.models import Advertisement

# Vérifier si des publicités existent déjà
if Advertisement.objects.count() >= 10:
    print(f"✅ {Advertisement.objects.count()} publicités déjà présentes. Skip.")
    sys.exit(0)

# Images Unsplash pour les publicités
UNSPLASH_IMAGES = [
    "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=728&h=90&fit=crop",
    "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=300&h=250&fit=crop",
    "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=728&h=90&fit=crop",
    "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=300&h=250&fit=crop",
    "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=728&h=90&fit=crop",
    "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=300&h=600&fit=crop",
    "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?w=728&h=90&fit=crop",
    "https://images.unsplash.com/photo-1556761175-4b46a572b786?w=300&h=250&fit=crop",
    "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=728&h=90&fit=crop",
    "https://images.unsplash.com/photo-1560472355-536de3962603?w=300&h=250&fit=crop",
    "https://images.unsplash.com/photo-1497366216548-37526070297c?w=728&h=90&fit=crop",
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=300&h=600&fit=crop",
]

# Données des publicités
ADS_DATA = [
    {
        "title": "Investissez en Afrique - Opportunités 2026",
        "advertiser": "Africa Investment Group",
        "position": "HOMEPAGE_TOP",
        "ad_type": "BANNER",
        "image_url": UNSPLASH_IMAGES[0],
        "click_url": "https://geniesdafriquemedia.com/partenariats",
        "is_active": True,
    },
    {
        "title": "Formation Tech Africa - Inscrivez-vous",
        "advertiser": "TechAfrica Academy",
        "position": "HOMEPAGE_MID",
        "ad_type": "BANNER",
        "image_url": UNSPLASH_IMAGES[2],
        "click_url": "https://geniesdafriquemedia.com/partenariats",
        "is_active": True,
    },
    {
        "title": "Business Africa Summit 2026",
        "advertiser": "Africa Business Network",
        "position": "ARTICLE_SIDEBAR",
        "ad_type": "SIDEBAR",
        "image_url": UNSPLASH_IMAGES[1],
        "click_url": "https://geniesdafriquemedia.com/partenariats",
        "is_active": True,
    },
    {
        "title": "Découvrez la Mode Africaine",
        "advertiser": "AfriStyle Fashion",
        "position": "ARTICLE_SIDEBAR",
        "ad_type": "SIDEBAR",
        "image_url": UNSPLASH_IMAGES[3],
        "click_url": "https://geniesdafriquemedia.com/partenariats",
        "is_active": True,
    },
    {
        "title": "Solutions Énergétiques Durables",
        "advertiser": "SolarAfrica Solutions",
        "position": "HOMEPAGE_TOP",
        "ad_type": "BANNER",
        "image_url": UNSPLASH_IMAGES[4],
        "click_url": "https://geniesdafriquemedia.com/partenariats",
        "is_active": True,
    },
    {
        "title": "Financement PME Africaines",
        "advertiser": "AfriBank Capital",
        "position": "ARTICLE_IN_BODY_1",
        "ad_type": "BANNER",
        "image_url": UNSPLASH_IMAGES[6],
        "click_url": "https://geniesdafriquemedia.com/partenariats",
        "is_active": True,
    },
    {
        "title": "Recrutement Talents Africains",
        "advertiser": "AfriTalent RH",
        "position": "ARTICLE_SIDEBAR",
        "ad_type": "SKYSCRAPER",
        "image_url": UNSPLASH_IMAGES[5],
        "click_url": "https://geniesdafriquemedia.com/partenariats",
        "is_active": True,
    },
    {
        "title": "Immobilier Premium Abidjan",
        "advertiser": "ImmoAfrique",
        "position": "HOMEPAGE_MID",
        "ad_type": "BANNER",
        "image_url": UNSPLASH_IMAGES[8],
        "click_url": "https://geniesdafriquemedia.com/partenariats",
        "is_active": True,
    },
    {
        "title": "Assurance Santé Africa Care",
        "advertiser": "Africa Care Insurance",
        "position": "ARTICLE_SIDEBAR",
        "ad_type": "SIDEBAR",
        "image_url": UNSPLASH_IMAGES[7],
        "click_url": "https://geniesdafriquemedia.com/partenariats",
        "is_active": True,
    },
    {
        "title": "Export Produits Africains vers Europe",
        "advertiser": "AfriTrade Export",
        "position": "ARTICLE_IN_BODY_2",
        "ad_type": "BANNER",
        "image_url": UNSPLASH_IMAGES[10],
        "click_url": "https://geniesdafriquemedia.com/partenariats",
        "is_active": True,
    },
    {
        "title": "Tourisme Durable en Afrique",
        "advertiser": "EcoTour Africa",
        "position": "ARTICLE_SIDEBAR",
        "ad_type": "SKYSCRAPER",
        "image_url": UNSPLASH_IMAGES[11],
        "click_url": "https://geniesdafriquemedia.com/partenariats",
        "is_active": True,
    },
    {
        "title": "Agriculture Intelligente Africa",
        "advertiser": "AgriTech Africa",
        "position": "HOMEPAGE_TOP",
        "ad_type": "BANNER",
        "image_url": UNSPLASH_IMAGES[9],
        "click_url": "https://geniesdafriquemedia.com/partenariats",
        "is_active": True,
    },
]

print(f"Création de {len(ADS_DATA)} publicités...")
created = 0
for ad_data in ADS_DATA:
    ad, created_flag = Advertisement.objects.get_or_create(
        title=ad_data["title"],
        defaults={
            "advertiser": ad_data["advertiser"],
            "position": ad_data["position"],
            "ad_type": ad_data["ad_type"],
            "image_url": ad_data["image_url"],
            "click_url": ad_data["click_url"],
            "is_active": ad_data["is_active"],
        }
    )
    if created_flag:
        created += 1
        print(f"  ✅ Créé: {ad.title}")
    else:
        print(f"  ⏭️  Existant: {ad.title}")

print(f"\n✅ {created} nouvelles publicités créées!")
print(f"📊 Total publicités: {Advertisement.objects.count()}")
