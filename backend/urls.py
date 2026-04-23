"""
Configuration des URLs pour SmartMeter.

Routes principales:
- /api/token/ : Obtenir un token JWT (login)
- /api/token/refresh/ : Rafraîchir le token
- /api/ : API energy
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # Auth API - Handle login, signup, and profile
    path('api/auth/', include('users.urls')),
    
    # Energy App - All your meter logic
    path('api/', include('energy.urls')), 
]