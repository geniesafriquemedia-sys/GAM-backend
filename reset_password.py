import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model

def reset_password(email, new_password):
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        print(f"Mot de passe changé pour {email}")
    except User.DoesNotExist:
        print(f"Utilisateur avec l'email {email} non trouvé.")

if __name__ == "__main__":
    reset_password("admin@geniesafriquemedia.com", "admin")
