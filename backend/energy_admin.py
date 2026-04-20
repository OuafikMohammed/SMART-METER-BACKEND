"""Energy admin configuration"""
from django.contrib import admin
from energy.models import Foyer, Consommation, Anomalie, Alerte, ConversationIA, ActionLog


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
    list_display = ('consommation', 'severite', 'score_confiance', 'statut', 'created_at')
    list_filter = ('severite', 'statut', 'created_at')
    search_fields = ('consommation__foyer__numero_foyer',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ('anomalie', 'acquittee', 'created_at')
    list_filter = ('acquittee', 'created_at')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


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
