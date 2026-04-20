"""
Modèles ORM pour l'application Energy (SmartMeter).
7 modèles: Foyer, Consommation, Anomalie, Alerte, ConversationIA, ActionLog + User (dans app users).
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Foyer(models.Model):
    """
    Représente un foyer (ménage) avec ses appareils et sa consommation électrique.
    Un foyer peut avoir plusieurs résidents (RG3).
    """
    
    # Identifiant unique du foyer
    numero_foyer = models.CharField(max_length=50, unique=True, db_index=True)
    
    # Localisation du foyer
    adresse = models.TextField()
    code_postal = models.CharField(max_length=10)
    ville = models.CharField(max_length=100)
    
    # Informations technique
    puissance_souscrite = models.FloatField(help_text="Puissance souscrite en kW")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'energy_foyer'
        verbose_name = 'Foyer'
        verbose_name_plural = 'Foyers'
        ordering = ['numero_foyer']
    
    def __str__(self):
        return f"Foyer {self.numero_foyer} - {self.adresse}"


class Consommation(models.Model):
    """
    Enregistre la consommation électrique pour chaque foyer.
    Timestamp: moment de la mesure, kwh: consommation en kWh.
    anomaly_label: label ML détecté, temperature: température ambiante.
    
    Respecte RG3 : accès selon le rôle (RESIDENT voir son foyer, ADMIN tout voir).
    """
    
    # Clé étrangère vers le foyer
    foyer = models.ForeignKey(
        Foyer,
        on_delete=models.CASCADE,
        related_name='consommations',
        db_index=True
    )
    
    # Mesure de consommation
    timestamp = models.DateTimeField(db_index=True, help_text="Heure de la mesure")
    kwh = models.FloatField(help_text="Consommation en kWh")
    
    # Détection anomalie (ML)
    anomaly_label = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Label d'anomalie détecté par ML (ex: 'pic', 'anomalie_consommation')"
    )
    
    # Contexte
    temperature = models.FloatField(null=True, blank=True, help_text="Température ambiante en °C")
    
    class Meta:
        db_table = 'energy_consommation'
        verbose_name = 'Consommation'
        verbose_name_plural = 'Consommations'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['foyer', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Consommation {self.foyer.numero_foyer} - {self.timestamp}"


class Anomalie(models.Model):
    """
    Anomalie détectée sur une consommation.
    Liée à une Consommation, avec score de confiance, sévérité et statut.
    
    Respecte RG3 : accès selon le rôle.
    """
    
    SEVERITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('MOYENNE', 'Moyenne'),
        ('HAUTE', 'Haute'),
        ('CRITIQUE', 'Critique'),
    ]
    
    STATUT_CHOICES = [
        ('NOUVELLE', 'Nouvelle'),
        ('CONSULTEE', 'Consultée'),
        ('ACQUITTEE', 'Acquittée'),
    ]
    
    # Lien vers la consommation
    consommation = models.OneToOneField(
        Consommation,
        on_delete=models.CASCADE,
        related_name='anomalie',
        db_index=True
    )
    
    # Score de confiance
    score_confiance = models.FloatField(
        help_text="Score de confiance de l'anomalie [0.0, 1.0]",
        validators=[lambda x: 0 <= x <= 1]
    )
    
    # Sévérité et statut
    severite = models.CharField(max_length=20, choices=SEVERITE_CHOICES, default='MOYENNE')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='NOUVELLE')
    
    # Description
    description = models.TextField(null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'energy_anomalie'
        verbose_name = 'Anomalie'
        verbose_name_plural = 'Anomalies'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['statut', '-created_at']),
        ]
    
    def __str__(self):
        return f"Anomalie {self.get_severite_display()} - {self.consommation.foyer.numero_foyer}"


class Alerte(models.Model):
    """
    Alerte générée à partir d'une Anomalie.
    Peut être acquittée par l'utilisateur.
    """
    
    # Lien vers l'anomalie
    anomalie = models.OneToOneField(
        Anomalie,
        on_delete=models.CASCADE,
        related_name='alerte',
        db_index=True
    )
    
    # Statut d'acquittement
    acquittee = models.BooleanField(default=False)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    acquittee_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'energy_alerte'
        verbose_name = 'Alerte'
        verbose_name_plural = 'Alertes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['acquittee', '-created_at']),
        ]
    
    def __str__(self):
        return f"Alerte {self.get_acquittee_display()} - Anomalie {self.anomalie.id}"


class ConversationIA(models.Model):
    """
    Conversation entre utilisateur et IA pour analyser les consommations.
    Chaque conversation est liée à un utilisateur.
    
    Respecte RG20 : actions tracées (conversation enregistrée).
    """
    
    # Utilisateur qui pose la question
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations_ia',
        db_index=True
    )
    
    # Contenu de l'échange
    question = models.TextField()
    reponse = models.TextField()
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'energy_conversationIA'
        verbose_name = 'Conversation IA'
        verbose_name_plural = 'Conversations IA'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['utilisateur', '-timestamp']),
        ]
    
    def __str__(self):
        return f"Conversation {self.utilisateur.username} - {self.timestamp}"


class ActionLog(models.Model):
    """
    Journal d'audit des actions utilisateur (RG20).
    Enregistre toutes les actions importantes (consultation, modification, etc.).
    
    Respecte RG20 : actions tracées avec user, action, details et timestamp.
    """
    
    # Utilisateur effectuant l'action
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='action_logs',
        db_index=True
    )
    
    # Type d'action
    action = models.CharField(
        max_length=100,
        help_text="Type d'action (ex: 'CONSULTER_CONSOMMATION', 'ACQUITTER_ANOMALIE')"
    )
    
    # Détails de l'action
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Détails supplémentaires en JSON (foyer_id, anomalie_id, etc.)"
    )
    
    # Timestamp de l'action
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Adresse IP de l'utilisateur (optionnel)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'energy_actionlog'
        verbose_name = 'Journal d\'action'
        verbose_name_plural = 'Journaux d\'actions'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['utilisateur', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.action} - {self.timestamp}"
