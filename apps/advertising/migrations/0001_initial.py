"""
Migration initiale pour apps.advertising
"""

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Date de création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Date de modification')),
                ('title', models.CharField(help_text='Nom interne pour identifier la campagne (non visible sur le site)', max_length=255, verbose_name='Nom interne')),
                ('advertiser_name', models.CharField(max_length=255, verbose_name='Nom du client')),
                ('advertiser_email', models.EmailField(max_length=254, verbose_name='Email du client')),
                ('advertiser_phone', models.CharField(blank=True, max_length=50, verbose_name='Téléphone')),
                ('notes', models.TextField(blank=True, verbose_name='Notes admin')),
                ('image', models.ImageField(help_text='Dimensions recommandées selon le type (Leaderboard: 970x90, Sidebar: 300x250, etc.)', upload_to='advertising/', verbose_name='Image publicitaire')),
                ('external_url', models.URLField(max_length=500, verbose_name='URL de destination (clic)')),
                ('alt_text', models.CharField(blank=True, help_text="Texte alternatif pour l'accessibilité", max_length=255, verbose_name='Texte alternatif')),
                ('ad_type', models.CharField(
                    choices=[
                        ('LEADERBOARD', 'Leaderboard (970x90)'),
                        ('BANNER', 'Banner (728x90)'),
                        ('SIDEBAR', 'Sidebar (300x250)'),
                        ('NATIVE', 'Native (inline article)'),
                        ('IN_ARTICLE', 'In-Article'),
                        ('INTERSTITIEL', 'Interstitiel'),
                    ],
                    default='BANNER',
                    max_length=20,
                    verbose_name='Type de publicité'
                )),
                ('position', models.CharField(
                    choices=[
                        ('HOMEPAGE_TOP', 'Homepage – Haut'),
                        ('HOMEPAGE_MID', 'Homepage – Milieu'),
                        ('ARTICLE_SIDEBAR', 'Article – Sidebar'),
                        ('ARTICLE_IN_BODY_1', 'Article – Dans le corps 1'),
                        ('ARTICLE_IN_BODY_2', 'Article – Dans le corps 2'),
                        ('CATEGORIES_TOP', 'Page Catégories – Haut'),
                        ('WEBTV_TOP', 'Web TV – Haut'),
                        ('FOOTER_BANNER', 'Footer – Bannière'),
                    ],
                    default='HOMEPAGE_TOP',
                    max_length=30,
                    verbose_name='Position'
                )),
                ('start_date', models.DateField(verbose_name='Date de début')),
                ('end_date', models.DateField(verbose_name='Date de fin')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activée')),
                ('status', models.CharField(
                    choices=[
                        ('DRAFT', 'Brouillon'),
                        ('ACTIVE', 'Active'),
                        ('PAUSED', 'En pause'),
                        ('EXPIRED', 'Expirée'),
                    ],
                    default='DRAFT',
                    max_length=10,
                    verbose_name='Statut'
                )),
                ('impressions_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='Impressions')),
                ('clicks_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='Clics')),
                ('price_per_month', models.DecimalField(decimal_places=2, default=0, help_text='Informationnel uniquement – facturation manuelle', max_digits=8, verbose_name='Prix mensuel (€)')),
            ],
            options={
                'verbose_name': 'Publicité',
                'verbose_name_plural': 'Publicités',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='advertisement',
            index=models.Index(fields=['position', 'status', 'start_date', 'end_date'], name='advertising_positio_idx'),
        ),
        migrations.AddIndex(
            model_name='advertisement',
            index=models.Index(fields=['is_active', 'status'], name='advertising_is_acti_idx'),
        ),
    ]
