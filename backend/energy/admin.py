"""Energy admin configuration."""
from django.contrib import admin

from .models import ActionLog, Alerte, Anomalie, Consommation, ConversationIA, Foyer, ConsumptionReading


@admin.register(Foyer)
class FoyerAdmin(admin.ModelAdmin):
    list_display = ('numero_foyer', 'adresse', 'ville', 'puissance_souscrite', 'is_active')
    list_filter = ('is_active', 'ville', 'created_at')
    search_fields = ('numero_foyer', 'adresse', 'ville')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Consommation)
class ConsommationAdmin(admin.ModelAdmin):
    list_display = ('foyer', 'timestamp', 'kwh', 'temperature', 'anomaly_label')
    list_filter = ('foyer', 'timestamp', 'anomaly_label')
    search_fields = ('foyer__numero_foyer',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(Anomalie)
class AnomalieAdmin(admin.ModelAdmin):
    """Admin pour les anomalies (RG7, RG8, RG9)."""
    list_display = (
        'foyer_numero',
        'severite',
        'score_confiance',
        'statut',
        'consultee_at',
        'acquittee_at',
        'created_at',
    )
    list_filter = ('severite', 'statut', 'created_at', 'updated_at')
    search_fields = ('consommation__foyer__numero_foyer',)
    readonly_fields = ('created_at', 'updated_at', 'consultee_at', 'acquittee_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Consommation', {
            'fields': ('consommation',)
        }),
        ('Détails Anomalie (RG7, RG8)', {
            'fields': (
                'score_confiance',
                'severite',
                'description',
            )
        }),
        ('Statut et Transition (RG9)', {
            'fields': (
                'statut',
                'consultee_at',
                'acquittee_at',
            ),
            'description': 'Statut anomalie : NOUVELLE → CONSULTEE → ACQUITTEE'
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def foyer_numero(self, obj):
        """Afficher le numéro du foyer."""
        return obj.consommation.foyer.numero_foyer
    foyer_numero.short_description = 'Foyer'
    
    def score_confiance(self, obj):
        """Afficher le score Hugging Face avec formatage."""
        return f"{obj.score_confiance:.2f}"
    score_confiance.short_description = 'Score HF'


@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    """Admin pour les alertes (RG10, RG11, RG12)."""
    list_display = (
        'foyer_numero',
        'statut',
        'acquittee',
        'created_at',
        'acquittee_at',
    )
    list_filter = ('statut', 'acquittee', 'created_at')
    search_fields = ('anomalie__consommation__foyer__numero_foyer',)
    readonly_fields = ('created_at', 'consultee_at', 'acquittee_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Anomalie', {
            'fields': ('anomalie',)
        }),
        ('Gestion Admin (RG11, RG12)', {
            'fields': (
                'statut',
                'acquittee',
                'consultee_at',
                'acquittee_at',
            ),
            'description': 'L\'administrateur consulte et traite les alertes. Alerte acquittée reste en base (archivage).'
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    actions = ['marquer_consultee', 'acquitter_alertes']
    
    def foyer_numero(self, obj):
        """Afficher le numéro du foyer."""
        return obj.anomalie.consommation.foyer.numero_foyer
    foyer_numero.short_description = 'Foyer'
    
    def marquer_consultee(self, request, queryset):
        """Action admin : Marquer les alertes comme consultées."""
        count = 0
        for alerte in queryset.filter(statut='NOUVELLE'):
            alerte.marquer_consultee()
            count += 1
        self.message_user(request, f'{count} alerte(s) marquée(s) comme consultée(s).')
    marquer_consultee.short_description = 'Marquer comme consultée'
    
    def acquitter_alertes(self, request, queryset):
        """Action admin : Acquitter les alertes (RG12)."""
        count = 0
        for alerte in queryset.filter(acquittee=False):
            alerte.acquitter()
            # Mettre à jour l'anomalie
            alerte.anomalie.marquer_acquittee()
            count += 1
        self.message_user(request, f'{count} alerte(s) acquittée(s) et archivée(s).')
    acquitter_alertes.short_description = 'Acquitter et archiver'


@admin.register(ConversationIA)
class ConversationIAAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'timestamp')
    list_filter = ('utilisateur', 'timestamp')
    search_fields = ('utilisateur__username', 'question')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp', 'utilisateur')
    search_fields = ('utilisateur__username', 'action')
    readonly_fields = ('timestamp', 'utilisateur', 'action', 'details', 'ip_address')
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConsumptionReading)
class ConsumptionReadingAdmin(admin.ModelAdmin):
    """Admin pour les lectures de consommation (Cahier des Charges)."""
    list_display = (
        'resident_email',
        'meter_id',
        'timestamp',
        'consumption_kwh',
        'cost_estimate',
        'tariff_type',
    )
    list_filter = ('timestamp', 'tariff_type', 'meter_id', 'resident')
    search_fields = ('resident__email', 'meter_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Résident', {
            'fields': ('resident',)
        }),
        ('Mesure', {
            'fields': (
                'meter_id',
                'timestamp',
                'consumption_kwh',
                'cost_estimate',
                'tariff_type',
            )
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def resident_email(self, obj):
        """Afficher l'email du résident."""
        return obj.resident.email
    resident_email.short_description = 'Résident'

