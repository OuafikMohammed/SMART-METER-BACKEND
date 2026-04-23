"""API URLs pour l'app energy."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AlerteViewSet, AnomalieViewSet, ConsommationViewSet, ConversationIAViewSet, FoyerViewSet

router = DefaultRouter()
router.register(r'foyers', FoyerViewSet, basename='foyer')
router.register(r'consommations', ConsommationViewSet, basename='consommation')
router.register(r'anomalies', AnomalieViewSet, basename='anomalie')
router.register(r'alertes', AlerteViewSet, basename='alerte')
router.register(r'conversations-ia', ConversationIAViewSet, basename='conversationIA')

urlpatterns = [
    path('', include(router.urls)),
]
