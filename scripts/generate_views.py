import os
import sys
import django
import random

# Ajouter le dossier parent au path
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

django.setup()

from apps.editorial.models import Article

articles = Article.objects.all()

if not articles.exists():
    print("Aucun article trouve.")
    sys.exit(0)

print(f"Generation de vues pour {articles.count()} articles...")

for article in articles:
    if not article.views_count or article.views_count == 0:
        views = random.randint(1000, 50000)
        article.views_count = views
        article.save(update_fields=['views_count'])
        print(f"  OK: {article.title[:50]} -> {views:,} vues")
    else:
        print(f"  Skip: {article.title[:50]} -> {article.views_count:,} vues (existant)")

print("Vues generees pour tous les articles!")

top5 = Article.objects.order_by('-views_count')[:5]
print("\nTop 5 articles:")
for i, article in enumerate(top5, 1):
    print(f"  {i}. {article.title[:50]} -> {article.views_count:,} vues")
