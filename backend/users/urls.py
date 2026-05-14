from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    UserProfileView,
    AdminUsersViewSet,
)
from rest_framework_simplejwt.views import TokenRefreshView
from energy.views_smartmeter import current_user

router = DefaultRouter()
router.register(r'admin/users', AdminUsersViewSet, basename='admin-users')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('me/', current_user, name='current_user'),
    path('', include(router.urls)),
]
