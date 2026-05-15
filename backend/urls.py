"""
Configuration des URLs pour SmartMeter.

Routes principales:
- /api/token/ : Obtenir un token JWT (login)
- /api/token/refresh/ : Rafraîchir le token
- /api/energy/ : API energy
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from energy.views_smartmeter import AdminResidentsListView, AdminDashboardView

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # Auth API - Handle login, signup, and profile
    path('api/auth/', include('users.urls')),
    
    # Admin API - Smart Meter endpoints
    path('api/admin/residents/', AdminResidentsListView.as_view(), name='api-admin-residents'),
    path('api/admin/dashboard/', AdminDashboardView.as_view(), name='api-admin-dashboard'),
    
    # Energy App - All your meter logic
    path('api/energy/', include('energy.urls')),
]