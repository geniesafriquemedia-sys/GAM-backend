# Système de Formulaire de Contact - Geniesdafriquemedia

## Vue d'ensemble

Le système de formulaire de contact permet aux visiteurs d'envoyer des messages à l'équipe Geniesdafriquemedia. Chaque message soumis déclenche automatiquement un email de notification envoyé à l'adresse `geniesdafriquemedia@gmail.com`.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                               │
│  src/app/contact/page.tsx                                          │
│  - Formulaire avec validation côté client                          │
│  - États: loading, success, error                                  │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API ENDPOINT                                   │
│  POST /api/v1/engagement/contact/                                  │
│  - Validation des données                                          │
│  - Rate limiting (protection anti-spam)                            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (Django)                               │
│  apps/engagement/views.py → ContactMessageCreateView               │
│  - Sauvegarde du message en base de données                        │
│  - Déclenchement de la notification email                          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BREVO SERVICE                                    │
│  apps/engagement/services.py                                        │
│  - send_contact_notification()                                      │
│  - Envoi email transactionnel via API Brevo                        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EMAIL REÇU                                       │
│  geniesdafriquemedia@gmail.com                                      │
│  - Notification avec détails du message                            │
│  - Lien pour répondre directement                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Fichiers clés

### Backend

| Fichier | Description |
|---------|-------------|
| `apps/engagement/views.py` | Vue `ContactMessageCreateView` - traite les requêtes POST |
| `apps/engagement/services.py` | `send_contact_notification()` - envoi email via Brevo |
| `apps/engagement/models.py` | Modèle `ContactMessage` - stockage en base |
| `apps/engagement/serializers.py` | Validation des données entrantes |
| `apps/engagement/admin.py` | Interface admin pour gérer les messages |

### Frontend

| Fichier | Description |
|---------|-------------|
| `src/app/contact/page.tsx` | Page de contact avec formulaire |
| `src/lib/api/services/engagement.service.ts` | Service API `contactService` |
| `src/types/engagement.ts` | Types TypeScript `ContactRequest`, `ContactResponse` |

## Fonctionnement détaillé

### 1. Soumission du formulaire (Frontend)

```typescript
// src/app/contact/page.tsx
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  // Validation côté client
  const validation = validateContactForm(formData);
  if (!validation.isValid) {
    setErrors(validation.errors);
    return;
  }

  // Envoi à l'API
  const response = await contactService.send(formData);
};
```

### 2. Validation côté client

```typescript
// src/lib/api/services/engagement.service.ts
export function validateContactForm(data: ContactRequest): ContactValidationResult {
  const errors = {};

  // Nom: minimum 2 caractères
  if (!data.name || data.name.trim().length < 2) {
    errors.name = 'Le nom doit contenir au moins 2 caractères';
  }

  // Email: format valide
  if (!isValidEmail(data.email)) {
    errors.email = 'Veuillez entrer un email valide';
  }

  // Sujet: minimum 5 caractères
  if (!data.subject || data.subject.trim().length < 5) {
    errors.subject = 'Le sujet doit contenir au moins 5 caractères';
  }

  // Message: minimum 20 caractères
  if (!data.message || data.message.trim().length < 20) {
    errors.message = 'Le message doit contenir au moins 20 caractères';
  }

  return { isValid: Object.keys(errors).length === 0, errors };
}
```

### 3. Traitement Backend (Vue Django)

```python
# apps/engagement/views.py
class ContactMessageCreateView(generics.CreateAPIView):
    authentication_classes = []  # Public
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'contact'

    def create(self, request, *args, **kwargs):
        # Validation et sauvegarde
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Envoi notification email
        contact_message = serializer.instance
        result = send_contact_notification(contact_message)

        return Response({'message': 'Votre message a été envoyé avec succès.'})
```

### 4. Envoi de l'email (Service Brevo)

```python
# apps/engagement/services.py
def send_contact_notification(contact_message) -> Dict[str, Any]:
    admin_email = getattr(settings, 'CONTACT_ADMIN_EMAIL', 'geniesdafriquemedia@gmail.com')

    subject = f"[Contact GAM] {contact_message.subject}"

    # Template HTML professionnel
    html_content = f"""
    <html>
      <body>
        <h2>Nouveau message de contact</h2>
        <p><strong>De:</strong> {contact_message.name}</p>
        <p><strong>Email:</strong> {contact_message.email}</p>
        <p><strong>Sujet:</strong> {contact_message.subject}</p>
        <p><strong>Message:</strong></p>
        <p>{contact_message.message}</p>
        <a href="mailto:{contact_message.email}">Répondre</a>
      </body>
    </html>
    """

    brevo_service = BrevoService()
    return brevo_service.send_transactional_email(
        to_email=admin_email,
        subject=subject,
        html_content=html_content
    )
```

## Configuration

### Variables d'environnement (.env)

```bash
# Clés API Brevo
BREVO_API_KEY=xkeysib-votre-cle-api

# Email de réception des messages (optionnel, défaut: geniesdafriquemedia@gmail.com)
CONTACT_ADMIN_EMAIL=geniesdafriquemedia@gmail.com
```

### Rate Limiting (Protection anti-spam)

```python
# config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'contact': '5/hour',  # Maximum 5 messages par heure par IP
    },
}
```

Pour désactiver le rate limiting en développement :

```python
# config/settings/development.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'contact': None,
    },
}
```

## Interface Admin

### Accès

- **URL**: `http://localhost:8000/admin/engagement/contactmessage/`
- **Sections**: Engagement → Messages de contact

### Fonctionnalités

| Action | Description |
|--------|-------------|
| Voir les messages | Liste de tous les messages reçus |
| Marquer comme lu | Change le statut de "new" à "read" |
| Marquer comme répondu | Enregistre la date et l'utilisateur |
| Archiver | Déplace le message dans les archives |

### Statuts des messages

| Statut | Badge | Description |
|--------|-------|-------------|
| `new` | Bleu | Message non lu |
| `read` | Orange | Message consulté |
| `replied` | Vert | Réponse envoyée |
| `archived` | Gris | Message archivé |

## Design de l'email

L'email de notification envoyé à l'admin inclut :

- **En-tête** : Logo et nom Geniesdafriquemedia
- **Informations expéditeur** : Nom, email, sujet
- **Corps du message** : Message complet du visiteur
- **Bouton CTA** : "Répondre" (lien mailto)
- **Pied de page** : Indication que c'est un message automatique

### Aperçu

```
┌─────────────────────────────────────────────┐
│  🌍 GENIESDAFRIQUEMEDIA                     │
│  Nouveau message de contact                 │
├─────────────────────────────────────────────┤
│                                             │
│  De: Jean Dupont                            │
│  Email: jean@example.com                    │
│  Sujet: Proposition de partenariat          │
│                                             │
│  ─────────────────────────────              │
│                                             │
│  Bonjour,                                   │
│                                             │
│  Je souhaiterais discuter d'un              │
│  partenariat avec votre média...            │
│                                             │
│  ─────────────────────────────              │
│                                             │
│  [ Répondre à ce message ]                  │
│                                             │
├─────────────────────────────────────────────┤
│  Message reçu le 25/12/2024 à 10:30         │
│  Ceci est un email automatique              │
└─────────────────────────────────────────────┘
```

## États du formulaire (Frontend)

Le formulaire gère plusieurs états visuels :

### 1. État initial
- Tous les champs vides et activés
- Bouton "Envoyer le message" actif

### 2. Validation en cours
- Erreurs affichées sous chaque champ invalide
- Bordure rouge sur les champs en erreur

### 3. Envoi en cours
- Tous les champs désactivés
- Spinner sur le bouton
- Texte "Envoi en cours..."

### 4. Succès
- Message vert "Votre message a été envoyé avec succès !"
- Formulaire réinitialisé

### 5. Erreur
- Message rouge avec détail de l'erreur
- Champs réactivés pour correction

## Dépannage

### Les emails ne sont pas reçus

1. Vérifier `BREVO_API_KEY` dans `.env`
2. Vérifier les logs Django pour les erreurs
3. Consulter le tableau de bord Brevo pour les emails transactionnels
4. Vérifier le dossier spam

### Erreur 429 (Too Many Requests)

Le rate limiting bloque les requêtes excessives. Attendre 1 heure ou désactiver temporairement en développement.

### Erreur de validation

Les champs doivent respecter :
- Nom : minimum 2 caractères
- Email : format valide
- Sujet : minimum 5 caractères
- Message : minimum 20 caractères

## API Endpoint

### POST /api/v1/engagement/contact/

**Request Body:**
```json
{
  "name": "Jean Dupont",
  "email": "jean@example.com",
  "subject": "Proposition de partenariat",
  "message": "Bonjour, je souhaiterais discuter d'un partenariat..."
}
```

**Success Response (201):**
```json
{
  "message": "Votre message a été envoyé avec succès."
}
```

**Validation Error (400):**
```json
{
  "name": ["Ce champ est obligatoire."],
  "message": ["Le message doit contenir au moins 20 caractères."]
}
```

**Rate Limit Error (429):**
```json
{
  "detail": "Requête limitée. Attendez 3600 secondes."
}
```

## Support

Pour toute question :
- Email : geniesdafriquemedia@gmail.com
- Téléphone : +241 66 79 76 00
