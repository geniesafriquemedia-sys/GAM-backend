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
        # Construire la liste des IDs de liste
        list_ids = []
        if self.list_id:
            try:
                list_ids = [int(self.list_id)]
            except (ValueError, TypeError):
                logger.warning(f'Invalid BREVO_LIST_ID: {self.list_id}')

        data = {
            'email': email,
            'listIds': list_ids,
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
            # 204 = No Content, pas de body JSON
            if response.status_code == 204 or not response.text:
                return {'success': True}
            try:
                return {'success': True, 'id': response.json().get('id')}
            except Exception:
                return {'success': True}
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

    def send_article_notification(
        self,
        article_title: str,
        article_excerpt: str,
        article_url: str,
        article_image_url: str = '',
        author_name: str = '',
        category_name: str = ''
    ) -> Dict[str, Any]:
        """
        Envoie une notification email à tous les abonnés pour un nouvel article.
        Utilise l'API Brevo pour créer et envoyer une campagne.
        """
        if not self.list_id:
            raise NewsletterServiceError('BREVO_LIST_ID non configuré')

        # Créer le contenu HTML de l'email
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f5f5;padding:40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color:#18181b;padding:30px;text-align:center;">
                            <h1 style="margin:0;color:#ffffff;font-size:24px;font-weight:800;">Geniesdafriquemedia</h1>
                            <p style="margin:10px 0 0;color:#a1a1aa;font-size:12px;text-transform:uppercase;letter-spacing:2px;">Nouvel Article</p>
                        </td>
                    </tr>

                    <!-- Image -->
                    {f'<tr><td><img src="{article_image_url}" width="600" style="width:100%;height:auto;display:block;" alt="{article_title}"></td></tr>' if article_image_url else ''}

                    <!-- Content -->
                    <tr>
                        <td style="padding:40px;">
                            <!-- Category Badge -->
                            {f'<p style="margin:0 0 15px;"><span style="background-color:#f59e0b;color:#ffffff;padding:6px 16px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">{category_name}</span></p>' if category_name else ''}

                            <!-- Title -->
                            <h2 style="margin:0 0 20px;font-size:28px;font-weight:800;color:#18181b;line-height:1.3;">
                                {article_title}
                            </h2>

                            <!-- Author -->
                            {f'<p style="margin:0 0 20px;color:#71717a;font-size:14px;">Par <strong>{author_name}</strong></p>' if author_name else ''}

                            <!-- Excerpt -->
                            <p style="margin:0 0 30px;color:#52525b;font-size:16px;line-height:1.7;">
                                {article_excerpt}
                            </p>

                            <!-- CTA Button -->
                            <a href="{article_url}" style="display:inline-block;background-color:#f59e0b;color:#ffffff;padding:16px 32px;border-radius:12px;text-decoration:none;font-weight:700;font-size:14px;text-transform:uppercase;letter-spacing:1px;">
                                Lire l'article →
                            </a>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color:#fafafa;padding:30px;text-align:center;border-top:1px solid #e5e5e5;">
                            <p style="margin:0 0 10px;color:#71717a;font-size:12px;">
                                Vous recevez cet email car vous êtes inscrit à notre newsletter.
                            </p>
                            <p style="margin:0;color:#a1a1aa;font-size:11px;">
                                © 2025 Geniesdafriquemedia. Tous droits réservés.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''

        # Créer la campagne
        campaign_data = {
            'name': f'Nouvel article: {article_title[:50]}',
            'subject': f'🆕 {article_title}',
            'sender': {
                'name': 'Geniesdafriquemedia',
                'email': 'geniesdafriquemedia@gmail.com'
            },
            'type': 'classic',
            'htmlContent': html_content,
            'recipients': {
                'listIds': [int(self.list_id)]
            },
        }

        # Créer la campagne
        response = self._make_request('POST', 'emailCampaigns', campaign_data)

        if response.status_code in [200, 201]:
            campaign_id = response.json().get('id')
            logger.info(f'Campaign created: {campaign_id}')

            # Envoyer immédiatement la campagne
            send_response = self._make_request('POST', f'emailCampaigns/{campaign_id}/sendNow')

            if send_response.status_code in [200, 201, 204]:
                logger.info(f'Campaign {campaign_id} sent successfully')
                return {'success': True, 'campaign_id': campaign_id}
            else:
                logger.error(f'Failed to send campaign: {send_response.text}')
                raise NewsletterServiceError(f'Erreur envoi campagne: {send_response.status_code}')
        else:
            logger.error(f'Failed to create campaign: {response.text}')
            raise NewsletterServiceError(f'Erreur création campagne: {response.status_code}')

    def send_transactional_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        reply_to_email: str = None,
        reply_to_name: str = None
    ) -> Dict[str, Any]:
        """
        Envoie un email transactionnel via Brevo.
        Utilisé pour les notifications de contact, confirmations, etc.
        """
        data = {
            'sender': {
                'name': 'Geniesdafriquemedia',
                'email': 'geniesdafriquemedia@gmail.com'
            },
            'to': [
                {
                    'email': to_email,
                    'name': to_name
                }
            ],
            'subject': subject,
            'htmlContent': html_content
        }

        if reply_to_email:
            data['replyTo'] = {
                'email': reply_to_email,
                'name': reply_to_name or reply_to_email
            }

        response = self._make_request('POST', 'smtp/email', data)

        if response.status_code in [200, 201, 202]:
            message_id = response.json().get('messageId', '')
            logger.info(f'Transactional email sent to {to_email}: {message_id}')
            return {'success': True, 'message_id': message_id}
        else:
            logger.error(f'Failed to send transactional email: {response.text}')
            raise NewsletterServiceError(f'Erreur envoi email: {response.status_code}')

    def send_video_notification(
        self,
        video_title: str,
        video_description: str,
        video_url: str,
        video_thumbnail_url: str = '',
        video_type: str = '',
        youtube_url: str = ''
    ) -> Dict[str, Any]:
        """
        Envoie une notification email à tous les abonnés pour une nouvelle vidéo.
        """
        if not self.list_id:
            raise NewsletterServiceError('BREVO_LIST_ID non configuré')

        # Créer le contenu HTML de l'email
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f5f5;padding:40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color:#18181b;padding:30px;text-align:center;">
                            <h1 style="margin:0;color:#ffffff;font-size:24px;font-weight:800;">Geniesdafriquemedia</h1>
                            <p style="margin:10px 0 0;color:#a1a1aa;font-size:12px;text-transform:uppercase;letter-spacing:2px;">📺 Nouvelle Vidéo Web TV</p>
                        </td>
                    </tr>

                    <!-- Thumbnail avec play button -->
                    {f'''<tr>
                        <td style="position:relative;">
                            <a href="{video_url}" style="display:block;position:relative;">
                                <img src="{video_thumbnail_url}" width="600" style="width:100%;height:auto;display:block;" alt="{video_title}">
                                <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:80px;height:80px;background-color:rgba(245,158,11,0.9);border-radius:50%;display:flex;align-items:center;justify-content:center;">
                                    <div style="width:0;height:0;border-top:15px solid transparent;border-bottom:15px solid transparent;border-left:25px solid white;margin-left:5px;"></div>
                                </div>
                            </a>
                        </td>
                    </tr>''' if video_thumbnail_url else ''}

                    <!-- Content -->
                    <tr>
                        <td style="padding:40px;">
                            <!-- Video Type Badge -->
                            {f'<p style="margin:0 0 15px;"><span style="background-color:#dc2626;color:#ffffff;padding:6px 16px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">▶ {video_type}</span></p>' if video_type else ''}

                            <!-- Title -->
                            <h2 style="margin:0 0 20px;font-size:28px;font-weight:800;color:#18181b;line-height:1.3;">
                                {video_title}
                            </h2>

                            <!-- Description -->
                            <p style="margin:0 0 30px;color:#52525b;font-size:16px;line-height:1.7;">
                                {video_description[:300]}{'...' if len(video_description) > 300 else ''}
                            </p>

                            <!-- CTA Buttons -->
                            <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
                                <tr>
                                    <td style="padding-right:10px;">
                                        <a href="{video_url}" style="display:inline-block;background-color:#f59e0b;color:#ffffff;padding:16px 32px;border-radius:12px;text-decoration:none;font-weight:700;font-size:14px;text-transform:uppercase;letter-spacing:1px;">
                                            Regarder sur GAM →
                                        </a>
                                    </td>
                                    {f'<td><a href="{youtube_url}" style="display:inline-block;background-color:#dc2626;color:#ffffff;padding:16px 32px;border-radius:12px;text-decoration:none;font-weight:700;font-size:14px;text-transform:uppercase;letter-spacing:1px;">▶ YouTube</a></td>' if youtube_url else ''}
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color:#fafafa;padding:30px;text-align:center;border-top:1px solid #e5e5e5;">
                            <p style="margin:0 0 10px;color:#71717a;font-size:12px;">
                                Vous recevez cet email car vous êtes inscrit à notre newsletter.
                            </p>
                            <p style="margin:0;color:#a1a1aa;font-size:11px;">
                                © 2025 Geniesdafriquemedia. Tous droits réservés.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''

        # Créer la campagne
        campaign_data = {
            'name': f'Nouvelle vidéo: {video_title[:50]}',
            'subject': f'📺 {video_title}',
            'sender': {
                'name': 'Geniesdafriquemedia',
                'email': 'geniesdafriquemedia@gmail.com'
            },
            'type': 'classic',
            'htmlContent': html_content,
            'recipients': {
                'listIds': [int(self.list_id)]
            },
        }

        # Créer la campagne
        response = self._make_request('POST', 'emailCampaigns', campaign_data)

        if response.status_code in [200, 201]:
            campaign_id = response.json().get('id')
            logger.info(f'Video campaign created: {campaign_id}')

            # Envoyer immédiatement la campagne
            send_response = self._make_request('POST', f'emailCampaigns/{campaign_id}/sendNow')

            if send_response.status_code in [200, 201, 204]:
                logger.info(f'Video campaign {campaign_id} sent successfully')
                return {'success': True, 'campaign_id': campaign_id}
            else:
                logger.error(f'Failed to send video campaign: {send_response.text}')
                raise NewsletterServiceError(f'Erreur envoi campagne vidéo: {send_response.status_code}')
        else:
            logger.error(f'Failed to create video campaign: {response.text}')
            raise NewsletterServiceError(f'Erreur création campagne vidéo: {response.status_code}')


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
            'confirmed_at': timezone.now(),
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


def send_article_notification(article) -> Dict[str, Any]:
    """
    Envoie une notification email pour un nouvel article publié.
    Évite les doublons en vérifiant si une notification a déjà été envoyée.
    """
    from .models import ArticleNotification

    # Vérifier si une notification a déjà été envoyée pour cet article
    if ArticleNotification.objects.filter(article_id=article.id).exists():
        logger.info(f'Notification already sent for article {article.id}')
        return {'success': True, 'already_sent': True}

    # Construire l'URL de l'article
    frontend_url = getattr(settings, 'FRONTEND_URL', 'https://geniesdafriquemedia.com')
    article_url = f'{frontend_url}/articles/{article.slug}'

    # Construire l'URL de l'image
    article_image_url = ''
    if article.image_url:
        if article.image_url.startswith('http'):
            article_image_url = article.image_url
        else:
            backend_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
            article_image_url = f'{backend_url}{article.image_url}'

    try:
        service = get_newsletter_service()

        # Vérifier que le service supporte les notifications
        if not hasattr(service, 'send_article_notification'):
            logger.warning('Newsletter service does not support article notifications')
            return {'success': False, 'error': 'Service non supporté'}

        result = service.send_article_notification(
            article_title=article.title,
            article_excerpt=article.excerpt or '',
            article_url=article_url,
            article_image_url=article_image_url,
            author_name=article.author.name if article.author else '',
            category_name=article.category.name if article.category else ''
        )

        # Enregistrer la notification envoyée
        ArticleNotification.objects.create(
            article_id=article.id,
            campaign_id=result.get('campaign_id', ''),
            status='sent'
        )

        logger.info(f'Article notification sent for: {article.title}')
        return result

    except NewsletterServiceError as e:
        logger.error(f'Failed to send article notification: {e}')

        # Enregistrer l'échec
        ArticleNotification.objects.create(
            article_id=article.id,
            status='failed',
            error_message=str(e)
        )

        return {'success': False, 'error': str(e)}


def send_video_notification(video) -> Dict[str, Any]:
    """
    Envoie une notification email pour une nouvelle vidéo publiée.
    Évite les doublons en vérifiant si une notification a déjà été envoyée.
    """
    from .models import VideoNotification

    # Vérifier si une notification a déjà été envoyée pour cette vidéo
    if VideoNotification.objects.filter(video_id=video.id).exists():
        logger.info(f'Notification already sent for video {video.id}')
        return {'success': True, 'already_sent': True}

    # Construire l'URL de la vidéo
    frontend_url = getattr(settings, 'FRONTEND_URL', 'https://geniesdafriquemedia.com')
    video_url = f'{frontend_url}/web-tv/{video.slug}'

    # Construire l'URL de la miniature
    video_thumbnail_url = ''
    if video.thumbnail_url:
        if video.thumbnail_url.startswith('http'):
            video_thumbnail_url = video.thumbnail_url
        else:
            backend_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
            video_thumbnail_url = f'{backend_url}{video.thumbnail_url}'

    try:
        service = get_newsletter_service()

        # Vérifier que le service supporte les notifications vidéo
        if not hasattr(service, 'send_video_notification'):
            logger.warning('Newsletter service does not support video notifications')
            return {'success': False, 'error': 'Service non supporté'}

        result = service.send_video_notification(
            video_title=video.title,
            video_description=video.description or '',
            video_url=video_url,
            video_thumbnail_url=video_thumbnail_url,
            video_type=video.get_video_type_display() if hasattr(video, 'get_video_type_display') else '',
            youtube_url=video.youtube_url or ''
        )

        # Enregistrer la notification envoyée
        VideoNotification.objects.create(
            video_id=video.id,
            campaign_id=result.get('campaign_id', ''),
            status='sent'
        )

        logger.info(f'Video notification sent for: {video.title}')
        return result

    except NewsletterServiceError as e:
        logger.error(f'Failed to send video notification: {e}')

        # Enregistrer l'échec
        VideoNotification.objects.create(
            video_id=video.id,
            status='failed',
            error_message=str(e)
        )

        return {'success': False, 'error': str(e)}


def send_contact_notification(contact_message) -> Dict[str, Any]:
    """
    Envoie une notification email à l'admin quand un message de contact est reçu.
    """
    admin_email = getattr(settings, 'CONTACT_ADMIN_EMAIL', 'geniesdafriquemedia@gmail.com')
    admin_name = getattr(settings, 'CONTACT_ADMIN_NAME', 'Geniesdafriquemedia')

    # Créer le contenu HTML de l'email
    html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f5f5;padding:40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color:#18181b;padding:30px;text-align:center;">
                            <h1 style="margin:0;color:#ffffff;font-size:24px;font-weight:800;">Geniesdafriquemedia</h1>
                            <p style="margin:10px 0 0;color:#a1a1aa;font-size:12px;text-transform:uppercase;letter-spacing:2px;">📩 Nouveau Message de Contact</p>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding:40px;">
                            <!-- Alert Badge -->
                            <p style="margin:0 0 20px;">
                                <span style="background-color:#3b82f6;color:#ffffff;padding:8px 20px;border-radius:20px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">
                                    Nouveau message
                                </span>
                            </p>

                            <!-- Sender Info -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:30px;background-color:#f9fafb;border-radius:12px;padding:20px;">
                                <tr>
                                    <td style="padding:15px;">
                                        <p style="margin:0 0 10px;color:#6b7280;font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">De</p>
                                        <p style="margin:0;color:#18181b;font-size:18px;font-weight:700;">{contact_message.name}</p>
                                        <p style="margin:5px 0 0;color:#3b82f6;font-size:14px;">
                                            <a href="mailto:{contact_message.email}" style="color:#3b82f6;text-decoration:none;">{contact_message.email}</a>
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- Subject -->
                            <p style="margin:0 0 10px;color:#6b7280;font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Sujet</p>
                            <h2 style="margin:0 0 25px;font-size:22px;font-weight:700;color:#18181b;line-height:1.3;">
                                {contact_message.subject}
                            </h2>

                            <!-- Message -->
                            <p style="margin:0 0 10px;color:#6b7280;font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Message</p>
                            <div style="background-color:#f9fafb;border-left:4px solid #f59e0b;padding:20px;border-radius:0 12px 12px 0;margin-bottom:30px;">
                                <p style="margin:0;color:#374151;font-size:16px;line-height:1.8;white-space:pre-wrap;">{contact_message.message}</p>
                            </div>

                            <!-- Reply Button -->
                            <a href="mailto:{contact_message.email}?subject=Re: {contact_message.subject}" style="display:inline-block;background-color:#f59e0b;color:#ffffff;padding:16px 32px;border-radius:12px;text-decoration:none;font-weight:700;font-size:14px;text-transform:uppercase;letter-spacing:1px;">
                                Répondre à {contact_message.name} →
                            </a>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color:#fafafa;padding:25px;text-align:center;border-top:1px solid #e5e5e5;">
                            <p style="margin:0 0 5px;color:#71717a;font-size:12px;">
                                Message reçu le {contact_message.created_at.strftime('%d/%m/%Y à %H:%M')}
                            </p>
                            <p style="margin:0;color:#a1a1aa;font-size:11px;">
                                © 2025 Geniesdafriquemedia - Formulaire de contact
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''

    try:
        service = get_newsletter_service()

        # Vérifier que le service supporte les emails transactionnels
        if not hasattr(service, 'send_transactional_email'):
            logger.warning('Newsletter service does not support transactional emails')
            return {'success': False, 'error': 'Service non supporté'}

        result = service.send_transactional_email(
            to_email=admin_email,
            to_name=admin_name,
            subject=f'📩 Contact: {contact_message.subject}',
            html_content=html_content,
            reply_to_email=contact_message.email,
            reply_to_name=contact_message.name
        )

        logger.info(f'Contact notification sent for message from: {contact_message.email}')
        return result

    except NewsletterServiceError as e:
        logger.error(f'Failed to send contact notification: {e}')
        return {'success': False, 'error': str(e)}
