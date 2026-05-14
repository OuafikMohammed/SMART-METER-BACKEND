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

from django.utils import timezone
from django.db.models import Sum, DecimalField, Count, Q
from django.db.models.functions import TruncDate
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ConsumptionReading, Foyer, Consommation, Anomalie
from .permissions import IsAdminRole, IsResidentRole
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
    GET /api/admin/residents/
    
    Liste les résidents gérés par l'admin connecté.
    Accessible uniquement aux ADMIN.
    
    Réponse:
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
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    
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
                "meter_id": "MTR-001",
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
    permission_classes = [IsAuthenticated, IsAdminRole]
    
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
        
        # Récupérer les readings de tous les résidents
        readings = ConsumptionReading.objects.filter(
            resident__in=residents
        )
        
        # Calculer les totaux
        total_kwh = readings.aggregate(
            total=Sum('consumption_kwh', output_field=DecimalField())
        )['total'] or 0
        
        total_cost = readings.aggregate(
            total=Sum('cost_estimate', output_field=DecimalField())
        )['total'] or 0
        
        # Données par résident
        residents_data = []
        for resident in residents:
            resident_readings = readings.filter(resident=resident)
            resident_kwh = resident_readings.aggregate(
                total=Sum('consumption_kwh', output_field=DecimalField())
            )['total'] or 0
            resident_cost = resident_readings.aggregate(
                total=Sum('cost_estimate', output_field=DecimalField())
            )['total'] or 0
            
            # Prendre le premier meter_id du résident
            first_reading = resident_readings.first()
            meter_id = first_reading.meter_id if first_reading else 'UNKNOWN'
            
            residents_data.append({
                'email': resident.email,
                'meter_id': meter_id,
                'total_consumption_kwh': resident_kwh,
                'total_cost_estimate': resident_cost,
            })
        
        # Consommation par jour
        consumption_by_day_data = []
        daily_readings = readings.annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            daily_consumption=Sum('consumption_kwh', output_field=DecimalField())
        ).order_by('date')
        
        for item in daily_readings:
            consumption_by_day_data.append({
                'date': item['date'],
                'total_consumption_kwh': item['daily_consumption'] or 0,
            })
        
        # Moyenne par résident
        avg_per_resident = total_kwh / residents.count() if residents.count() > 0 else 0
        
        response_data = {
            'admin_email': request.user.email,
            'total_residents': residents.count(),
            'total_consumption_kwh': total_kwh,
            'total_cost_estimate': total_cost,
            'average_consumption_per_resident': avg_per_resident,
            'residents': residents_data,
            'consumption_by_day': consumption_by_day_data,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class ResidentDashboardView(APIView):
    """
    GET /api/resident/dashboard/
    
    Dashboard pour le résident.
    Retourne uniquement les données du résident connecté.
    Accessible uniquement aux RESIDENT.
    
    Réponse:
    {
        "resident_email": "resident@example.com",
        "meter_id": "MTR-001",
        "total_consumption_kwh": 65.6,
        "total_cost_estimate": 16.4,
        "average_daily_consumption": 9.4,
        "readings": [
            {
                "id": 1,
                "meter_id": "MTR-001",
                "timestamp": "2026-05-01T12:00:00Z",
                "consumption_kwh": 8.5,
                "cost_estimate": 2.125,
                "tariff_type": "standard"
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated, IsResidentRole]
    
    def get(self, request):
        # Récupérer les readings du résident
        readings = ConsumptionReading.objects.filter(
            resident=request.user
        ).order_by('-timestamp')
        
        if not readings.exists():
            return Response({
                'resident_email': request.user.email,
                'meter_id': 'UNKNOWN',
                'total_consumption_kwh': 0,
                'total_cost_estimate': 0,
                'average_daily_consumption': 0,
                'readings': [],
            }, status=status.HTTP_200_OK)
        
        # Calculer les statistiques
        total_kwh = readings.aggregate(
            total=Sum('consumption_kwh', output_field=DecimalField())
        )['total'] or 0
        
        total_cost = readings.aggregate(
            total=Sum('cost_estimate', output_field=DecimalField())
        )['total'] or 0
        
        # Nombre de jours avec données
        dates_count = readings.values('timestamp__date').distinct().count()
        avg_daily = total_kwh / dates_count if dates_count > 0 else 0
        
        # Meter ID (prendre le premier du résident)
        meter_id = readings.first().meter_id if readings.first() else 'UNKNOWN'
        
        # Sérialiser les readings
        readings_serializer = ResidentDashboardReadingSerializer(readings, many=True)
        
        response_data = {
            'resident_email': request.user.email,
            'meter_id': meter_id,
            'total_consumption_kwh': total_kwh,
            'total_cost_estimate': total_cost,
            'average_daily_consumption': avg_daily,
            'readings': readings_serializer.data,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


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
    permission_classes = [IsAuthenticated, IsResidentRole]
    
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
    permission_classes = [IsAuthenticated, IsAdminRole]
    
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
    permission_classes = [IsAuthenticated, IsAdminRole]
    
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
    permission_classes = [IsAuthenticated, IsAdminRole]
    
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
    permission_classes = [IsAuthenticated, IsAdminRole]
    
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
