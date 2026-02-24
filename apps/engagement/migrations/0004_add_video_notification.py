# Generated manually on 2026-02-24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("engagement", "0003_add_article_notification"),
    ]

    operations = [
        migrations.CreateModel(
            name="VideoNotification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        verbose_name="Date de création",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Date de modification"
                    ),
                ),
                (
                    "video_id",
                    models.PositiveBigIntegerField(
                        db_index=True,
                        help_text="ID de la vidéo notifiée",
                        unique=True,
                        verbose_name="ID Vidéo",
                    ),
                ),
                (
                    "campaign_id",
                    models.CharField(
                        blank=True,
                        help_text="ID de la campagne Brevo",
                        max_length=100,
                        verbose_name="ID Campagne",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "En attente"),
                            ("sent", "Envoyé"),
                            ("failed", "Échoué"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "error_message",
                    models.TextField(blank=True, verbose_name="Message d'erreur"),
                ),
                (
                    "sent_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Date d'envoi"
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification vidéo",
                "verbose_name_plural": "Notifications vidéos",
                "ordering": ["-sent_at"],
            },
        ),
    ]
