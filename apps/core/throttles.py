"""
Throttles personnalisés pour l'API GAM.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class ReadSafeAnonRateThrottle(AnonRateThrottle):
    """
    Ne throttle que les requêtes d'écriture pour les anonymes.
    Les GET/HEAD/OPTIONS ne sont jamais bloqués : le serveur Next.js SSR
    partage une seule IP Railway et dépasserait 100/h très rapidement.
    """
    rate = '2000/hour'

    def allow_request(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return super().allow_request(request, view)
