"""API URLs pour l'app energy."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AlerteViewSet,
    AnomalieViewSet,
    AdminFoyersListView,
    AdminResidentsListView,
    AdminResidentDetailView,
    AssignFoyerView,
    ConsommationViewSet,
    ConversationIAViewSet,
    FoyerViewSet,
    ImportCSVView,
    ResidentDashboardView,
    ResidentHistoriqueView,
    ResidentAlertesView,
)
from .views_smartmeter import (
    AdminResidentsListView as AdminResidentsListViewNew,
    AdminDashboardView,
    AdminFoyersListView as AdminFoyersListViewNew,
    AdminAnalyticsConsumptionView,
    AdminAnalyticsTopConsumersView,
    AdminAnalyticsStatsView,
    ResidentDashboardView as ResidentDashboardViewNew,
    ResidentReadingsView,
)

router = DefaultRouter()
router.register(r'foyers', FoyerViewSet, basename='foyer')
router.register(r'consommations', ConsommationViewSet, basename='consommation')
router.register(r'anomalies', AnomalieViewSet, basename='anomalie')
router.register(r'alertes', AlerteViewSet, basename='alerte')
router.register(r'chat', ConversationIAViewSet, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
    
    # Import CSV
    path('import-csv/', ImportCSVView.as_view(), name='import-csv'),
    
    # Admin endpoints (old)
    path('admin/foyers-old/', AdminFoyersListView.as_view(), name='admin-foyers-old'),
    path('admin/residents-old/', AdminResidentsListView.as_view(), name='admin-residents-old'),
    path('admin/residents-old/<int:resident_id>/', AdminResidentDetailView.as_view(), name='admin-resident-detail'),
    path('admin/residents-old/<int:resident_id>/assign-foyer/', AssignFoyerView.as_view(), name='admin-assign-foyer'),
    
    # Admin endpoints (new - Cahier des Charges)
    path('admin/residents/', AdminResidentsListViewNew.as_view(), name='admin-residents'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/foyers/', AdminFoyersListViewNew.as_view(), name='admin-foyers'),
    
    # Admin analytics endpoints
    path('admin/analytics/consumption/', AdminAnalyticsConsumptionView.as_view(), name='admin-analytics-consumption'),
    path('admin/analytics/top-consumers/', AdminAnalyticsTopConsumersView.as_view(), name='admin-analytics-top-consumers'),
    path('admin/analytics/stats/', AdminAnalyticsStatsView.as_view(), name='admin-analytics-stats'),
    
    # Resident endpoints
    path('resident/dashboard/', ResidentDashboardViewNew.as_view(), name='resident-dashboard'),
    path('resident/readings/', ResidentReadingsView.as_view(), name='resident-readings'),
    path('resident/historique/', ResidentHistoriqueView.as_view(), name='resident-historique'),
    path('resident/alertes/', ResidentAlertesView.as_view(), name='resident-alertes'),
]
