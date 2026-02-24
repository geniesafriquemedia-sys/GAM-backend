"""
Advertising Admin - Interface Django admin standard
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'advertiser_name', 'ad_type', 'position',
        'status', 'start_date', 'end_date',
        'impressions_count', 'clicks_count', 'ctr_display',
        'is_currently_active',
    ]
    list_filter = ['status', 'ad_type', 'position', 'is_active']
    search_fields = ['title', 'advertiser_name', 'advertiser_email']
    readonly_fields = ['impressions_count', 'clicks_count', 'created_at', 'updated_at', 'image_preview']
    date_hierarchy = 'start_date'
    ordering = ['-created_at']

    fieldsets = (
        ('Informations client', {
            'fields': ('title', 'advertiser_name', 'advertiser_email', 'advertiser_phone', 'notes')
        }),
        ('Contenu publicitaire', {
            'fields': ('image', 'image_preview', 'external_url', 'alt_text')
        }),
        ('Placement', {
            'fields': ('ad_type', 'position')
        }),
        ('Planification', {
            'fields': ('start_date', 'end_date', 'status', 'is_active', 'price_per_month')
        }),
        ('Statistiques', {
            'fields': ('impressions_count', 'clicks_count'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def ctr_display(self, obj):
        return f"{obj.ctr}%"
    ctr_display.short_description = 'CTR'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:80px;max-width:200px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Aperçu'

    def is_currently_active(self, obj):
        return obj.is_currently_active
    is_currently_active.boolean = True
    is_currently_active.short_description = 'Active maintenant'
