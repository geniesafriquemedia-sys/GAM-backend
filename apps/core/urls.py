"""
Core URLs
"""

from django.urls import path
from .views import SocialNetworkListView

app_name = 'core'

urlpatterns = [
    path('social-networks/', SocialNetworkListView.as_view(), name='social-networks'),
]
