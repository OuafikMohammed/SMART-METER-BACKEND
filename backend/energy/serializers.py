"""REST API serializers pour l'app energy."""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from .models import ActionLog, Alerte, Anomalie, Consommation, ConversationIA, Foyer, ConsumptionReading

User = get_user_model()


class FoyerSerializer(serializers.ModelSerializer):
    utilisateurs_count = serializers.SerializerMethodField()

    class Meta:
        model = Foyer
        fields = [
            'id',
            'numero_foyer',
            'adresse',
            'code_postal',
            'ville',
            'puissance_souscrite',
            'is_active',
            'utilisateurs_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_utilisateurs_count(self, obj):
        return obj.utilisateurs.count()


class ConsommationSerializer(serializers.ModelSerializer):
    foyer_numero = serializers.CharField(source='foyer.numero_foyer', read_only=True)

    class Meta:
        model = Consommation
        fields = ['id', 'foyer', 'foyer_numero', 'timestamp', 'kwh', 'anomaly_label', 'temperature']
        read_only_fields = ['timestamp']


class AnomalieSerializer(serializers.ModelSerializer):
    """Serializer pour les anomalies avec détails Hugging Face."""
    consommation_kwh = serializers.FloatField(source='consommation.kwh', read_only=True)
    foyer_numero = serializers.CharField(source='consommation.foyer.numero_foyer', read_only=True)
    foyer_id = serializers.IntegerField(source='consommation.foyer.id', read_only=True)
    timestamp_consommation = serializers.DateTimeField(source='consommation.timestamp', read_only=True)
    temperature = serializers.FloatField(source='consommation.temperature', read_only=True)
    
    class Meta:
        model = Anomalie
        fields = [
            'id',
            'consommation',
            'consommation_kwh',
            'foyer_numero',
            'foyer_id',
            'timestamp_consommation',
            'temperature',
            'score_confiance',  # RG8: Score Hugging Face
            'severite',
            'statut',  # RG9: Statuts anomalie
            'consultee_at',
            'acquittee_at',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'consultee_at', 'acquittee_at']


class AlerteSerializer(serializers.ModelSerializer):
    """Serializer pour les alertes avec détails anomalie et foyer."""
    anomalie_severite = serializers.CharField(source='anomalie.get_severite_display', read_only=True)
    anomalie_score = serializers.FloatField(source='anomalie.score_confiance', read_only=True)
    anomalie_statut = serializers.CharField(source='anomalie.get_statut_display', read_only=True)
    foyer_numero = serializers.CharField(source='anomalie.consommation.foyer.numero_foyer', read_only=True)
    foyer_id = serializers.IntegerField(source='anomalie.consommation.foyer.id', read_only=True)
    timestamp_anomalie = serializers.DateTimeField(source='anomalie.created_at', read_only=True)

    class Meta:
        model = Alerte
        fields = [
            'id',
            'anomalie',
            'anomalie_severite',
            'anomalie_score',
            'anomalie_statut',
            'foyer_numero',
            'foyer_id',
            'statut',  # RG11: Admin traite alertes
            'acquittee',  # RG12: Archivage
            'timestamp_anomalie',
            'created_at',
            'consultee_at',
            'acquittee_at',
        ]
        read_only_fields = ['created_at', 'consultee_at', 'acquittee_at']


class ConversationIASerializer(serializers.ModelSerializer):
    utilisateur_username = serializers.CharField(source='utilisateur.username', read_only=True)

    class Meta:
        model = ConversationIA
        fields = ['id', 'utilisateur', 'utilisateur_username', 'question', 'reponse', 'timestamp']
        read_only_fields = ['timestamp']


class ActionLogSerializer(serializers.ModelSerializer):
    utilisateur_username = serializers.CharField(source='utilisateur.username', read_only=True)

    class Meta:
        model = ActionLog
        fields = ['id', 'utilisateur', 'utilisateur_username', 'action', 'details', 'timestamp', 'ip_address']
        read_only_fields = ['timestamp', 'utilisateur', 'utilisateur_username', 'ip_address']


# ============================================================================
# NEW SERIALIZERS FOR ADMIN AND RESIDENT ENDPOINTS
# ============================================================================

class FoyerDetailSerializer(serializers.ModelSerializer):
    """
    Serializer détaillé pour un foyer (avec count de residents et consommations).
    Utilisé par admin/foyers/.
    """
    residents_count = serializers.SerializerMethodField()
    consommations_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Foyer
        fields = [
            'id', 'numero_foyer', 'adresse', 'code_postal', 'ville',
            'puissance_souscrite', 'is_active', 'residents_count',
            'consommations_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_residents_count(self, obj):
        return obj.utilisateurs.count()
    
    def get_consommations_count(self, obj):
        return obj.consommations.count()


class UserResidentListSerializer(serializers.ModelSerializer):
    """
    Serializer pour lister les résidents avec leurs données réelles.
    Utilisé par admin/residents/.
    """
    foyer = FoyerDetailSerializer(read_only=True)
    consommation_jour = serializers.SerializerMethodField()
    consommation_semaine = serializers.SerializerMethodField()
    anomalies_actives = serializers.SerializerMethodField()
    alertes_non_acquittees = serializers.SerializerMethodField()
    derniere_mesure = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'foyer', 'consommation_jour', 'consommation_semaine',
            'anomalies_actives', 'alertes_non_acquittees', 'derniere_mesure'
        ]
    
    def get_consommation_jour(self, obj):
        if not obj.foyer:
            return 0.0
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        total = obj.foyer.consommations.filter(
            timestamp__gte=today,
            timestamp__lt=tomorrow
        ).aggregate(Sum('kwh'))['kwh__sum'] or 0.0
        return round(float(total), 2)
    
    def get_consommation_semaine(self, obj):
        if not obj.foyer:
            return 0.0
        week_ago = timezone.now() - timedelta(days=7)
        total = obj.foyer.consommations.filter(
            timestamp__gte=week_ago
        ).aggregate(Sum('kwh'))['kwh__sum'] or 0.0
        return round(float(total), 2)
    
    def get_anomalies_actives(self, obj):
        if not obj.foyer:
            return 0
        return Anomalie.objects.filter(
            consommation__foyer=obj.foyer,
            statut__in=['NOUVELLE', 'CONSULTEE']
        ).count()
    
    def get_alertes_non_acquittees(self, obj):
        if not obj.foyer:
            return 0
        return Alerte.objects.filter(
            anomalie__consommation__foyer=obj.foyer,
            acquittee=False
        ).count()
    
    def get_derniere_mesure(self, obj):
        if not obj.foyer:
            return None
        try:
            derniere = obj.foyer.consommations.latest('timestamp')
            return derniere.timestamp
        except Consommation.DoesNotExist:
            return None


class UserResidentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer détaillé pour un résident (avec toutes ses données).
    Utilisé par admin/residents/{id}/.
    """
    foyer = FoyerDetailSerializer(read_only=True)
    consommation_jour = serializers.SerializerMethodField()
    consommation_semaine = serializers.SerializerMethodField()
    consommation_mois = serializers.SerializerMethodField()
    cout_estime_mois = serializers.SerializerMethodField()
    anomalies_actives = serializers.SerializerMethodField()
    alertes_non_acquittees = serializers.SerializerMethodField()
    dernieres_consommations = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'foyer', 'consommation_jour', 'consommation_semaine', 'consommation_mois',
            'cout_estime_mois', 'anomalies_actives', 'alertes_non_acquittees',
            'dernieres_consommations'
        ]
    
    def get_consommation_jour(self, obj):
        if not obj.foyer:
            return 0.0
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        total = obj.foyer.consommations.filter(
            timestamp__gte=today,
            timestamp__lt=tomorrow
        ).aggregate(Sum('kwh'))['kwh__sum'] or 0.0
        return round(float(total), 2)
    
    def get_consommation_semaine(self, obj):
        if not obj.foyer:
            return 0.0
        week_ago = timezone.now() - timedelta(days=7)
        total = obj.foyer.consommations.filter(
            timestamp__gte=week_ago
        ).aggregate(Sum('kwh'))['kwh__sum'] or 0.0
        return round(float(total), 2)
    
    def get_consommation_mois(self, obj):
        if not obj.foyer:
            return 0.0
        month_ago = timezone.now() - timedelta(days=30)
        total = obj.foyer.consommations.filter(
            timestamp__gte=month_ago
        ).aggregate(Sum('kwh'))['kwh__sum'] or 0.0
        return round(float(total), 2)
    
    def get_cout_estime_mois(self, obj):
        consommation_mois = self.get_consommation_mois(obj)
        tarif_kwh = 2.5  # 2.5 DH par kWh
        return round(consommation_mois * tarif_kwh, 2)
    
    def get_anomalies_actives(self, obj):
        if not obj.foyer:
            return []
        anomalies = Anomalie.objects.filter(
            consommation__foyer=obj.foyer,
            statut__in=['NOUVELLE', 'CONSULTEE']
        ).values('id', 'severite', 'statut', 'consommation__timestamp')
        return list(anomalies)
    
    def get_alertes_non_acquittees(self, obj):
        if not obj.foyer:
            return []
        alertes = Alerte.objects.filter(
            anomalie__consommation__foyer=obj.foyer,
            acquittee=False
        ).values('id', 'statut', 'created_at')
        return list(alertes)
    
    def get_dernieres_consommations(self, obj):
        if not obj.foyer:
            return []
        consommations = obj.foyer.consommations.order_by('-timestamp')[:48]
        return [
            {'timestamp': c.timestamp, 'kwh': c.kwh}
            for c in consommations
        ]


class DashboardSerializer(serializers.Serializer):
    """
    Serializer pour le dashboard résident.
    Retourne les KPIs du foyer connecté.
    """
    consommation_actuelle = serializers.FloatField()
    consommation_jour = serializers.FloatField()
    consommation_semaine = serializers.FloatField()
    consommation_mois = serializers.FloatField()
    cout_estime_jour = serializers.FloatField()
    cout_estime_semaine = serializers.FloatField()
    cout_estime_mois = serializers.FloatField()
    variation_jour = serializers.FloatField()
    variation_semaine = serializers.FloatField()
    alertes_actives = serializers.IntegerField()
    anomalies_actives = serializers.IntegerField()
    foyer = FoyerDetailSerializer(read_only=True)
    points_graphique = serializers.ListField()


class ConsommationDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour historique résident."""
    foyer_numero = serializers.CharField(source='foyer.numero_foyer', read_only=True)
    
    class Meta:
        model = Consommation
        fields = ['id', 'timestamp', 'kwh', 'anomaly_label', 'temperature', 'foyer_numero']
        read_only_fields = ['timestamp']


class AlerteResidentSerializer(serializers.ModelSerializer):
    """Serializer pour les alertes du résident."""
    anomalie = AnomalieSerializer(read_only=True)
    
    class Meta:
        model = Alerte
        fields = ['id', 'anomalie', 'statut', 'acquittee', 'created_at', 'consultee_at', 'acquittee_at']
        read_only_fields = ['created_at', 'consultee_at', 'acquittee_at']


# ============================================================================
# NEW SERIALIZERS FOR SMARTMETER CAHIER DES CHARGES
# ============================================================================

class ConsumptionReadingSerializer(serializers.ModelSerializer):
    """
    Serializer pour les lectures de consommation (ConsumptionReading).
    Utilisé par les endpoints /api/resident/readings/ et /api/admin/dashboard/
    """
    resident_email = serializers.CharField(source='resident.email', read_only=True)
    
    class Meta:
        model = ConsumptionReading
        fields = [
            'id',
            'resident',
            'resident_email',
            'meter_id',
            'timestamp',
            'consumption_kwh',
            'cost_estimate',
            'tariff_type',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['resident', 'created_at', 'updated_at']


class ResidentSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple pour afficher les résidents gérés par un admin.
    Inclut le meter_id du premier compteur associé au résident.
    """
    meter_id = serializers.SerializerMethodField()
    
    def get_meter_id(self, obj):
        """Récupère le meter_id du premier enregistrement de consommation du résident."""
        reading = obj.consumption_readings.first()
        return reading.meter_id if reading else None
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'meter_id']
        read_only_fields = fields


class AdminDashboardResidentSerializer(serializers.Serializer):
    """
    Serializer pour afficher les données agrégées d'un résident dans le dashboard admin.
    """
    email = serializers.EmailField()
    meter_id = serializers.CharField()
    total_consumption_kwh = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_cost_estimate = serializers.DecimalField(max_digits=10, decimal_places=2)


class AdminDashboardConsumptionDaySerializer(serializers.Serializer):
    """
    Serializer pour afficher la consommation agrégée par jour.
    """
    date = serializers.DateField()
    total_consumption_kwh = serializers.DecimalField(max_digits=10, decimal_places=2)


class AdminDashboardSerializer(serializers.Serializer):
    """
    Serializer pour le dashboard admin.
    Retourne les données agrégées de tous les résidents gérés par l'admin.
    """
    admin_email = serializers.EmailField()
    total_residents = serializers.IntegerField()
    total_consumption_kwh = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_cost_estimate = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_consumption_per_resident = serializers.DecimalField(max_digits=10, decimal_places=2)
    residents = AdminDashboardResidentSerializer(many=True)
    consumption_by_day = AdminDashboardConsumptionDaySerializer(many=True)


class ResidentDashboardReadingSerializer(serializers.ModelSerializer):
    """
    Serializer pour afficher les readings du résident.
    """
    class Meta:
        model = ConsumptionReading
        fields = ['id', 'meter_id', 'timestamp', 'consumption_kwh', 'cost_estimate', 'tariff_type']
        read_only_fields = fields


class ResidentDashboardSerializer(serializers.Serializer):
    """
    Serializer pour le dashboard résident.
    Retourne uniquement les données du résident connecté.
    """
    resident_email = serializers.EmailField()
    meter_id = serializers.CharField()
    total_consumption_kwh = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_cost_estimate = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_daily_consumption = serializers.DecimalField(max_digits=10, decimal_places=2)
    readings = ResidentDashboardReadingSerializer(many=True)


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'endpoint /api/auth/me/
    Retourne les informations de l'utilisateur connecté.
    """
    managed_by_email = serializers.CharField(source='managed_by.email', read_only=True, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'role',
            'managed_by',
            'managed_by_email',
            'is_active',
        ]
        read_only_fields = fields

