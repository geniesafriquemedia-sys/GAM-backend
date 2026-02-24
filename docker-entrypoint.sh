#!/bin/bash
# =============================================================================
# GAM Backend - Docker Entrypoint Script
# Exécute les commandes d'initialisation avant de démarrer Gunicorn
# =============================================================================

set -e

echo "Starting GAM Backend..."

# Appliquer les migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Migrer les images Cloudinary → Supabase (idempotent : skip si déjà présentes)
if [ "${USE_SUPABASE}" = "True" ]; then
    echo "Migrating media from Cloudinary to Supabase..."
    python manage.py migrate_to_supabase || echo "Migration skipped or already complete."
fi

# Générer les vues pour les articles (une seule fois)
echo "Generating article views..."
python manage.py shell < scripts/generate_views.py || echo "Views generation skipped or already complete."

# Peupler les publicités (une seule fois)
echo "Populating advertisements..."
python manage.py shell < scripts/populate_ads.py || echo "Ads population skipped or already complete."

echo "Initialization complete!"

# Démarrer Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance
