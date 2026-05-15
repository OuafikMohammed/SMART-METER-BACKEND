"""
Views pour les nouveaux endpoints du Cahier des Charges SmartMeter.

Endpoints:
- GET /api/auth/me/
- GET /api/admin/residents/
- GET /api/admin/dashboard/
- GET /api/admin/foyers/
- GET /api/admin/anomalies/
- GET /api/admin/analytics/*
- GET /api/resident/dashboard/
- GET /api/resident/readings/
"""

from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, DecimalField, Count, Q
from django.db.models.functions import TruncDate
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ConsumptionReading, Foyer, Consommation, Anomalie, Alerte
from .permissions import EstAdmin, EstResident
from .serializers import (
    CurrentUserSerializer,
    AdminDashboardSerializer,
    AdminDashboardResidentSerializer,
    AdminDashboardConsumptionDaySerializer,
    ResidentDashboardSerializer,
    ResidentDashboardReadingSerializer,
    ConsumptionReadingSerializer,
    ResidentSimpleSerializer,
    AnomalieSerializer,
)

User = get_user_model()

# Tarif kWh (2.5 DH par kWh - valeur par défaut)
TARIF_KWH = 2.5


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    GET /api/auth/me/
    
    Retourne les informations de l'utilisateur connecté.
    
    Réponse:
    {
        "id": 1,
        "email": "user@example.com",
        "username": "username",
        "first_name": "First",
        "last_name": "Last",
        "role": "ADMIN",
        "managed_by": null,
        "managed_by_email": null,
        "is_active": true
    }
    """
    serializer = CurrentUserSerializer(request.user)
    return Response(serializer.data)


class AdminResidentsListView(APIView):
    """
    GET /api/admin/residents/ - Liste les résidents
    POST /api/admin/residents/ - Créer un résident
    
    Accessible uniquement aux ADMIN.
    
    Réponse GET:
    {
        "count": 2,
        "residents": [
            {
                "id": 2,
                "email": "resident@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "RESIDENT"
            }
        ]
    }
    
    Request POST:
    {
        "email": "new_resident@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "SecurePass123!"
    }
    """
    permission_classes = [IsAuthenticated, EstAdmin]
    
    def get(self, request):
        # Récupérer uniquement les résidents gérés par cet admin
        residents = User.objects.filter(
            role='RESIDENT',
            managed_by=request.user
        ).order_by('email')
        
        serializer = ResidentSimpleSerializer(residents, many=True)
        
        return Response({
            'count': residents.count(),
            'residents': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Créer un nouveau résident géré par cet admin"""
        try:
            email = request.data.get('email')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            password = request.data.get('password')
            
            # Validation
            if not email or not password:
                return Response(
                    {'error': 'email et password sont obligatoires'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier si l'email existe déjà
            if User.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Cet email est déjà utilisé'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Créer le résident
            username = email.split('@')[0]  # Utiliser la partie avant @ comme username
            # S'assurer que le username est unique
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            resident = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role='RESIDENT',
                managed_by=request.user
            )
            
            serializer = ResidentSimpleSerializer(resident)
            return Response(
                {
                    'message': 'Résident créé avec succès',
                    'resident': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la création du résident: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminResidentDetailView(APIView):
    """
    GET /api/admin/residents/{id}/ - Récupérer les détails d'un résident
    PATCH /api/admin/residents/{id}/ - Modifier un résident
    DELETE /api/admin/residents/{id}/ - Supprimer un résident
    
    Accessible uniquement aux ADMIN et pour leurs résidents
    """
    permission_classes = [IsAuthenticated, EstAdmin]
    
    def get(self, request, resident_id):
        """Récupérer les détails d'un résident"""
        try:
            resident = User.objects.get(
                id=resident_id,
                role='RESIDENT',
                managed_by=request.user
            )
            serializer = ResidentSimpleSerializer(resident)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Résident non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def patch(self, request, resident_id):
        """Modifier un résident"""
        try:
            resident = User.objects.get(
                id=resident_id,
                role='RESIDENT',
                managed_by=request.user
            )
            
            # Mettre à jour les champs autorisés
            if 'first_name' in request.data:
                resident.first_name = request.data['first_name']
            if 'last_name' in request.data:
                resident.last_name = request.data['last_name']
            if 'email' in request.data:
                # Vérifier que le nouvel email n'existe pas déjà
                new_email = request.data['email']
                if new_email != resident.email and User.objects.filter(email=new_email).exists():
                    return Response(
                        {'error': 'Cet email est déjà utilisé'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                resident.email = new_email
            if 'password' in request.data:
                resident.set_password(request.data['password'])
            
            resident.save()
            serializer = ResidentSimpleSerializer(resident)
            return Response(
                {
                    'message': 'Résident modifié avec succès',
                    'resident': serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Résident non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la modification du résident: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, resident_id):
        """Supprimer un résident"""
        try:
            resident = User.objects.get(
                id=resident_id,
                role='RESIDENT',
                managed_by=request.user
            )
            
            resident_email = resident.email
            resident.delete()
            
            return Response(
                {'message': f'Résident {resident_email} supprimé avec succès'},
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Résident non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la suppression du résident: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminDashboardView(APIView):
    """
    GET /api/admin/dashboard/
    
    Dashboard agrégé pour l'admin.
    Retourne les données de consommation de tous ses résidents.
    Accessible uniquement aux ADMIN.
    
    Réponse:
    {
        "admin_email": "admin@example.com",
        "total_residents": 2,
        "total_consumption_kwh": 127.4,
        "total_cost_estimate": 31.85,
        "average_consumption_per_resident": 63.7,
        "residents": [
            {
                "email": "resident1@example.com",
                "numero_foyer": "F001",
                "total_consumption_kwh": 65.6,
                "total_cost_estimate": 16.4
            }
        ],
        "consumption_by_day": [
            {
                "date": "2026-05-01",
                "total_consumption_kwh": 13.9
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated, EstAdmin]
    
    def get(self, request):
        # Récupérer les résidents gérés par cet admin
        residents = User.objects.filter(
            role='RESIDENT',
            managed_by=request.user
        )
        
        if not residents.exists():
            return Response({
                'admin_email': request.user.email,
                'total_residents': 0,
                'total_consumption_kwh': 0,
                'total_cost_estimate': 0,
                'average_consumption_per_resident': 0,
                'residents': [],
                'consumption_by_day': [],
            }, status=status.HTTP_200_OK)
        
        # Récupérer les foyers des résidents gérés
        foyers = Foyer.objects.filter(utilisateurs__in=residents).distinct()
        
        if not foyers.exists():
            return Response({
                'admin_email': request.user.email,
                'total_residents': residents.count(),
                'total_consumption_kwh': 0,
                'total_cost_estimate': 0,
                'average_consumption_per_resident': 0,
                'residents': [],
                'consumption_by_day': [],
            }, status=status.HTTP_200_OK)
        
        # Récupérer toutes les consommations des foyers
        consommations = Consommation.objects.filter(foyer__in=foyers).order_by('-timestamp')
        
        # Calculer les totaux
        total_kwh = consommations.aggregate(
            total=Sum('kwh')
        )['total'] or 0
        total_kwh = float(total_kwh)
        
        total_cost = round(total_kwh * TARIF_KWH, 2)
        
        # Données par résident (foyer)
        residents_data = []
        for foyer in foyers:
            foyer_consommations = consommations.filter(foyer=foyer)
            foyer_kwh = foyer_consommations.aggregate(total=Sum('kwh'))['total'] or 0
            foyer_kwh = float(foyer_kwh)
            foyer_cost = round(foyer_kwh * TARIF_KWH, 2)
            
            # Récupérer le résident
            resident = foyer.utilisateurs.filter(role='RESIDENT').first()
            resident_email = resident.email if resident else 'Unknown'
            
            residents_data.append({
                'email': resident_email,
                'numero_foyer': foyer.numero_foyer,
                'total_consumption_kwh': foyer_kwh,
                'total_cost_estimate': foyer_cost,
            })
        
        # Consommation par jour
        consumption_by_day_data = []
        daily_consommations = consommations.annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            daily_consumption=Sum('kwh')
        ).order_by('date')
        
        for item in daily_consommations:
            consumption_by_day_data.append({
                'date': item['date'],
                'total_consumption_kwh': float(item['daily_consumption'] or 0),
            })
        
        # Moyenne par résident
        avg_per_resident = total_kwh / residents.count() if residents.count() > 0 else 0
        
        response_data = {
            'admin_email': request.user.email,
            'total_residents': residents.count(),
            'total_consumption_kwh': round(total_kwh, 2),
            'total_cost_estimate': total_cost,
            'average_consumption_per_resident': round(avg_per_resident, 2),
            'residents': residents_data,
            'consumption_by_day': consumption_by_day_data,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class ResidentDashboardView(APIView):
    """
    GET /api/resident/dashboard/
    
    Dashboard pour le résident.
    Retourne les statistiques de consommation du résident connecté.
    Accessible uniquement aux RESIDENT.
    
    Réponse:
    {
        "consommation_actuelle": 8.5,
        "consommation_jour": 25.3,
        "consommation_semaine": 187.2,
        "cout_estime_mois": 192.5,
        "alertes_actives": 2,
        "variation_jour": 12.5,
        "points_graphique": [
            {
                "timestamp": "2026-05-01T12:00:00Z",
                "kwh": 8.5,
                "anomaly_label": 0
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated, EstResident]
    
    def get(self, request):
        try:
            now = timezone.now()
            
            # Priorité 1: Vérifier s'il y a des readings ConsumptionReading
            readings = ConsumptionReading.objects.filter(
                resident=request.user
            ).order_by('-timestamp')
            
            if readings.exists():
                # Utiliser ConsumptionReading (nouveau modèle)
                return self._get_dashboard_from_readings(readings, now)
            
            # Priorité 2: Vérifier s'il y a un foyer avec Consommation
            foyer = request.user.foyer
            if foyer:
                consommations = Consommation.objects.filter(
                    foyer=foyer
                ).order_by('-timestamp')
                
                if consommations.exists():
                    return self._get_dashboard_from_consommation(consommations, foyer, now, request.user)
            
            # Pas de données disponibles
            return Response({
                'consommation_actuelle': 0,
                'consommation_jour': 0,
                'consommation_semaine': 0,
                'cout_estime_mois': 0,
                'alertes_actives': 0,
                'variation_jour': 0,
                'points_graphique': [],
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des données: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_dashboard_from_readings(self, readings, now):
        """Construit le dashboard à partir de ConsumptionReading"""
        
        # 1. CONSOMMATION ACTUELLE (dernière lecture)
        consommation_actuelle = float(readings.first().consumption_kwh) if readings.exists() else 0
        
        # 2. CONSOMMATION DU JOUR
        debut_jour = now.replace(hour=0, minute=0, second=0, microsecond=0)
        consommation_jour = readings.filter(
            timestamp__gte=debut_jour,
            timestamp__lte=now
        ).aggregate(total=Sum('consumption_kwh', output_field=DecimalField()))['total'] or 0
        consommation_jour = float(consommation_jour)
        
        # 3. CONSOMMATION SEMAINE
        debut_semaine = now - timedelta(days=7)
        consommation_semaine = readings.filter(
            timestamp__gte=debut_semaine,
            timestamp__lte=now
        ).aggregate(total=Sum('consumption_kwh', output_field=DecimalField()))['total'] or 0
        consommation_semaine = float(consommation_semaine)
        
        # 4. COÛT ESTIMÉ MOIS
        debut_mois = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        consommation_mois = readings.filter(
            timestamp__gte=debut_mois,
            timestamp__lte=now
        ).aggregate(total=Sum('consumption_kwh', output_field=DecimalField()))['total'] or 0
        cout_estime_mois = round(float(consommation_mois) * TARIF_KWH, 2)
        
        # 5. ALERTES ACTIVES
        # Comptabiliser les alertes sans ConsumptionReading directement
        alertes_actives = 0
        
        # 6. VARIATION DU JOUR
        debut_hier = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        fin_hier = debut_hier + timedelta(days=1)
        
        consommation_hier = readings.filter(
            timestamp__gte=debut_hier,
            timestamp__lt=debut_jour
        ).aggregate(total=Sum('consumption_kwh', output_field=DecimalField()))['total'] or 0
        consommation_hier = float(consommation_hier)
        
        if consommation_hier > 0:
            variation_jour = round(((consommation_jour - consommation_hier) / consommation_hier) * 100, 1)
        else:
            variation_jour = 0 if consommation_jour == 0 else 100
        
        # 7. POINTS GRAPHIQUE (48 derniers points)
        points_consommations = readings.order_by('-timestamp')[:48]
        points_graphique = []
        for reading in reversed(list(points_consommations)):
            points_graphique.append({
                'timestamp': reading.timestamp.isoformat(),
                'kwh': float(reading.consumption_kwh),
                'anomaly_label': 0  # ConsumptionReading n'a pas de champ anomaly_label
            })
        
        return Response({
            'consommation_actuelle': round(consommation_actuelle, 2),
            'consommation_jour': round(consommation_jour, 2),
            'consommation_semaine': round(consommation_semaine, 2),
            'cout_estime_mois': cout_estime_mois,
            'alertes_actives': alertes_actives,
            'variation_jour': variation_jour,
            'points_graphique': points_graphique,
        }, status=status.HTTP_200_OK)
    
    def _get_dashboard_from_consommation(self, consommations, foyer, now, user):
        """Construit le dashboard à partir de Consommation (modèle hérité)"""
        
        # 1. CONSOMMATION ACTUELLE (dernière consommation)
        consommation_actuelle = consommations.first().kwh if consommations.exists() else 0
        
        # 2. CONSOMMATION DU JOUR
        debut_jour = now.replace(hour=0, minute=0, second=0, microsecond=0)
        consommation_jour = consommations.filter(
            timestamp__gte=debut_jour,
            timestamp__lte=now
        ).aggregate(total=Sum('kwh'))['total'] or 0
        
        # 3. CONSOMMATION SEMAINE
        debut_semaine = now - timedelta(days=7)
        consommation_semaine = consommations.filter(
            timestamp__gte=debut_semaine,
            timestamp__lte=now
        ).aggregate(total=Sum('kwh'))['total'] or 0
        
        # 4. COÛT ESTIMÉ MOIS
        debut_mois = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        consommation_mois = consommations.filter(
            timestamp__gte=debut_mois,
            timestamp__lte=now
        ).aggregate(total=Sum('kwh'))['total'] or 0
        cout_estime_mois = round(consommation_mois * TARIF_KWH, 2)
        
        # 5. ALERTES ACTIVES
        alertes_actives = Alerte.objects.filter(
            anomalie__consommation__foyer=foyer,
            acquittee=False
        ).count()
        
        # 6. VARIATION DU JOUR
        debut_hier = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        fin_hier = debut_hier + timedelta(days=1)
        
        consommation_hier = consommations.filter(
            timestamp__gte=debut_hier,
            timestamp__lt=debut_jour
        ).aggregate(total=Sum('kwh'))['total'] or 0
        
        if consommation_hier > 0:
            variation_jour = round(((consommation_jour - consommation_hier) / consommation_hier) * 100, 1)
        else:
            variation_jour = 0 if consommation_jour == 0 else 100
        
        # 7. POINTS GRAPHIQUE (48 derniers points)
        points_consommations = consommations.order_by('-timestamp')[:48]
        points_graphique = []
        for c in reversed(list(points_consommations)):
            points_graphique.append({
                'timestamp': c.timestamp.isoformat(),
                'kwh': round(c.kwh, 2),
                'anomaly_label': int(c.anomaly_label) if c.anomaly_label else 0
            })
        
        return Response({
            'consommation_actuelle': round(consommation_actuelle, 2),
            'consommation_jour': round(consommation_jour, 2),
            'consommation_semaine': round(consommation_semaine, 2),
            'cout_estime_mois': cout_estime_mois,
            'alertes_actives': alertes_actives,
            'variation_jour': variation_jour,
            'points_graphique': points_graphique,
        }, status=status.HTTP_200_OK)


class ResidentReadingsView(APIView):
    """
    GET /api/resident/readings/?meter_id=MTR-001&start_date=2026-05-01&end_date=2026-05-07
    
    Récupère les readings du résident connecté.
    Accessible uniquement aux RESIDENT.
    
    Paramètres optionnels:
    - meter_id: Filtre par meter_id
    - start_date: Date de début (YYYY-MM-DD)
    - end_date: Date de fin (YYYY-MM-DD)
    - tariff_type: Filtre par type de tarif
    
    Réponse:
    {
        "count": 7,
        "readings": [
            {
                "id": 1,
                "resident": 2,
                "resident_email": "resident@example.com",
                "meter_id": "MTR-001",
                "timestamp": "2026-05-01T00:00:00Z",
                "consumption_kwh": 8.5,
                "cost_estimate": 2.125,
                "tariff_type": "standard",
                "created_at": "2026-05-01T00:00:00Z",
                "updated_at": "2026-05-01T00:00:00Z"
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated, EstResident]
    
    def get(self, request):
        # Récupérer les readings du résident
        readings = ConsumptionReading.objects.filter(
            resident=request.user
        ).order_by('-timestamp')
        
        # Filtrer par meter_id si fourni
        meter_id = request.query_params.get('meter_id')
        if meter_id:
            readings = readings.filter(meter_id=meter_id)
        
        # Filtrer par tariff_type si fourni
        tariff_type = request.query_params.get('tariff_type')
        if tariff_type:
            readings = readings.filter(tariff_type=tariff_type)
        
        # Filtrer par plage de dates si fourni
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            readings = readings.filter(timestamp__gte=start_date)
        if end_date:
            readings = readings.filter(timestamp__lte=end_date)
        
        # Sérialiser
        serializer = ConsumptionReadingSerializer(readings, many=True)
        
        return Response({
            'count': readings.count(),
            'readings': serializer.data,
        }, status=status.HTTP_200_OK)


class AdminFoyersListView(APIView):
    """
    GET /api/admin/foyers/
    
    Liste tous les foyers des résidents gérés par l'admin connecté.
    Accessible uniquement aux ADMIN.
    
    Réponse:
    {
        "count": 4,
        "results": [
            {
                "id": 1,
                "numero_foyer": "F001",
                "adresse": "123 Rue de la Paix",
                "code_postal": "75001",
                "ville": "Paris",
                "puissance_souscrite": 9.0,
                "resident_email": "resident1@example.com",
                "resident_name": "John Doe",
                "is_active": true
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated, EstAdmin]
    
    def get(self, request):
        # Récupérer les résidents gérés par cet admin
        residents = User.objects.filter(
            role='RESIDENT',
            managed_by=request.user
        ).exclude(foyer__isnull=True)
        
        # Récupérer les foyers de ces résidents
        foyers = []
        for resident in residents:
            if resident.foyer:
                foyer_data = {
                    'id': resident.foyer.id,
                    'numero_foyer': resident.foyer.numero_foyer,
                    'adresse': resident.foyer.adresse,
                    'code_postal': resident.foyer.code_postal,
                    'ville': resident.foyer.ville,
                    'puissance_souscrite': resident.foyer.puissance_souscrite,
                    'resident_email': resident.email,
                    'resident_name': f"{resident.first_name} {resident.last_name}".strip() or resident.email,
                    'is_active': resident.foyer.is_active,
                }
                foyers.append(foyer_data)
        
        return Response({
            'count': len(foyers),
            'results': foyers,
        }, status=status.HTTP_200_OK)


class AdminAnalyticsConsumptionView(APIView):
    """
    GET /api/admin/analytics/consumption/
    
    Retourne les données de consommation en détail.
    Accessible uniquement aux ADMIN.
    """
    permission_classes = [IsAuthenticated, EstAdmin]
    
    def get(self, request):
        # Récupérer les résidents gérés par cet admin
        residents = User.objects.filter(
            role='RESIDENT',
            managed_by=request.user
        )
        
        # Récupérer les readings
        readings = ConsumptionReading.objects.filter(
            resident__in=residents
        ).order_by('-timestamp')
        
        # Regrouper par résident et jour
        from django.db.models import Count
        daily_data = []
        
        daily_readings = readings.annotate(
            date=TruncDate('timestamp')
        ).values('date', 'resident__email').annotate(
            daily_consumption=Sum('consumption_kwh', output_field=DecimalField()),
            reading_count=Count('id'),
            daily_cost=Sum('cost_estimate', output_field=DecimalField())
        ).order_by('-date')
        
        for item in daily_readings:
            daily_data.append({
                'date': item['date'],
                'resident_email': item['resident__email'],
                'total_consumption_kwh': float(item['daily_consumption'] or 0),
                'reading_count': item['reading_count'],
                'total_cost': float(item['daily_cost'] or 0),
            })
        
        return Response({
            'results': daily_data,
        }, status=status.HTTP_200_OK)


class AdminAnalyticsTopConsumersView(APIView):
    """
    GET /api/admin/analytics/top-consumers/
    
    Retourne les résidents avec la plus haute consommation.
    Accessible uniquement aux ADMIN.
    """
    permission_classes = [IsAuthenticated, EstAdmin]
    
    def get(self, request):
        # Récupérer les résidents gérés par cet admin
        residents = User.objects.filter(
            role='RESIDENT',
            managed_by=request.user
        )
        
        # Récupérer les readings
        readings = ConsumptionReading.objects.filter(
            resident__in=residents
        )
        
        # Calculer la consommation par résident
        top_consumers = []
        for resident in residents:
            resident_readings = readings.filter(resident=resident)
            total_kwh = resident_readings.aggregate(
                total=Sum('consumption_kwh', output_field=DecimalField())
            )['total'] or 0
            
            if total_kwh > 0:
                top_consumers.append({
                    'resident_email': resident.email,
                    'resident_name': f"{resident.first_name} {resident.last_name}".strip() or resident.email,
                    'total_consumption_kwh': float(total_kwh),
                    'reading_count': resident_readings.count(),
                })
        
        # Trier par consommation décroissante
        top_consumers.sort(key=lambda x: x['total_consumption_kwh'], reverse=True)
        
        return Response({
            'results': top_consumers[:10],  # Top 10
        }, status=status.HTTP_200_OK)


class AdminAnalyticsStatsView(APIView):
    """
    GET /api/admin/analytics/stats/
    
    Retourne les statistiques globales.
    Accessible uniquement aux ADMIN.
    """
    permission_classes = [IsAuthenticated, EstAdmin]
    
    def get(self, request):
        # Récupérer les résidents gérés par cet admin
        residents = User.objects.filter(
            role='RESIDENT',
            managed_by=request.user
        )
        
        # Récupérer les readings
        readings = ConsumptionReading.objects.filter(
            resident__in=residents
        )
        
        # Calculer les stats
        total_kwh = readings.aggregate(
            total=Sum('consumption_kwh', output_field=DecimalField())
        )['total'] or 0
        
        total_cost = readings.aggregate(
            total=Sum('cost_estimate', output_field=DecimalField())
        )['total'] or 0
        
        reading_count = readings.count()
        
        # Moyenne
        avg_consumption = total_kwh / reading_count if reading_count > 0 else 0
        
        # Min/Max
        min_reading = readings.order_by('consumption_kwh').first()
        max_reading = readings.order_by('-consumption_kwh').first()
        
        min_kwh = float(min_reading.consumption_kwh) if min_reading else 0
        max_kwh = float(max_reading.consumption_kwh) if max_reading else 0
        
        stats = {
            'total_residents': residents.count(),
            'total_readings': reading_count,
            'total_consumption_kwh': float(total_kwh),
            'total_cost_estimate': float(total_cost),
            'average_consumption_kwh': float(avg_consumption),
            'min_consumption_kwh': min_kwh,
            'max_consumption_kwh': max_kwh,
            'average_cost_per_reading': float(total_cost / reading_count) if reading_count > 0 else 0,
        }
        
        return Response(stats, status=status.HTTP_200_OK)
