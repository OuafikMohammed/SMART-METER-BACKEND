from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import (
    RegisterSerializer, 
    UserSerializer, 
    CustomTokenObtainPairSerializer
)

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vue pour obtenir un token JWT avec des infos utilisateur personnalisées.
    Utilisée pour le Login (Résident et Admin).
    """
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    """
    Vue pour l'inscription des nouveaux résidents.
    Accessibilité: Publique.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserSerializer(user).data,
                "message": "Utilisateur créé avec succès. Vous pouvez maintenant vous connecter.",
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Vue pour récupérer ou mettre à jour le profil de l'utilisateur connecté.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class AdminUsersViewSet(viewsets.ViewSet):
    """
    ViewSet pour l'administration des utilisateurs.
    Accessible uniquement aux ADMIN (RG3).
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        GET /api/admin/users/
        Lister tous les utilisateurs (admin seulement).
        """
        # Vérifier que l'utilisateur est ADMIN
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Accès refusé. Vous devez être administrateur.'},
                status=status.HTTP_403_FORBIDDEN
            )

        users = User.objects.select_related('foyer').all().order_by('username')
        
        # Construire les données de réponse
        data = []
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'foyer': None,
            }
            
            if user.foyer:
                user_data['foyer'] = {
                    'id': user.foyer.id,
                    'numero_foyer': user.foyer.numero_foyer,
                }
            
            data.append(user_data)
        
        return Response(data)

    def retrieve(self, request, pk=None):
        """
        GET /api/admin/users/{id}/
        Récupérer les détails d'un utilisateur.
        """
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Accès refusé'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': 'Utilisateur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
