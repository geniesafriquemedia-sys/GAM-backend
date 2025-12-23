"""
Engagement Services - Services pour la newsletter (US-10)
Intégration Brevo (ex-Sendinblue) et Mailchimp
"""

import logging
from typing import Optional, Dict, Any
from django.conf import settings
from django.utils import timezone
import requests

logger = logging.getLogger(__name__)


class NewsletterServiceError(Exception):
    """Exception pour les erreurs du service newsletter."""
    pass


class BaseNewsletterService:
    """Classe de base pour les services newsletter."""

    def subscribe(self, email: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    def unsubscribe(self, email: str) -> bool:
        raise NotImplementedError

    def get_subscriber(self, email: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class BrevoService(BaseNewsletterService):
    """
    Service d'intégration Brevo (ex-Sendinblue).
    Documentation: https://developers.brevo.com/
    """

    BASE_URL = 'https://api.brevo.com/v3'

    def __init__(self):
        self.api_key = settings.BREVO_API_KEY
        self.list_id = settings.BREVO_LIST_ID
        self.headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _make_request(self, method: str, endpoint: str, data: dict = None) -> requests.Response:
        """Effectue une requête vers l'API Brevo."""
        url = f'{self.BASE_URL}/{endpoint}'
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=10
            )
            return response
        except requests.RequestException as e:
            logger.error(f'Brevo API error: {e}')
            raise NewsletterServiceError(f'Erreur de connexion à Brevo: {e}')

    def subscribe(self, email: str, **kwargs) -> Dict[str, Any]:
        """
        Inscrit un email à la newsletter via Brevo.
        """
        data = {
            'email': email,
            'listIds': [int(self.list_id)] if self.list_id else [],
            'updateEnabled': True,
        }

        # Ajouter les attributs supplémentaires
        attributes = {}
        if kwargs.get('first_name'):
            attributes['PRENOM'] = kwargs['first_name']
        if kwargs.get('last_name'):
            attributes['NOM'] = kwargs['last_name']
        if attributes:
            data['attributes'] = attributes

        response = self._make_request('POST', 'contacts', data)

        if response.status_code in [200, 201, 204]:
            logger.info(f'Successfully subscribed {email} to Brevo')
            return {'success': True, 'id': response.json().get('id')}
        elif response.status_code == 400:
            error_data = response.json()
            if 'duplicate' in str(error_data).lower():
                return {'success': True, 'already_subscribed': True}
            raise NewsletterServiceError(f'Erreur Brevo: {error_data}')
        else:
            raise NewsletterServiceError(f'Erreur Brevo: {response.status_code}')

    def unsubscribe(self, email: str) -> bool:
        """
        Désabonne un email de la newsletter.
        """
        if not self.list_id:
            return True

        data = {
            'emails': [email]
        }

        response = self._make_request(
            'POST',
            f'contacts/lists/{self.list_id}/contacts/remove',
            data
        )

        if response.status_code in [200, 201, 204]:
            logger.info(f'Successfully unsubscribed {email} from Brevo')
            return True
        else:
            logger.error(f'Failed to unsubscribe {email}: {response.text}')
            return False

    def get_subscriber(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un abonné.
        """
        response = self._make_request('GET', f'contacts/{email}')

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            raise NewsletterServiceError(f'Erreur Brevo: {response.status_code}')


class MailchimpService(BaseNewsletterService):
    """
    Service d'intégration Mailchimp.
    Documentation: https://mailchimp.com/developer/marketing/api/
    """

    def __init__(self):
        self.api_key = settings.MAILCHIMP_API_KEY
        self.list_id = settings.MAILCHIMP_LIST_ID

        # Extraire le datacenter de la clé API
        if self.api_key and '-' in self.api_key:
            self.dc = self.api_key.split('-')[-1]
            self.base_url = f'https://{self.dc}.api.mailchimp.com/3.0'
        else:
            self.base_url = None

        self.headers = {
            'Content-Type': 'application/json',
        }
        self.auth = ('anystring', self.api_key)

    def _make_request(self, method: str, endpoint: str, data: dict = None) -> requests.Response:
        """Effectue une requête vers l'API Mailchimp."""
        if not self.base_url:
            raise NewsletterServiceError('Configuration Mailchimp invalide')

        url = f'{self.base_url}/{endpoint}'
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                auth=self.auth,
                json=data,
                timeout=10
            )
            return response
        except requests.RequestException as e:
            logger.error(f'Mailchimp API error: {e}')
            raise NewsletterServiceError(f'Erreur de connexion à Mailchimp: {e}')

    def _get_subscriber_hash(self, email: str) -> str:
        """Génère le hash MD5 de l'email pour l'API Mailchimp."""
        import hashlib
        return hashlib.md5(email.lower().encode()).hexdigest()

    def subscribe(self, email: str, **kwargs) -> Dict[str, Any]:
        """
        Inscrit un email à la newsletter via Mailchimp.
        """
        data = {
            'email_address': email,
            'status': 'subscribed',
        }

        # Ajouter les merge fields
        merge_fields = {}
        if kwargs.get('first_name'):
            merge_fields['FNAME'] = kwargs['first_name']
        if kwargs.get('last_name'):
            merge_fields['LNAME'] = kwargs['last_name']
        if merge_fields:
            data['merge_fields'] = merge_fields

        response = self._make_request(
            'POST',
            f'lists/{self.list_id}/members',
            data
        )

        if response.status_code in [200, 201]:
            result = response.json()
            logger.info(f'Successfully subscribed {email} to Mailchimp')
            return {'success': True, 'id': result.get('id')}
        elif response.status_code == 400:
            error_data = response.json()
            if 'already a list member' in str(error_data).lower():
                return {'success': True, 'already_subscribed': True}
            raise NewsletterServiceError(f'Erreur Mailchimp: {error_data}')
        else:
            raise NewsletterServiceError(f'Erreur Mailchimp: {response.status_code}')

    def unsubscribe(self, email: str) -> bool:
        """
        Désabonne un email de la newsletter.
        """
        subscriber_hash = self._get_subscriber_hash(email)
        data = {
            'status': 'unsubscribed'
        }

        response = self._make_request(
            'PATCH',
            f'lists/{self.list_id}/members/{subscriber_hash}',
            data
        )

        if response.status_code in [200, 204]:
            logger.info(f'Successfully unsubscribed {email} from Mailchimp')
            return True
        else:
            logger.error(f'Failed to unsubscribe {email}: {response.text}')
            return False

    def get_subscriber(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un abonné.
        """
        subscriber_hash = self._get_subscriber_hash(email)
        response = self._make_request(
            'GET',
            f'lists/{self.list_id}/members/{subscriber_hash}'
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            raise NewsletterServiceError(f'Erreur Mailchimp: {response.status_code}')


def get_newsletter_service() -> BaseNewsletterService:
    """
    Factory pour obtenir le service newsletter configuré.
    """
    provider = getattr(settings, 'NEWSLETTER_PROVIDER', 'brevo')

    if provider == 'mailchimp':
        return MailchimpService()
    else:
        return BrevoService()


def subscribe_to_newsletter(email: str, ip_address: str = None, source: str = '', **kwargs) -> Dict[str, Any]:
    """
    Fonction principale pour inscrire un email à la newsletter.
    Gère la création locale et la synchronisation avec le provider.
    """
    from .models import NewsletterSubscription

    # Vérifier si l'email existe déjà
    subscription, created = NewsletterSubscription.objects.get_or_create(
        email=email.lower(),
        defaults={
            'ip_address': ip_address,
            'source': source,
            'status': NewsletterSubscription.Status.CONFIRMED,
        }
    )

    if not created:
        if subscription.status == NewsletterSubscription.Status.UNSUBSCRIBED:
            # Réactiver l'abonnement
            subscription.status = NewsletterSubscription.Status.CONFIRMED
            subscription.confirmed_at = timezone.now()
            subscription.save()
        else:
            return {'success': True, 'already_subscribed': True}

    # Synchroniser avec le provider externe
    try:
        service = get_newsletter_service()
        result = service.subscribe(email, **kwargs)

        if result.get('id'):
            subscription.external_id = str(result['id'])
        subscription.synced_at = timezone.now()
        subscription.sync_error = ''
        subscription.save(update_fields=['external_id', 'synced_at', 'sync_error'])

        return {'success': True, 'created': created}

    except NewsletterServiceError as e:
        logger.error(f'Newsletter sync error for {email}: {e}')
        subscription.sync_error = str(e)
        subscription.save(update_fields=['sync_error'])

        # On retourne quand même succès car l'inscription locale a réussi
        return {'success': True, 'created': created, 'sync_warning': str(e)}
