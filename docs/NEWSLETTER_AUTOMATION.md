# Automatisation Newsletter - Geniesdafriquemedia

## Vue d'ensemble

Le système d'automatisation newsletter envoie automatiquement des emails aux abonnés lorsqu'un nouvel article ou une nouvelle vidéo est publié(e) sur la plateforme.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PUBLICATION                                  │
│  (Article ou Vidéo passe en statut "Publié" via Wagtail/Admin)     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      SIGNAL DJANGO                                   │
│  apps/editorial/signals.py                                          │
│  - send_newsletter_on_publish (articles)                            │
│  - send_newsletter_on_video_publish (vidéos)                        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   VÉRIFICATION DOUBLON                               │
│  apps/engagement/services.py                                         │
│  - Vérifie si notification déjà envoyée                             │
│  - ArticleNotification / VideoNotification                          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BREVO SERVICE                                   │
│  apps/engagement/services.py → BrevoService                         │
│  - Crée la campagne email                                           │
│  - Génère le HTML avec design professionnel                         │
│  - Envoie à tous les abonnés de la liste                           │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TRACKING & ADMIN                                  │
│  - ArticleNotification / VideoNotification                          │
│  - Visible dans Django Admin                                        │
│  - Statuts: pending, sent, failed                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Configuration

### Variables d'environnement (.env)

```bash
# Provider newsletter (brevo ou mailchimp)
NEWSLETTER_PROVIDER=brevo

# Clés API Brevo
BREVO_API_KEY=xkeysib-votre-cle-api
BREVO_LIST_ID=2

# Activer/désactiver les notifications automatiques
ENABLE_ARTICLE_NOTIFICATIONS=True

# URLs pour les liens dans les emails
FRONTEND_URL=https://gam-tunnel-front.geniesafriquemedia.workers.dev
BACKEND_URL=https://gam-tunnel-back.geniesafriquemedia.workers.dev
```

### Désactiver temporairement les notifications

Pour désactiver les notifications sans modifier le code :

```bash
ENABLE_ARTICLE_NOTIFICATIONS=False
```

## Fichiers clés

| Fichier | Description |
|---------|-------------|
| `apps/engagement/services.py` | Service Brevo, méthodes d'envoi |
| `apps/editorial/signals.py` | Signaux Django (déclencheurs) |
| `apps/engagement/models.py` | Modèles de tracking (ArticleNotification, VideoNotification) |
| `apps/engagement/admin.py` | Interface admin pour le suivi |
| `config/settings/base.py` | Configuration des paramètres |

## Fonctionnement détaillé

### 1. Déclenchement

Le signal `post_save` est déclenché à chaque sauvegarde d'un Article ou d'une Vidéo :

```python
@receiver(post_save, sender=Article)
def send_newsletter_on_publish(sender, instance, created, **kwargs):
    # Vérifie si le statut est "published"
    if instance.status != PublishableModel.PublicationStatus.PUBLISHED:
        return

    # Envoie la notification
    send_article_notification(instance)
```

### 2. Protection contre les doublons

Avant d'envoyer, le système vérifie si une notification a déjà été envoyée :

```python
if ArticleNotification.objects.filter(article_id=article.id).exists():
    return {'success': True, 'already_sent': True}
```

### 3. Génération de l'email

Le service Brevo génère un email HTML professionnel avec :
- En-tête Geniesdafriquemedia
- Image de l'article/vidéo
- Titre et extrait
- Bouton CTA "Lire l'article" / "Regarder la vidéo"
- Pied de page avec désabonnement

### 4. Envoi via Brevo API

```python
# Création de la campagne
response = self._make_request('POST', 'emailCampaigns', campaign_data)

# Envoi immédiat
send_response = self._make_request('POST', f'emailCampaigns/{campaign_id}/sendNow')
```

### 5. Tracking

Après envoi, une entrée est créée dans la base :

```python
ArticleNotification.objects.create(
    article_id=article.id,
    campaign_id=result.get('campaign_id', ''),
    status='sent'
)
```

## Interface Admin

Accédez au suivi des notifications via Django Admin :

- **URL**: `http://localhost:8000/admin/`
- **Sections**:
  - Engagement → Notifications articles
  - Engagement → Notifications vidéos

### Informations affichées

| Champ | Description |
|-------|-------------|
| ID Article/Vidéo | Identifiant du contenu |
| Statut | sent, pending, failed |
| ID Campagne | Référence Brevo |
| Date d'envoi | Timestamp de l'envoi |
| Message d'erreur | En cas d'échec |

## Commandes de test

### Créer des articles de test

```bash
python manage.py create_test_articles
```

### Créer des vidéos de test

```bash
python manage.py create_test_videos
```

## Dépannage

### Les notifications ne s'envoient pas

1. Vérifier `ENABLE_ARTICLE_NOTIFICATIONS=True` dans `.env`
2. Vérifier `BREVO_API_KEY` et `BREVO_LIST_ID`
3. Consulter les logs Django pour les erreurs
4. Vérifier que l'article/vidéo est bien en statut "published"

### Erreur "relation does not exist"

Exécuter les migrations :

```bash
python manage.py makemigrations engagement
python manage.py migrate
```

### Emails non reçus

1. Vérifier le dossier spam
2. Vérifier l'email de l'expéditeur dans Brevo
3. Consulter les statistiques de campagne dans Brevo

### Notifications en double

Le système empêche automatiquement les doublons. Si vous voyez des doublons :
- Vérifier les entrées dans ArticleNotification/VideoNotification
- Supprimer les entrées de test si nécessaire

## Design des emails

### Article
- Couleur primaire : `#f59e0b` (orange)
- En-tête sombre : `#18181b`
- Badge catégorie coloré
- Bouton CTA orange

### Vidéo
- Badge type vidéo rouge : `#dc2626`
- Miniature avec icône play
- Boutons : GAM (orange) + YouTube (rouge)

## Brevo Dashboard

Accédez à vos statistiques sur : https://app.brevo.com

- **Campagnes** : Historique des envois
- **Contacts** : Liste des abonnés
- **Statistiques** : Taux d'ouverture, clics, etc.

## Extension future

### Ajouter un nouveau type de contenu

1. Créer le modèle de notification (ex: `PodcastNotification`)
2. Ajouter la méthode d'envoi dans `BrevoService`
3. Créer la fonction dans `services.py`
4. Ajouter le signal dans `signals.py`
5. Enregistrer dans `admin.py`
6. Créer et appliquer les migrations

### Personnaliser le template email

Modifier les méthodes dans `BrevoService` :
- `send_article_notification()` → Template articles
- `send_video_notification()` → Template vidéos

## Support

Pour toute question :
- Email : geniesdafriquemedia@gmail.com
- Téléphone : +241 66 79 76 00
