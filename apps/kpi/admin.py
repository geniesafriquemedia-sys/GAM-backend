"""
KPI Admin
"""

from django.contrib import admin
from .models import PlatformKPI


@admin.register(PlatformKPI)
class PlatformKPIAdmin(admin.ModelAdmin):
    """Interface admin pour les KPI"""
    
    list_display = [
        'last_updated',
        'total_articles',
        'total_videos',
        'monthly_readers',
        'tv_experts',
        'is_active'
    ]
    
    list_filter = ['is_active', 'last_updated']
    
    fieldsets = (
        ('Métriques Éditoriales', {
            'fields': ('total_articles', 'total_videos')
        }),
        ('Métriques d\'Audience', {
            'fields': ('monthly_readers', 'total_views')
        }),
        ('Métriques Géographiques', {
            'fields': ('countries_covered',)
        }),
        ('Métriques Équipe', {
            'fields': ('tv_experts', 'total_authors')
        }),
        ('Métadonnées', {
            'fields': ('is_active', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['last_updated']
    
    actions = ['update_from_database']
    
    def update_from_database(self, request, queryset):
        """Action admin pour recalculer les KPIs"""
        for kpi in queryset:
            kpi.update_from_database()
        self.message_user(request, f"{queryset.count()} KPI(s) mis à jour depuis la base de données.")
    update_from_database.short_description = "Recalculer depuis la base de données"
