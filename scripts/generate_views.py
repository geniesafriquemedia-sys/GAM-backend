#!/usr/bin/env python
"""
Script pour générer des vues aléatoires sur les articles.
À exécuter une seule fois pour peupler les compteurs de vues.
"""

import os
import django
import random
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.editorial.models import Article

def generate_views():
    """Génère des vues aléatoires pour tous les articles publiés."""
    
    published_articles = Article.objects.filter(status='published')
    count = published_articles.count()
    
    if count == 0:
        print("❌ Aucun article publié trouvé")
        return
    
    print(f"📊 Génération de vues pour {count} articles...")
    
    updated = 0
    for article in published_articles:
        # Générer entre 1,000 et 50,000 vues
        views = random.randint(1000, 50000)
        
        article.views_count = views
        article.save(update_fields=['views_count'])
        
        updated += 1
        print(f"  ✓ {article.title[:50]}... → {views:,} vues")
    
    print(f"\n✅ {updated} articles mis à jour avec des vues!")
    
    # Afficher le top 5
    print("\n🔥 Top 5 articles les plus vus :")
    top_articles = Article.objects.filter(status='published').order_by('-views_count')[:5]
    for i, article in enumerate(top_articles, 1):
        print(f"  {i}. {article.title[:50]}... → {article.views_count:,} vues")

if __name__ == '__main__':
    generate_views()
