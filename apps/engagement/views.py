"""
Engagement Views - Vues pour l'engagement utilisateur
"""

from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.throttling import ScopedRateThrottle
from drf_spectacular.utils import extend_schema

from .models import NewsletterSubscription, ContactMessage
from .serializers import (
    NewsletterSubscribeSerializer,
    NewsletterUnsubscribeSerializer,
    NewsletterSubscriptionSerializer,
    ContactMessageCreateSerializer,
    ContactMessageSerializer,
)
from .services import subscribe_to_newsletter, send_contact_notification


# =============================================================================
# NEWSLETTER VIEWS
# =============================================================================

@extend_schema(tags=['Newsletter'])
class NewsletterSubscribeView(generics.GenericAPIView):
    """
    Inscription à la newsletter (US-10).
    Validation email + envoi vers Brevo/Mailchimp.
    """
    authentication_classes = []  # Pas d'authentification requise (public)
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'newsletter'
    serializer_class = NewsletterSubscribeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        ip_address = self._get_client_ip(request)

        try:
            result = subscribe_to_newsletter(
                email=data['email'],
                ip_address=ip_address,
                source=data.get('source', 'website'),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
            )

            if result.get('already_subscribed'):
                return Response(
                    {'message': 'Vous êtes déjà inscrit à notre newsletter.'},
                    status=status.HTTP_200_OK
                )

            return Response(
                {'message': 'Inscription réussie ! Merci de votre intérêt.'},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Newsletter subscription error: {e}', exc_info=True)
            return Response(
                {'error': 'Une erreur est survenue. Veuillez réessayer.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_client_ip(self, request):
        """Récupère l'adresse IP du client."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


@extend_schema(tags=['Newsletter'])
class NewsletterUnsubscribeView(generics.GenericAPIView):
    """
    Désabonnement de la newsletter.
    """
    authentication_classes = []  # Pas d'authentification requise (public)
    permission_classes = [AllowAny]
    serializer_class = NewsletterUnsubscribeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            subscription = NewsletterSubscription.objects.get(email=email)
            subscription.unsubscribe()

            return Response(
                {'message': 'Vous avez été désabonné avec succès.'},
                status=status.HTTP_200_OK
            )
        except NewsletterSubscription.DoesNotExist:
            return Response(
                {'error': 'Email non trouvé.'},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(tags=['Admin - Newsletter'])
class AdminNewsletterViewSet(viewsets.ModelViewSet):
    """
    Administration des inscriptions newsletter.
    """
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['status', 'source']
    search_fields = ['email']
    ordering_fields = ['created_at', 'confirmed_at']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des inscriptions."""
        total = self.get_queryset().count()
        confirmed = self.get_queryset().filter(
            status=NewsletterSubscription.Status.CONFIRMED
        ).count()
        unsubscribed = self.get_queryset().filter(
            status=NewsletterSubscription.Status.UNSUBSCRIBED
        ).count()

        return Response({
            'total': total,
            'confirmed': confirmed,
            'unsubscribed': unsubscribed,
            'active_rate': round(confirmed / total * 100, 2) if total > 0 else 0,
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export des emails confirmés."""
        emails = list(
            self.get_queryset()
            .filter(status=NewsletterSubscription.Status.CONFIRMED)
            .values_list('email', flat=True)
        )
        return Response({'emails': emails, 'count': len(emails)})


# =============================================================================
# CONTACT VIEWS
# =============================================================================

@extend_schema(tags=['Contact'])
class ContactMessageCreateView(generics.CreateAPIView):
    """
    Envoi d'un message de contact.
    """
    authentication_classes = []  # Pas d'authentification requise (public)
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'contact'
    serializer_class = ContactMessageCreateSerializer

    def perform_create(self, serializer):
        ip_address = self._get_client_ip(self.request)
        serializer.save(ip_address=ip_address)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Envoyer la notification email à l'admin
        contact_message = serializer.instance
        try:
            result = send_contact_notification(contact_message)
            if result.get('success'):
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f'Contact notification sent for message from: {contact_message.email}')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error sending contact notification: {e}')
            # Ne pas bloquer l'envoi du message en cas d'erreur email

        return Response(
            {'message': 'Votre message a été envoyé avec succès.'},
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['Admin - Contact'])
class AdminContactMessageViewSet(viewsets.ModelViewSet):
    """
    Administration des messages de contact.
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['status']
    search_fields = ['name', 'email', 'subject', 'message']
    ordering_fields = ['created_at', 'status']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.mark_as_read()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_replied(self, request, pk=None):
        """Marque un message comme répondu."""
        message = self.get_object()
        message.mark_as_replied(request.user)
        return Response({'message': 'Message marqué comme répondu.'})

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive un message."""
        message = self.get_object()
        message.status = ContactMessage.Status.ARCHIVED
        message.save()
        return Response({'message': 'Message archivé.'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des messages."""
        total = self.get_queryset().count()
        new = self.get_queryset().filter(status=ContactMessage.Status.NEW).count()
        replied = self.get_queryset().filter(status=ContactMessage.Status.REPLIED).count()

        return Response({
            'total': total,
            'new': new,
            'read': self.get_queryset().filter(status=ContactMessage.Status.READ).count(),
            'replied': replied,
            'archived': self.get_queryset().filter(status=ContactMessage.Status.ARCHIVED).count(),
            'response_rate': round(replied / total * 100, 2) if total > 0 else 0,
        })
