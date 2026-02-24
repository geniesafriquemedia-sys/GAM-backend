import os
import sys
import django
import random
from datetime import datetime, timedelta

# Ajouter le dossier parent au path
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
    'SIDEBAR',
    'ARTICLE_TOP',
    'ARTICLE_SIDEBAR',
    'ARTICLE_IN_BODY_1',
    'ARTICLE_IN_BODY_2',
    'VIDEO_PRE_ROLL',
    'FOOTER',
    'SEARCH_TOP',
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
    'MTN Africa', 'Orange Africa', 'Ecobank', 'Jumia', 'Dangote Group',
    'Air Afrique', 'Africa Finance', 'Safaricom', 'Andela', 'Flutterwave',
]

created = 0
start_date = datetime.now()
end_date = start_date + timedelta(days=90)

for i, position in enumerate(POSITIONS):
    try:
        ad = Advertisement(
            title=f"Publicite {ADVERTISERS[i % len(ADVERTISERS)]}",
            advertiser_name=ADVERTISERS[i % len(ADVERTISERS)],
            position=position,
            ad_type='BANNER',
            image_url=UNSPLASH_IMAGES[i % len(UNSPLASH_IMAGES)],
            target_url='https://geniesdafriquemedia.com',
            is_active=True,
            start_date=start_date,
            end_date=end_date,
            priority=random.randint(1, 10),
        )
        ad.save()
        created += 1
        print(f"  OK: {position} -> {ADVERTISERS[i % len(ADVERTISERS)]}")
    except Exception as e:
        print(f"  ERROR: {position} -> {e}")

print(f"\n{created} publicites creees avec succes!")
