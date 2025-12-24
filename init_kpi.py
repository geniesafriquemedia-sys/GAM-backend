"""
Script pour initialiser les KPIs
Exécuter avec: python init_kpi.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.kpi.models import PlatformKPI

def init_kpi():
    """Initialise ou met à jour les KPIs"""
    print("🔄 Initialisation des KPIs...")
    
    # Récupérer ou créer l'instance KPI
    kpi = PlatformKPI.get_active()
    
    print(f"📊 KPI trouvé: {kpi}")
    print("🔄 Calcul des métriques depuis la base de données...")
    
    # Mettre à jour depuis la base de données
    kpi.update_from_database()
    
    print("\n✅ KPIs mis à jour avec succès!")
    print(f"📈 Articles publiés: {kpi.total_articles}")
    print(f"📹 Vidéos publiées: {kpi.total_videos}")
    print(f"👥 Auteurs actifs: {kpi.total_authors}")
    print(f"🎬 Experts TV: {kpi.tv_experts}")
    print(f"🌍 Pays couverts: {kpi.countries_covered}")
    print(f"📊 Lecteurs mensuels: {kpi.monthly_readers}")
    print(f"👁️ Vues totales: {kpi.total_views}")
    print(f"🕐 Dernière mise à jour: {kpi.last_updated}")

if __name__ == '__main__':
    init_kpi()
