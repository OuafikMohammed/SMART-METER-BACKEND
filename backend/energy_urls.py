"""
API URLs pour l'app energy
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from energy.views import (
    FoyerViewSet, ConsommationViewSet, AnomalieViewSet, 
    AlerteViewSet, ConversationIAViewSet
)

router = DefaultRouter()
router.register(r'foyers', FoyerViewSet, basename='foyer')
router.register(r'consommations', ConsommationViewSet, basename='consommation')
router.register(r'anomalies', AnomalieViewSet, basename='anomalie')
router.register(r'alertes', AlerteViewSet, basename='alerte')
router.register(r'conversations-ia', ConversationIAViewSet, basename='conversationIA')

urlpatterns = [
    path('', include(router.urls)),
]
