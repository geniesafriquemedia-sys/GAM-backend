import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
users = User.objects.all()
print("Utilisateurs existants :")
for user in users:
    print(f"Email: {user.email} | Username: {getattr(user, 'username', None)} | is_superuser: {user.is_superuser}")
