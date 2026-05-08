"""REST API views pour l'app energy."""
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Alerte, Anomalie, Consommation, ConversationIA, Foyer
from .serializers import (
    AlerteSerializer,
    AnomalieSerializer,
    ConsommationSerializer,
    ConversationIASerializer,
    FoyerSerializer,
)
from .utils_logging import get_client_ip, log_action
from .services.ai_service import generer_reponse_ia


class FoyerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FoyerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'ville']
    search_fields = ['numero_foyer', 'adresse', 'ville']
    ordering_fields = ['numero_foyer', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Foyer.objects.all()
        if self.request.user.role == 'RESIDENT' and self.request.user.foyer:
            return Foyer.objects.filter(id=self.request.user.foyer.id)
        return Foyer.objects.none()


class ConsommationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConsommationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['foyer', 'anomaly_label']
    ordering_fields = ['timestamp', 'kwh']
    ordering = ['-timestamp']

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Consommation.objects.select_related('foyer').all()
        if self.request.user.role == 'RESIDENT' and self.request.user.foyer:
            return Consommation.objects.filter(foyer=self.request.user.foyer)
        return Consommation.objects.none()


class AnomalieViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les anomalies (RG7, RG8, RG9)."""
    serializer_class = AnomalieSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['severite', 'statut', 'consommation__foyer']
    ordering_fields = ['score_confiance', 'created_at', 'severite']
    ordering = ['-created_at']

    def get_queryset(self):
        """RG3: Accès basé sur le rôle."""
        if self.request.user.role == 'ADMIN':
            return Anomalie.objects.select_related('consommation__foyer').all()
        if self.request.user.role == 'RESIDENT' and self.request.user.foyer:
            return Anomalie.objects.filter(
                consommation__foyer=self.request.user.foyer
            ).select_related('consommation__foyer')
        return Anomalie.objects.none()
    
    def get_permissions(self):
        """Les RESIDENTS ne peuvent consulter, les ADMINS peuvent modifier."""
        if self.action in ['update', 'partial_update', 'marquer_consultee', 'marquer_acquittee']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'])
    def marquer_consultee(self, request, pk=None):
        """Marquer une anomalie comme consultée (RG9: NOUVELLE → CONSULTEE)."""
        try:
            anomalie = self.get_object()
        except Anomalie.DoesNotExist:
            return Response({'error': 'Anomalie non trouvée'}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier les permissions
        if request.user.role == 'RESIDENT' and anomalie.consommation.foyer != request.user.foyer:
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)
        
        anomalie.marquer_consultee()
        log_action(
            user=request.user,
            action='MARQUER_ANOMALIE_CONSULTEE',
            details={'anomalie_id': anomalie.id, 'foyer_id': anomalie.consommation.foyer.id},
            ip_address=get_client_ip(request),
        )
        
        serializer = self.get_serializer(anomalie)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def marquer_acquittee(self, request, pk=None):
        """Marquer une anomalie comme acquittée (RG9: → ACQUITTEE)."""
        try:
            anomalie = self.get_object()
        except Anomalie.DoesNotExist:
            return Response({'error': 'Anomalie non trouvée'}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier les permissions
        if request.user.role == 'RESIDENT' and anomalie.consommation.foyer != request.user.foyer:
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)
        
        anomalie.marquer_acquittee()
        log_action(
            user=request.user,
            action='MARQUER_ANOMALIE_ACQUITTEE',
            details={'anomalie_id': anomalie.id, 'foyer_id': anomalie.consommation.foyer.id},
            ip_address=get_client_ip(request),
        )
        
        serializer = self.get_serializer(anomalie)
        return Response(serializer.data)


class AlerteViewSet(viewsets.ViewSet):
    """ViewSet pour gérer les alertes (RG10, RG11, RG12)."""
    permission_classes = [IsAuthenticated]
    serializer_class = AlerteSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get_queryset(self):
        """RG10: Alertes visibles uniquement dans l'application."""
        if self.request.user.role == 'ADMIN':
            return Alerte.objects.select_related('anomalie__consommation__foyer').all()
        elif self.request.user.role == 'RESIDENT' and self.request.user.foyer:
            return Alerte.objects.filter(
                anomalie__consommation__foyer=self.request.user.foyer
            ).select_related('anomalie__consommation__foyer')
        return Alerte.objects.none()

    def list(self, request):
        """Lister les alertes avec filtres."""
        queryset = self.get_queryset()
        
        # Filtres pour l'admin
        statut = request.query_params.get('statut')
        acquittee = request.query_params.get('acquittee')
        foyer_id = request.query_params.get('foyer_id')
        
        if statut:
            queryset = queryset.filter(statut=statut)
        if acquittee is not None:
            queryset = queryset.filter(acquittee=acquittee.lower() == 'true')
        if foyer_id and request.user.role == 'ADMIN':
            queryset = queryset.filter(anomalie__consommation__foyer_id=foyer_id)
        
        # Tri par défaut
        queryset = queryset.order_by('-created_at')
        
        serializer = AlerteSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Récupérer une alerte spécifique."""
        try:
            alerte = self.get_queryset().get(pk=pk)
        except Alerte.DoesNotExist:
            return Response({'error': 'Alerte non trouvée'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AlerteSerializer(alerte)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def marquer_consultee(self, request, pk=None):
        """Marquer l'alerte comme consultée (RG11)."""
        try:
            alerte = self.get_queryset().get(pk=pk)
        except Alerte.DoesNotExist:
            return Response({'error': 'Alerte non trouvée'}, status=status.HTTP_404_NOT_FOUND)
        
        alerte.marquer_consultee()
        log_action(
            user=request.user,
            action='MARQUER_ALERTE_CONSULTEE',
            details={'alerte_id': alerte.id, 'anomalie_id': alerte.anomalie.id},
            ip_address=get_client_ip(request),
        )
        
        serializer = AlerteSerializer(alerte)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def acquitter(self, request, pk=None):
        """Acquitter l'alerte (RG11, RG12: archivage)."""
        try:
            alerte = self.get_queryset().get(pk=pk)
        except Alerte.DoesNotExist:
            return Response({'error': 'Alerte non trouvée'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'RESIDENT' and alerte.anomalie.consommation.foyer != request.user.foyer:
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)

        alerte.acquitter()
        # Mettre à jour l'anomalie associée
        alerte.anomalie.marquer_acquittee()
        
        log_action(
            user=request.user,
            action='ACQUITTER_ALERTE',
            details={
                'alerte_id': alerte.id,
                'anomalie_id': alerte.anomalie.id,
                'foyer_id': alerte.anomalie.consommation.foyer.id,
            },
            ip_address=get_client_ip(request),
        )

        serializer = AlerteSerializer(alerte)
        return Response(serializer.data)


class ConversationIAViewSet(viewsets.ViewSet):
    """ViewSet pour gérer les conversations IA (RG16, RG17, RG18)."""
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationIASerializer

    def list(self, request):
        """
        GET /api/chat/historique/
        Lister les 20 derniers messages du résident connecté (RG18).
        """
        conversations = ConversationIA.objects.filter(
            utilisateur=request.user
        ).order_by('-timestamp')[:20]
        
        serializer = ConversationIASerializer(conversations, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        POST /api/chat/
        Poser une question à l'IA et sauvegarder la réponse (RG16, RG17, RG18).
        
        - Valide la question
        - Récupère le foyer du résident
        - Appelle generer_reponse_ia() avec contexte MySQL
        - Sauvegarde dans ConversationIA
        - Log l'action (RG20)
        """
        question = request.data.get('question', '').strip()
        
        if not question:
            return Response(
                {'error': 'La question est requise'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que le résident a un foyer
        if not request.user.foyer:
            return Response(
                {'error': 'Votre compte n\'est pas lié à un foyer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Générer la réponse IA avec contexte MySQL (RG16, RG17)
            reponse = generer_reponse_ia(
                foyer_id=request.user.foyer.id,
                question=question
            )
            
            # Sauvegarder la conversation (RG18)
            conversation = ConversationIA.objects.create(
                utilisateur=request.user,
                question=question,
                reponse=reponse,
            )
            
            # Log de l'action (RG20)
            log_action(
                user=request.user,
                action='CHAT_IA',
                details={
                    'conversation_id': conversation.id,
                    'question': question[:100],
                    'foyer_id': request.user.foyer.id,
                },
                ip_address=get_client_ip(request),
            )
            
            serializer = ConversationIASerializer(conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            log_action(
                user=request.user,
                action='CHAT_IA_ERROR',
                details={'error': str(e), 'question': question[:100]},
                ip_address=get_client_ip(request),
            )
            return Response(
                {'error': 'Erreur lors de la génération de la réponse'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
