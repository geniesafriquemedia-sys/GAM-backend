# =============================================================================
# GAM Backend - Django/Wagtail Dockerfile
# Multi-stage build pour optimiser la taille de l'image
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Base Python
# -----------------------------------------------------------------------------
FROM python:3.11-slim as base

# Variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

# Repertoire de travail
WORKDIR /app

# Installer les dependances systeme
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Stage 2: Builder - Installation des dependances Python
# -----------------------------------------------------------------------------
FROM base as builder

# Creer un virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier et installer les requirements
COPY requirements/ requirements/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements/production.txt

# -----------------------------------------------------------------------------
# Stage 3: Development
# -----------------------------------------------------------------------------
FROM base as development

# Copier le virtualenv depuis builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Installer les dependances de developpement
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/development.txt

# Copier le code source
COPY . .

# Exposer le port
EXPOSE 8000

# Commande de developpement
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# -----------------------------------------------------------------------------
# Stage 4: Production
# -----------------------------------------------------------------------------
FROM base as production

# Creer un utilisateur non-root
RUN groupadd -r gam && useradd -r -g gam gam

# Copier le virtualenv depuis builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier le code source
COPY --chown=gam:gam . .

# Copier et rendre executable l'entrypoint
COPY --chown=gam:gam docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Creer les repertoires necessaires
RUN mkdir -p /app/staticfiles /app/media /app/static && \
    chown -R gam:gam /app/staticfiles /app/media /app/static

# Passer a l'utilisateur non-root
USER gam

# Exposer le port
EXPOSE 8000

# Variables d'environnement de production
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Commande de production - Utiliser l'entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
