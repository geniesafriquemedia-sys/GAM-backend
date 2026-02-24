import os
import sys
import django
import random
from datetime import date, timedelta
from django.core.files.base import ContentFile
import requests

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

django.setup()

from apps.advertising.models import Advertisement

# Verifier si des pubs existent deja
if Advertisement.objects.count() >= 10:
    print(f"Publicites deja presentes ({Advertisement.objects.count()}). Skip.")
    sys.exit(0)

print("Creation des publicites...")

POSITIONS = [
    'HOMEPAGE_TOP',
    'HOMEPAGE_MID',
    'ARTICLE_SIDEBAR',
    'ARTICLE_IN_BODY_1',
    'ARTICLE_IN_BODY_2',
    'CATEGORIES_TOP',
    'WEBTV_TOP',
    'FOOTER_BANNER',
]

UNSPLASH_IMAGES = [
    'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=728&h=90&fit=crop',
    'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=728&h=90&fit=crop',
    'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=728&h=90&fit=crop',
    'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=728&h=90&fit=crop',
    'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=728&h=90&fit=crop',
    'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=728&h=90&fit=crop',
    'https://images.unsplash.com/photo-1573164713988-8665fc963095?w=728&h=90&fit=crop',
    'https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=728&h=90&fit=crop',
    'https://images.unsplash.com/photo-1556761175-b413da4baf72?w=728&h=90&fit=crop',
    'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=728&h=90&fit=crop',
]

ADVERTISERS = [
    ('MTN Africa', 'contact@mtn.com'),
    ('Orange Africa', 'contact@orange.com'),
    ('Ecobank', 'contact@ecobank.com'),
    ('Jumia', 'contact@jumia.com'),
    ('Dangote Group', 'contact@dangote.com'),
    ('Africa Finance', 'contact@africafinance.com'),
    ('Safaricom', 'contact@safaricom.com'),
    ('Andela', 'contact@andela.com'),
    ('Flutterwave', 'contact@flutterwave.com'),
    ('Africa Tourism', 'contact@africatourism.com'),
]

created = 0
start_date = date.today()
end_date = start_date + timedelta(days=90)

for i, position in enumerate(POSITIONS):
    advertiser, email = ADVERTISERS[i % len(ADVERTISERS)]
    image_url = UNSPLASH_IMAGES[i % len(UNSPLASH_IMAGES)]

    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image_content = ContentFile(response.content)

        ad = Advertisement(
            title=f"Publicite {advertiser}",
            advertiser_name=advertiser,
            advertiser_email=email,
            advertiser_phone="+221000000000",
            notes="Publicite generee automatiquement",
            external_url='https://geniesdafriquemedia.com/partenariats',
            alt_text=f"Publicite {advertiser}",
            ad_type='BANNER',
            position=position,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            status='ACTIVE',
            price_per_month=0,
        )
        ad.image.save(f"ad_{position.lower()}_{i}.jpg", image_content, save=True)
        created += 1
        print(f"  OK: {position} -> {advertiser}")
    except Exception as e:
        print(f"  ERROR: {position} -> {e}")

print(f"\n{created} publicites creees avec succes!")
