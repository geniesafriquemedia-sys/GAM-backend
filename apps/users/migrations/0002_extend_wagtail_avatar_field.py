"""
Migration to extend Wagtail UserProfile avatar field length.
Cloudinary paths can exceed 100 characters.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('wagtailusers', '0012_userprofile_theme'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE wagtailusers_userprofile ALTER COLUMN avatar TYPE varchar(255);",
            reverse_sql="ALTER TABLE wagtailusers_userprofile ALTER COLUMN avatar TYPE varchar(100);",
        ),
    ]
