"""
REST API Serializers pour l'app energy
"""
from rest_framework import serializers
from energy.models import Foyer, Consommation, Anomalie, Alerte, ConversationIA, ActionLog


class FoyerSerializer(serializers.ModelSerializer):
    """Serializer pour les Foyers"""
    utilisateurs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Foyer
        fields = ['id', 'numero_foyer', 'adresse', 'code_postal', 'ville', 
                  'puissance_souscrite', 'is_active', 'utilisateurs_count', 
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_utilisateurs_count(self, obj):
        return obj.utilisateurs.count()


class ConsommationSerializer(serializers.ModelSerializer):
    """Serializer pour les Consommations"""
    foyer_numero = serializers.CharField(source='foyer.numero_foyer', read_only=True)
    
    class Meta:
        model = Consommation
        fields = ['id', 'foyer', 'foyer_numero', 'timestamp', 'kwh', 
                  'anomaly_label', 'temperature']
        read_only_fields = ['timestamp']


class AnomalieSerializer(serializers.ModelSerializer):
    """Serializer pour les Anomalies"""
    consommation_kwh = serializers.FloatField(source='consommation.kwh', read_only=True)
    
    class Meta:
        model = Anomalie
        fields = ['id', 'consommation', 'consommation_kwh', 'score_confiance', 
                  'severite', 'statut', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AlerteSerializer(serializers.ModelSerializer):
    """Serializer pour les Alertes"""
    anomalie_severite = serializers.CharField(source='anomalie.get_severite_display', read_only=True)
    
    class Meta:
        model = Alerte
        fields = ['id', 'anomalie', 'anomalie_severite', 'acquittee', 
                  'created_at', 'acquittee_at']


class ConversationIASerializer(serializers.ModelSerializer):
    """Serializer pour les Conversations IA"""
    utilisateur_username = serializers.CharField(source='utilisateur.username', read_only=True)
    
    class Meta:
        model = ConversationIA
        fields = ['id', 'utilisateur', 'utilisateur_username', 'question', 
                  'reponse', 'timestamp']
        read_only_fields = ['timestamp']


class ActionLogSerializer(serializers.ModelSerializer):
    """Serializer pour les ActionLogs (audit trail)"""
    utilisateur_username = serializers.CharField(source='utilisateur.username', read_only=True)
    
    class Meta:
        model = ActionLog
        fields = ['id', 'utilisateur', 'utilisateur_username', 'action', 
                  'details', 'timestamp', 'ip_address']
        read_only_fields = ['timestamp', 'utilisateur', 'utilisateur_username', 'ip_address']
