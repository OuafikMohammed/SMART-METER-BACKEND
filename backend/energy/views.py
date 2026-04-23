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


class AnomalieViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AnomalieSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['severite', 'statut']
    ordering_fields = ['score_confiance', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Anomalie.objects.select_related('consommation').all()
        if self.request.user.role == 'RESIDENT' and self.request.user.foyer:
            return Anomalie.objects.filter(consommation__foyer=self.request.user.foyer).select_related('consommation')
        return Anomalie.objects.none()


class AlerteViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AlerteSerializer

    def list(self, request):
        if request.user.role == 'ADMIN':
            alertes = Alerte.objects.select_related('anomalie').all()
        elif request.user.role == 'RESIDENT' and request.user.foyer:
            alertes = Alerte.objects.filter(anomalie__consommation__foyer=request.user.foyer).select_related('anomalie')
        else:
            alertes = Alerte.objects.none()
        serializer = AlerteSerializer(alertes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def acquitter(self, request, pk=None):
        try:
            alerte = Alerte.objects.get(pk=pk)
        except Alerte.DoesNotExist:
            return Response({'error': 'Alerte non trouvee'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'RESIDENT' and alerte.anomalie.consommation.foyer != request.user.foyer:
            return Response({'error': 'Acces refuse'}, status=status.HTTP_403_FORBIDDEN)

        alerte.acquittee = True
        alerte.acquittee_at = timezone.now()
        alerte.save()

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
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationIASerializer

    def list(self, request):
        conversations = ConversationIA.objects.filter(utilisateur=request.user).order_by('-timestamp')
        serializer = ConversationIASerializer(conversations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def ask(self, request):
        question = request.data.get('question', '')
        if not question:
            return Response({'error': 'La question est requise'}, status=status.HTTP_400_BAD_REQUEST)

        conversation = ConversationIA.objects.create(
            utilisateur=request.user,
            question=question,
            reponse="Reponse simulee a votre question.",
        )

        log_action(
            user=request.user,
            action='POSER_QUESTION_IA',
            details={'conversation_id': conversation.id},
            ip_address=get_client_ip(request),
        )

        serializer = ConversationIASerializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
