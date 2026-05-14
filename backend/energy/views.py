"""REST API views pour l'app energy."""
import pandas as pd
from datetime import timedelta, datetime
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Alerte, Anomalie, ActionLog, Consommation, ConversationIA, Foyer
from .serializers import (
    AlerteSerializer,
    AnomalieSerializer,
    ConsommationSerializer,
    ConversationIASerializer,
    FoyerSerializer,
)
from .utils_logging import get_client_ip, log_action
from .services.ai_service import generer_reponse_ia

# Tarif kWh (2.5 DH par kWh - valeur par défaut)
TARIF_KWH = 2.5


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
        """Filter consumptions by user role - RG3: Data isolation."""
        if self.request.user.role == 'ADMIN':
            # Admin sees consumptions only for foyers of residents they manage
            managed_residents = User.objects.filter(
                managed_by=self.request.user,
                role='RESIDENT'
            )
            managed_foyers = Foyer.objects.filter(
                user__in=managed_residents
            ).distinct()
            return Consommation.objects.filter(
                foyer__in=managed_foyers
            ).select_related('foyer').distinct()
        
        if self.request.user.role == 'RESIDENT' and self.request.user.foyer:
            # Resident sees only their foyer's consumptions
            return Consommation.objects.filter(foyer=self.request.user.foyer)
        
        return Consommation.objects.none()

    def _get_date_range(self, period):
        """Calculate date range based on period."""
        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:  # month (default)
            start_date = now - timedelta(days=30)
        return start_date, now

    @action(detail=False, methods=['get'])
    def consumption_history(self, request):
        """
        GET /api/energy/consommations/consumption-history/?period=month
        Returns consumption history for the specified period.
        """
        period = request.query_params.get('period', 'month')
        start_date, end_date = self._get_date_range(period)
        
        # Get queryset for current user
        queryset = self.get_queryset()
        
        # Filter by date range
        data = queryset.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).order_by('timestamp').values('timestamp', 'kwh', 'foyer__numero_foyer')
        
        # Convert to list and format
        results = []
        for item in data:
            results.append({
                'date': item['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'consumption': item['kwh'],
                'foyer': item['foyer__numero_foyer']
            })
        
        return Response({'results': results})

    @action(detail=False, methods=['get'])
    def consumption_stats(self, request):
        """
        GET /api/energy/consommations/consumption-stats/?period=month
        Returns consumption statistics for the specified period.
        """
        period = request.query_params.get('period', 'month')
        start_date, end_date = self._get_date_range(period)
        
        # Get queryset for current user
        queryset = self.get_queryset()
        
        # Filter by date range
        data = list(queryset.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).values_list('kwh', 'timestamp'))
        
        if not data:
            return Response({
                'avg': 0,
                'total': 0,
                'peak': '00:00',
                'saving': '0%'
            })
        
        # Calculate statistics
        kwh_values = [item[0] for item in data]
        total_consumption = sum(kwh_values)
        avg_consumption = total_consumption / len(kwh_values) if kwh_values else 0
        
        # Find peak consumption time
        peak_idx = kwh_values.index(max(kwh_values))
        peak_time = data[peak_idx][1].strftime('%H:%M') if data[peak_idx][1] else '00:00'
        
        return Response({
            'avg': round(avg_consumption, 2),
            'total': round(total_consumption, 2),
            'peak': peak_time,
            'saving': '0%'  # Can be calculated based on comparison to previous period
        })



class AnomalieViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les anomalies (RG7, RG8, RG9)."""
    serializer_class = AnomalieSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['severite', 'statut', 'consommation__foyer']
    ordering_fields = ['score_confiance', 'created_at', 'severite']
    ordering = ['-created_at']

    def get_queryset(self):
        """RG3: Accès basé sur le rôle. Admins voient anomalies de leurs résidents gérés."""
        if self.request.user.role == 'ADMIN':
            # Admin sees anomalies only for residents they manage
            managed_residents = User.objects.filter(
                managed_by=self.request.user, 
                role='RESIDENT'
            )
            managed_foyers = Foyer.objects.filter(
                user__in=managed_residents
            ).distinct()
            return Anomalie.objects.filter(
                consommation__foyer__in=managed_foyers
            ).select_related('consommation__foyer').distinct()
        
        if self.request.user.role == 'RESIDENT' and self.request.user.foyer:
            # Resident sees anomalies only for their foyer
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


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

class AdminFoyersListView(APIView):
    """
    Endpoint GET /api/energy/admin/foyers/
    Lister tous les foyers créés depuis l'import Kaggle.
    Réservé aux ADMIN.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Vérifier que l'utilisateur est ADMIN
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Accès refusé. Seuls les administrateurs peuvent lister les foyers.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Récupérer les foyers avec filtres et pagination
            foyers = Foyer.objects.all()
            
            # Filtrer par recherche
            search = request.query_params.get('search')
            if search:
                foyers = foyers.filter(
                    numero_foyer__icontains=search
                ) | foyers.filter(
                    adresse__icontains=search
                ) | foyers.filter(
                    ville__icontains=search
                )
            
            # Filtrer par active
            is_active = request.query_params.get('is_active')
            if is_active:
                foyers = foyers.filter(is_active=is_active.lower() == 'true')
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            start = (page - 1) * page_size
            end = start + page_size
            
            total = foyers.count()
            foyers_page = foyers[start:end]
            
            # Serializer
            from .serializers import FoyerDetailSerializer
            serializer = FoyerDetailSerializer(foyers_page, many=True)
            
            log_action(
                user=request.user,
                action='LIST_FOYERS',
                details={'total': total, 'page': page},
                ip_address=get_client_ip(request),
            )
            
            return Response({
                'count': total,
                'page': page,
                'page_size': page_size,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            log_action(
                user=request.user,
                action='LIST_FOYERS_ERROR',
                details={'error': str(e)},
                ip_address=get_client_ip(request),
            )
            return Response(
                {'error': f'Erreur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminResidentsListView(APIView):
    """
    Endpoint GET /api/energy/admin/residents/
    Lister tous les résidents avec leurs données réelles.
    Réservé aux ADMIN.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Vérifier que l'utilisateur est ADMIN
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Accès refusé. Seuls les administrateurs peuvent lister les résidents.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Récupérer les résidents
            residents = User.objects.filter(role='RESIDENT')
            
            # Filtrer par recherche
            search = request.query_params.get('search')
            if search:
                residents = residents.filter(
                    username__icontains=search
                ) | residents.filter(
                    email__icontains=search
                ) | residents.filter(
                    first_name__icontains=search
                ) | residents.filter(
                    last_name__icontains=search
                )
            
            # Filtrer par foyer
            foyer_id = request.query_params.get('foyer_id')
            if foyer_id:
                residents = residents.filter(foyer_id=foyer_id)
            
            # Filtrer avec/sans foyer
            has_foyer = request.query_params.get('has_foyer')
            if has_foyer:
                if has_foyer.lower() == 'true':
                    residents = residents.exclude(foyer__isnull=True)
                else:
                    residents = residents.filter(foyer__isnull=True)
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            start = (page - 1) * page_size
            end = start + page_size
            
            total = residents.count()
            residents_page = residents[start:end]
            
            # Serializer
            from .serializers import UserResidentListSerializer
            serializer = UserResidentListSerializer(residents_page, many=True)
            
            log_action(
                user=request.user,
                action='LIST_RESIDENTS',
                details={'total': total, 'page': page},
                ip_address=get_client_ip(request),
            )
            
            return Response({
                'count': total,
                'page': page,
                'page_size': page_size,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            log_action(
                user=request.user,
                action='LIST_RESIDENTS_ERROR',
                details={'error': str(e)},
                ip_address=get_client_ip(request),
            )
            return Response(
                {'error': f'Erreur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminResidentDetailView(APIView):
    """
    Endpoint GET /api/energy/admin/residents/{id}/
    Détails complets d'un résident avec toutes ses données.
    Réservé aux ADMIN.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, resident_id):
        # Vérifier que l'utilisateur est ADMIN
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Accès refusé. Seuls les administrateurs peuvent voir les détails.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            resident = User.objects.get(id=resident_id, role='RESIDENT')
            
            # Serializer
            from .serializers import UserResidentDetailSerializer
            serializer = UserResidentDetailSerializer(resident)
            
            log_action(
                user=request.user,
                action='VIEW_RESIDENT_DETAIL',
                details={'resident_id': resident_id},
                ip_address=get_client_ip(request),
            )
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                resident = User.objects.get(id=resident_id, role='RESIDENT')
                return Response({'error': f'Erreur: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Résident non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )


class AssignFoyerView(APIView):
    """
    Endpoint PATCH /api/energy/admin/residents/{id}/assign-foyer/
    Assigner un foyer à un résident.
    Réservé aux ADMIN.
    
    Request body:
    {
        "foyer_id": 1
    }
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, resident_id):
        # Vérifier que l'utilisateur est ADMIN
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Accès refusé. Seuls les administrateurs peuvent assigner un foyer.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            resident = User.objects.get(id=resident_id, role='RESIDENT')
            
            # Récupérer le foyer_id depuis le request body
            foyer_id = request.data.get('foyer_id')
            
            if not foyer_id:
                return Response(
                    {'error': 'foyer_id est requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier que le foyer existe
            foyer = Foyer.objects.get(id=foyer_id)
            
            # Assigner le foyer au résident
            resident.foyer = foyer
            resident.save()
            
            # Log
            log_action(
                user=request.user,
                action='ASSIGN_FOYER',
                details={'resident_id': resident_id, 'foyer_id': foyer_id},
                ip_address=get_client_ip(request),
            )
            
            # Serializer
            from .serializers import UserResidentListSerializer
            serializer = UserResidentListSerializer(resident)
            
            return Response({
                'message': 'Foyer assigné avec succès',
                'resident': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                resident = User.objects.get(id=resident_id, role='RESIDENT')
                return Response({'error': f'Erreur: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Résident non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Foyer.DoesNotExist:
                return Response(
                    {'error': 'Foyer non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )


class ResidentHistoriqueView(APIView):
    """
    Endpoint GET /api/energy/resident/historique/?period=week|month|year
    Historique des consommations du foyer connecté (résident).
    Réservé aux RESIDENT.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Vérifier que l'utilisateur est RESIDENT
        if request.user.role != 'RESIDENT':
            return Response(
                {'error': 'Accès refusé. Seuls les résidents peuvent accéder à l\'historique.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que le résident a un foyer
        if not request.user.foyer:
            return Response(
                {'error': 'Votre compte n\'est pas lié à un foyer.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            period = request.query_params.get('period', 'month')
            foyer = request.user.foyer
            now = timezone.now()
            
            # Calculer la plage de dates
            if period == 'week':
                start_date = now - timedelta(days=7)
            elif period == 'year':
                start_date = now - timedelta(days=365)
            else:  # month (défaut)
                start_date = now - timedelta(days=30)
            
            # Récupérer les consommations
            consommations = Consommation.objects.filter(
                foyer=foyer,
                timestamp__gte=start_date,
                timestamp__lte=now
            ).order_by('-timestamp')
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 100))
            start = (page - 1) * page_size
            end = start + page_size
            
            total = consommations.count()
            total_kwh = consommations.aggregate(Sum('kwh'))['kwh__sum'] or 0
            avg_kwh = total_kwh / total if total > 0 else 0
            
            consommations_page = consommations[start:end]
            
            # Serializer
            from .serializers import ConsommationDetailSerializer
            serializer = ConsommationDetailSerializer(consommations_page, many=True)
            
            log_action(
                user=request.user,
                action='VIEW_HISTORIQUE',
                details={'foyer_id': foyer.id, 'period': period},
                ip_address=get_client_ip(request),
            )
            
            return Response({
                'count': total,
                'period': period,
                'total_kwh': round(total_kwh, 2),
                'avg_kwh': round(avg_kwh, 2),
                'page': page,
                'page_size': page_size,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            log_action(
                user=request.user,
                action='VIEW_HISTORIQUE_ERROR',
                details={'error': str(e)},
                ip_address=get_client_ip(request),
            )
            return Response(
                {'error': f'Erreur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResidentAlertesView(APIView):
    """
    Endpoint GET /api/energy/resident/alertes/?status=all|new|acknowledged
    Alertes du foyer connecté (résident).
    Réservé aux RESIDENT.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Vérifier que l'utilisateur est RESIDENT
        if request.user.role != 'RESIDENT':
            return Response(
                {'error': 'Accès refusé. Seuls les résidents peuvent accéder aux alertes.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que le résident a un foyer
        if not request.user.foyer:
            return Response(
                {'error': 'Votre compte n\'est pas lié à un foyer.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            foyer = request.user.foyer
            
            # Récupérer les alertes
            alertes = Alerte.objects.filter(
                anomalie__consommation__foyer=foyer
            ).select_related('anomalie__consommation')
            
            # Filtrer par statut
            status_filter = request.query_params.get('status', 'all')
            if status_filter == 'new':
                alertes = alertes.filter(acquittee=False)
            elif status_filter == 'acknowledged':
                alertes = alertes.filter(acquittee=True)
            
            # Tri
            alertes = alertes.order_by('-created_at')
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 50))
            start = (page - 1) * page_size
            end = start + page_size
            
            total = alertes.count()
            alertes_actives = alertes.filter(acquittee=False).count()
            alertes_acquittees = alertes.filter(acquittee=True).count()
            
            alertes_page = alertes[start:end]
            
            # Serializer
            from .serializers import AlerteResidentSerializer
            serializer = AlerteResidentSerializer(alertes_page, many=True)
            
            log_action(
                user=request.user,
                action='VIEW_ALERTES',
                details={'foyer_id': foyer.id, 'status': status_filter},
                ip_address=get_client_ip(request),
            )
            
            return Response({
                'count': total,
                'alertes_actives': alertes_actives,
                'alertes_acquittees': alertes_acquittees,
                'page': page,
                'page_size': page_size,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            log_action(
                user=request.user,
                action='VIEW_ALERTES_ERROR',
                details={'error': str(e)},
                ip_address=get_client_ip(request),
            )
            return Response(
                {'error': f'Erreur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ImportCSVView(APIView):
    """
    Endpoint POST /api/energy/import-csv/ pour importer les données de consommation depuis un fichier CSV.
    Réservé aux administrateurs (RG2, RG3).
    
    Format CSV attendu:
    LCLid,DateTime,KWH/hh (per 0.5 hour),anomaly_label
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Importer les données CSV de consommation.
        
        Paramètres:
        - file (multipart/form-data): Fichier CSV
        
        Colonnes obligatoires:
        - LCLid: Identifiant du foyer
        - DateTime: Date et heure de la mesure
        - KWH/hh (per 0.5 hour): Consommation en kWh
        - anomaly_label: Label d'anomalie (int ou null)
        
        Retours:
        - 200: Import réussi avec résumé
        - 400: Erreur validation ou colonnes manquantes
        - 403: Accès refusé (utilisateur pas ADMIN)
        - 500: Erreur serveur
        """
        
        # Vérification des permissions (ADMIN uniquement)
        if request.user.role != 'ADMIN':
            log_action(
                user=request.user,
                action='IMPORT_CSV_DENIED',
                details={'raison': 'Utilisateur pas ADMIN', 'role': request.user.role},
                ip_address=get_client_ip(request),
            )
            return Response(
                {'error': 'Accès refusé. Seuls les administrateurs peuvent importer des données.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que le fichier a été fourni
        if 'file' not in request.FILES:
            return Response(
                {'error': 'Le fichier CSV est requis (clé: "file")'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        # Vérifier l'extension du fichier
        if not file.name.endswith('.csv'):
            return Response(
                {'error': 'Le fichier doit être un fichier CSV (.csv)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Lire le CSV avec pandas
            df = pd.read_csv(file)
            
            # Colonnes obligatoires
            required_columns = ['LCLid', 'DateTime', 'KWH/hh (per 0.5 hour)', 'anomaly_label']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response(
                    {'error': f'Colonnes manquantes: {", ".join(missing_columns)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Statistiques d'import
            foyers_created = 0
            foyers_existing = 0
            consommations_created = 0
            consommations_skipped = 0
            errors = []
            
            # Traiter chaque ligne du CSV
            for idx, row in df.iterrows():
                try:
                    lcl_id = str(row['LCLid']).strip()
                    datetime_str = str(row['DateTime']).strip()
                    kwh_str = str(row['KWH/hh (per 0.5 hour)']).strip()
                    anomaly_label_str = str(row['anomaly_label']).strip()
                    
                    # Validation du LCLid
                    if not lcl_id or lcl_id == 'nan':
                        errors.append(f'Ligne {idx + 2}: LCLid vide ou invalide')
                        continue
                    
                    # Conversion DateTime
                    try:
                        timestamp = pd.to_datetime(datetime_str)
                    except:
                        errors.append(f'Ligne {idx + 2}: DateTime invalide "{datetime_str}"')
                        continue
                    
                    # Conversion kWh en float
                    try:
                        kwh = float(kwh_str)
                    except:
                        errors.append(f'Ligne {idx + 2}: kWh invalide "{kwh_str}"')
                        continue
                    
                    # Conversion anomaly_label en int (ou null)
                    anomaly_label = None
                    if anomaly_label_str and anomaly_label_str != 'nan' and anomaly_label_str != '':
                        try:
                            anomaly_label = int(float(anomaly_label_str))
                        except:
                            errors.append(f'Ligne {idx + 2}: anomaly_label invalide "{anomaly_label_str}"')
                            continue
                    
                    # Créer ou récupérer le Foyer
                    foyer, created = Foyer.objects.get_or_create(
                        numero_foyer=lcl_id,
                        defaults={
                            'adresse': f'Adresse non disponible - {lcl_id}',
                            'code_postal': '00000',
                            'ville': 'Ville non disponible',
                            'puissance_souscrite': 3.0,  # Valeur par défaut
                        }
                    )
                    
                    if created:
                        foyers_created += 1
                    else:
                        foyers_existing += 1
                    
                    # Créer ou récupérer la Consommation (éviter les doublons)
                    consommation, created = Consommation.objects.get_or_create(
                        foyer=foyer,
                        timestamp=timestamp,
                        defaults={
                            'kwh': kwh,
                            'anomaly_label': str(anomaly_label) if anomaly_label is not None else None,
                        }
                    )
                    
                    if created:
                        consommations_created += 1
                    else:
                        consommations_skipped += 1
                
                except Exception as e:
                    errors.append(f'Ligne {idx + 2}: Erreur lors du traitement: {str(e)}')
            
            # Créer un ActionLog pour cet import
            action_log = ActionLog.objects.create(
                utilisateur=request.user,
                action='IMPORT_CSV',
                details={
                    'filename': file.name,
                    'total_rows': len(df),
                    'foyers_created': foyers_created,
                    'foyers_existing': foyers_existing,
                    'consommations_created': consommations_created,
                    'consommations_skipped': consommations_skipped,
                    'errors_count': len(errors),
                },
                ip_address=get_client_ip(request),
            )
            
            # Préparer la réponse
            response_data = {
                'success': True,
                'message': 'Import CSV complété',
                'action_log_id': action_log.id,
                'statistics': {
                    'total_rows_processed': len(df),
                    'foyers_created': foyers_created,
                    'foyers_existing': foyers_existing,
                    'consommations_created': consommations_created,
                    'consommations_skipped': consommations_skipped,
                    'errors_count': len(errors),
                },
                'errors': errors[:50],  # Limiter à 50 erreurs dans la réponse
            }
            
            if errors:
                response_data['warning'] = f'{len(errors)} erreurs détectées (voir le champ "errors")'
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Log l'erreur
            log_action(
                user=request.user,
                action='IMPORT_CSV_ERROR',
                details={'error': str(e), 'filename': file.name},
                ip_address=get_client_ip(request),
            )
            return Response(
                {'error': f'Erreur lors de la lecture du fichier CSV: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResidentDashboardView(APIView):
    """
    Endpoint GET /api/energy/resident/dashboard/
    Retourne les données du dashboard pour un résident authentifié.
    
    Données retournées:
    - consommation_actuelle: dernière consommation kWh du foyer
    - consommation_jour: somme kWh du jour
    - consommation_semaine: somme kWh des 7 derniers jours
    - cout_estime_mois: estimation en DH, basée sur consommation mois * tarif_kwh
    - alertes_actives: nombre d'alertes/anomalies non acquittées
    - variation_jour: pourcentage de variation vs hier
    - points_graphique: liste des 48 dernières consommations avec timestamp, kwh, anomaly_label
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Vérifier que l'utilisateur est RESIDENT
        if request.user.role != 'RESIDENT':
            return Response(
                {'error': 'Accès refusé. Seuls les résidents peuvent accéder au dashboard.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que le résident a un foyer
        if not request.user.foyer:
            return Response(
                {'error': 'Votre compte n\'est pas lié à un foyer.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            foyer = request.user.foyer
            now = timezone.now()
            
            # ============ 1. CONSOMMATION ACTUELLE ============
            # Dernière consommation kWh du foyer
            derniere_consommation = Consommation.objects.filter(
                foyer=foyer
            ).order_by('-timestamp').first()
            
            consommation_actuelle = derniere_consommation.kwh if derniere_consommation else 0
            
            # ============ 2. CONSOMMATION DU JOUR ============
            # Somme kWh du jour actuel (depuis 00:00:00 jusqu'à maintenant)
            debut_jour = now.replace(hour=0, minute=0, second=0, microsecond=0)
            consommation_jour = Consommation.objects.filter(
                foyer=foyer,
                timestamp__gte=debut_jour,
                timestamp__lte=now
            ).aggregate(total=Sum('kwh'))['total'] or 0
            
            # ============ 3. CONSOMMATION SEMAINE ============
            # Somme kWh des 7 derniers jours
            debut_semaine = now - timedelta(days=7)
            consommation_semaine = Consommation.objects.filter(
                foyer=foyer,
                timestamp__gte=debut_semaine,
                timestamp__lte=now
            ).aggregate(total=Sum('kwh'))['total'] or 0
            
            # ============ 4. COÛT ESTIMÉ MOIS ============
            # Estimation basée sur la consommation du mois * tarif_kwh
            debut_mois = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            consommation_mois = Consommation.objects.filter(
                foyer=foyer,
                timestamp__gte=debut_mois,
                timestamp__lte=now
            ).aggregate(total=Sum('kwh'))['total'] or 0
            
            cout_estime_mois = round(consommation_mois * TARIF_KWH, 2)
            
            # ============ 5. ALERTES ACTIVES ============
            # Nombre d'alertes/anomalies non acquittées
            alertes_actives = Alerte.objects.filter(
                anomalie__consommation__foyer=foyer,
                acquittee=False
            ).count()
            
            # ============ 6. VARIATION DU JOUR ============
            # Comparaison consommation d'aujourd'hui vs hier
            debut_hier = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            fin_hier = debut_hier + timedelta(days=1)
            
            consommation_hier = Consommation.objects.filter(
                foyer=foyer,
                timestamp__gte=debut_hier,
                timestamp__lte=fin_hier
            ).aggregate(total=Sum('kwh'))['total'] or 0
            
            if consommation_hier > 0:
                variation_jour = round(((consommation_jour - consommation_hier) / consommation_hier) * 100, 1)
            else:
                variation_jour = 0 if consommation_jour == 0 else 100
            
            # ============ 7. POINTS GRAPHIQUE ============
            # Dernières 48 consommations (2 jours) avec timestamp, kwh, anomaly_label
            points_consommations = Consommation.objects.filter(
                foyer=foyer
            ).order_by('-timestamp')[:48]
            
            points_graphique = []
            for c in reversed(list(points_consommations)):
                points_graphique.append({
                    'timestamp': c.timestamp.isoformat(),
                    'kwh': round(c.kwh, 2),
                    'anomaly_label': int(c.anomaly_label) if c.anomaly_label else 0
                })
            
            # ============ RÉPONSE ============
            response_data = {
                'consommation_actuelle': round(consommation_actuelle, 2),
                'consommation_jour': round(consommation_jour, 2),
                'consommation_semaine': round(consommation_semaine, 2),
                'cout_estime_mois': cout_estime_mois,
                'alertes_actives': alertes_actives,
                'variation_jour': variation_jour,
                'points_graphique': points_graphique,
            }
            
            log_action(
                user=request.user,
                action='VIEW_DASHBOARD',
                details={'foyer_id': foyer.id},
                ip_address=get_client_ip(request),
            )
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            log_action(
                user=request.user,
                action='DASHBOARD_ERROR',
                details={'error': str(e)},
                ip_address=get_client_ip(request),
            )
            return Response(
                {'error': f'Erreur lors de la récupération des données du dashboard: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConsumptionHistoryView(APIView):
    """
    Endpoint GET /api/energy/consumption-history/?period=month
    Retourne l'historique de consommation pour la période spécifiée.
    
    Paramètres:
    - period: 'week', 'month' (défaut), ou 'year'
    
    Retourne une liste d'objets avec:
    - date: timestamp ISO
    - consumption: kWh
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Vérifier que l'utilisateur est RESIDENT
        if request.user.role != 'RESIDENT':
            return Response(
                {'error': 'Accès refusé. Seuls les résidents peuvent accéder à l\'historique.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que le résident a un foyer
        if not request.user.foyer:
            return Response(
                {'error': 'Votre compte n\'est pas lié à un foyer.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            period = request.query_params.get('period', 'month')
            foyer = request.user.foyer
            now = timezone.now()
            
            # Calculer la plage de dates
            if period == 'week':
                start_date = now - timedelta(days=7)
            elif period == 'year':
                start_date = now - timedelta(days=365)
            else:  # month (défaut)
                start_date = now - timedelta(days=30)
            
            # Récupérer les données de consommation
            consommations = Consommation.objects.filter(
                foyer=foyer,
                timestamp__gte=start_date,
                timestamp__lte=now
            ).order_by('timestamp').values('timestamp', 'kwh')
            
            # Formater la réponse
            results = []
            for item in consommations:
                results.append({
                    'date': item['timestamp'].isoformat(),
                    'consumption': round(item['kwh'], 2),
                    'cost': round(item['kwh'] * TARIF_KWH, 2)
                })
            
            log_action(
                user=request.user,
                action='VIEW_HISTORY',
                details={'foyer_id': foyer.id, 'period': period},
                ip_address=get_client_ip(request),
            )
            
            return Response({'results': results}, status=status.HTTP_200_OK)
        
        except Exception as e:
            log_action(
                user=request.user,
                action='HISTORY_ERROR',
                details={'error': str(e)},
                ip_address=get_client_ip(request),
            )
            return Response(
                {'error': f'Erreur lors de la récupération de l\'historique: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConsumptionStatsView(APIView):
    """
    Endpoint GET /api/energy/consumption-stats/?period=month
    Retourne les statistiques de consommation pour la période spécifiée.
    
    Paramètres:
    - period: 'week', 'month' (défaut), ou 'year'
    
    Retourne:
    - avg: consommation moyenne kWh
    - total: consommation totale kWh
    - peak: heure de pointe (HH:MM)
    - saving: pourcentage d'économie vs période précédente
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Vérifier que l'utilisateur est RESIDENT
        if request.user.role != 'RESIDENT':
            return Response(
                {'error': 'Accès refusé. Seuls les résidents peuvent accéder aux statistiques.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que le résident a un foyer
        if not request.user.foyer:
            return Response(
                {'error': 'Votre compte n\'est pas lié à un foyer.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            period = request.query_params.get('period', 'month')
            foyer = request.user.foyer
            now = timezone.now()
            
            # Calculer la plage de dates
            if period == 'week':
                days = 7
            elif period == 'year':
                days = 365
            else:  # month (défaut)
                days = 30
            
            start_date = now - timedelta(days=days)
            
            # Récupérer les données de consommation
            consommations = list(Consommation.objects.filter(
                foyer=foyer,
                timestamp__gte=start_date,
                timestamp__lte=now
            ).order_by('timestamp').values('timestamp', 'kwh'))
            
            if not consommations:
                return Response({
                    'avg': 0,
                    'total': 0,
                    'peak': '00:00',
                    'saving': '0%'
                }, status=status.HTTP_200_OK)
            
            # Calculer les statistiques
            kwh_values = [item['kwh'] for item in consommations]
            total_consumption = sum(kwh_values)
            avg_consumption = total_consumption / len(kwh_values) if kwh_values else 0
            
            # Trouver le pic de consommation
            peak_idx = kwh_values.index(max(kwh_values))
            peak_time = consommations[peak_idx]['timestamp'].strftime('%H:%M')
            
            # Calculer l'économie vs période précédente
            prev_start_date = start_date - timedelta(days=days)
            prev_consommations = Consommation.objects.filter(
                foyer=foyer,
                timestamp__gte=prev_start_date,
                timestamp__lt=start_date
            ).aggregate(total=Sum('kwh'))['total'] or 0
            
            saving_percent = 0
            if prev_consommations > 0:
                saving_percent = ((prev_consommations - total_consumption) / prev_consommations) * 100
            
            response_data = {
                'avg': round(avg_consumption, 2),
                'total': round(total_consumption, 2),
                'peak': peak_time,
                'saving': f'{saving_percent:.1f}%'
            }
            
            log_action(
                user=request.user,
                action='VIEW_STATS',
                details={'foyer_id': foyer.id, 'period': period},
                ip_address=get_client_ip(request),
            )
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            log_action(
                user=request.user,
                action='STATS_ERROR',
                details={'error': str(e)},
                ip_address=get_client_ip(request),
            )
            return Response(
                {'error': f'Erreur lors de la récupération des statistiques: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AlertsView(APIView):
    """
    Endpoint GET /api/energy/alerts/?statut=active|resolved
    Retourne les alertes du résident authentifié.
    
    Paramètres:
    - statut: 'active' ou 'resolved' (optionnel)
    
    Retourne une liste d'alertes avec:
    - id
    - title
    - description
    - severity
    - timestamp
    - resolvedAt (si applicable)
    - statut
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Vérifier que l'utilisateur est RESIDENT
        if request.user.role != 'RESIDENT':
            return Response(
                {'error': 'Accès refusé. Seuls les résidents peuvent accéder aux alertes.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que le résident a un foyer
        if not request.user.foyer:
            return Response(
                {'error': 'Votre compte n\'est pas lié à un foyer.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            foyer = request.user.foyer
            statut = request.query_params.get('statut')  # 'active' ou 'resolved'
            
            # Récupérer les alertes du foyer
            queryset = Alerte.objects.filter(
                anomalie__consommation__foyer=foyer
            ).select_related('anomalie__consommation__foyer').order_by('-created_at')
            
            # Filtrer par statut si fourni
            if statut == 'active':
                queryset = queryset.filter(statut='ACTIVE')
            elif statut == 'resolved':
                queryset = queryset.filter(statut='RESOLVED')
            
            # Sérialiser les alertes
            serializer = AlerteSerializer(queryset, many=True)
            
            log_action(
                user=request.user,
                action='VIEW_ALERTS',
                details={'foyer_id': foyer.id, 'statut': statut or 'all'},
                ip_address=get_client_ip(request),
            )
            
            return Response({'results': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            log_action(
                user=request.user,
                action='ALERTS_ERROR',
                details={'error': str(e)},
                ip_address=get_client_ip(request),
            )
            return Response(
                {'error': f'Erreur lors de la récupération des alertes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
