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
