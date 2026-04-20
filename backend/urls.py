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
    # Admin Django
    path('admin/', admin.site.urls),
    
    # JWT Authentication (RG1)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Energy (RG3: contrôle d'accès par rôle)
    path('api/', include('energy.urls')),
]
