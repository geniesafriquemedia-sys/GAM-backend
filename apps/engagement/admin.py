"""
Engagement Admin - Administration des inscriptions newsletter et contacts
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import NewsletterSubscription, ContactMessage, ArticleNotification, VideoNotification


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    """Administration des inscriptions newsletter."""

    list_display = [
        'email', 'status_badge', 'source', 'synced_status',
        'confirmed_at', 'created_at'
    ]
    list_filter = ['status', 'source', 'created_at']
    search_fields = ['email']
    ordering = ['-created_at']
    readonly_fields = [
        'ip_address', 'external_id', 'synced_at', 'sync_error',
        'confirmed_at', 'unsubscribed_at', 'created_at', 'updated_at'
    ]

    fieldsets = (
        (None, {
            'fields': ('email', 'status', 'source')
        }),
        ('Synchronisation', {
            'fields': ('external_id', 'synced_at', 'sync_error'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('ip_address', 'confirmed_at', 'unsubscribed_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'confirmed': '#28A745',
            'unsubscribed': '#DC3545',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'

    def synced_status(self, obj):
        if obj.sync_error:
            return format_html(
                '<span style="color: #DC3545;">❌ Erreur</span>'
            )
        elif obj.synced_at:
            return format_html(
                '<span style="color: #28A745;">✓ Synchronisé</span>'
            )
        return format_html(
            '<span style="color: #6C757D;">⏳ En attente</span>'
        )
    synced_status.short_description = 'Sync'

    actions = ['confirm_subscriptions', 'export_emails']

    @admin.action(description='Confirmer les inscriptions sélectionnées')
    def confirm_subscriptions(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(
            status=NewsletterSubscription.Status.PENDING
        ).update(
            status=NewsletterSubscription.Status.CONFIRMED,
            confirmed_at=timezone.now()
        )
        self.message_user(request, f'{updated} inscription(s) confirmée(s).')

    @admin.action(description='Exporter les emails (copier dans presse-papier)')
    def export_emails(self, request, queryset):
        emails = list(queryset.values_list('email', flat=True))
        self.message_user(
            request,
            f'{len(emails)} email(s) : {", ".join(emails[:10])}{"..." if len(emails) > 10 else ""}'
        )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Administration des messages de contact."""

    list_display = [
        'subject', 'name', 'email', 'status_badge',
        'replied_by', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    ordering = ['-created_at']
    readonly_fields = [
        'ip_address', 'replied_at', 'replied_by', 'created_at', 'updated_at'
    ]

    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'subject')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Statut', {
            'fields': ('status', 'replied_at', 'replied_by')
        }),
        ('Métadonnées', {
            'fields': ('ip_address', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'new': '#007BFF',
            'read': '#FFA500',
            'replied': '#28A745',
            'archived': '#6C757D',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'

    actions = ['mark_as_read', 'mark_as_replied', 'archive_messages']

    @admin.action(description='Marquer comme lu')
    def mark_as_read(self, request, queryset):
        updated = queryset.filter(
            status=ContactMessage.Status.NEW
        ).update(status=ContactMessage.Status.READ)
        self.message_user(request, f'{updated} message(s) marqué(s) comme lu(s).')

    @admin.action(description='Marquer comme répondu')
    def mark_as_replied(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status=ContactMessage.Status.REPLIED,
            replied_at=timezone.now(),
            replied_by=request.user
        )
        self.message_user(request, f'{updated} message(s) marqué(s) comme répondu(s).')

    @admin.action(description='Archiver')
    def archive_messages(self, request, queryset):
        updated = queryset.update(status=ContactMessage.Status.ARCHIVED)
        self.message_user(request, f'{updated} message(s) archivé(s).')


@admin.register(ArticleNotification)
class ArticleNotificationAdmin(admin.ModelAdmin):
    """Administration des notifications d'articles."""

    list_display = [
        'article_id', 'status_badge', 'campaign_id', 'sent_at'
    ]
    list_filter = ['status', 'sent_at']
    search_fields = ['article_id', 'campaign_id']
    ordering = ['-sent_at']
    readonly_fields = ['article_id', 'campaign_id', 'status', 'error_message', 'sent_at']

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'sent': '#28A745',
            'failed': '#DC3545',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'

    def has_add_permission(self, request):
        return False  # Les notifications sont créées automatiquement

    def has_change_permission(self, request, obj=None):
        return False  # Lecture seule


@admin.register(VideoNotification)
class VideoNotificationAdmin(admin.ModelAdmin):
    """Administration des notifications de vidéos."""

    list_display = [
        'video_id', 'status_badge', 'campaign_id', 'sent_at'
    ]
    list_filter = ['status', 'sent_at']
    search_fields = ['video_id', 'campaign_id']
    ordering = ['-sent_at']
    readonly_fields = ['video_id', 'campaign_id', 'status', 'error_message', 'sent_at']

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'sent': '#28A745',
            'failed': '#DC3545',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'

    def has_add_permission(self, request):
        return False  # Les notifications sont créées automatiquement

    def has_change_permission(self, request, obj=None):
        return False  # Lecture seule
