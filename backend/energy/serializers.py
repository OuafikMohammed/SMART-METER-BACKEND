"""REST API serializers pour l'app energy."""
from rest_framework import serializers

from .models import ActionLog, Alerte, Anomalie, Consommation, ConversationIA, Foyer


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
