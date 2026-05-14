"""
Permissions personnalisées pour SmartMeter.
Respecte RG3 : contrôle d'accès selon le rôle.

- EstAdmin: vérifier que l'utilisateur est administrateur
- EstResident: vérifier que l'utilisateur est résident
"""
from rest_framework.permissions import BasePermission


class EstAdmin(BasePermission):
    """
    Permission personnalisée : vérifier que l'utilisateur est administrateur.
    Respecte RG3 : contrôle d'accès par rôle ADMIN.
    """
    
    message = "Seuls les administrateurs peuvent accéder à cette ressource."
    
    def has_permission(self, request, view):
        """Vérifie si l'utilisateur est authentifié et administrateur."""
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class EstResident(BasePermission):
    """
    Permission personnalisée : vérifier que l'utilisateur est résident.
    Respecte RG3 : contrôle d'accès par rôle RESIDENT.
    """
    
    message = "Seuls les résidents peuvent accéder à cette ressource."
    
    def has_permission(self, request, view):
        """Vérifie si l'utilisateur est authentifié et résident."""
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'RESIDENT'
        )


class EstProprietaireFoyer(BasePermission):
    """
    Permission d'objet : vérifier que l'utilisateur est propriétaire du foyer.
    
    Respecte RG3 : 
    - ADMIN peut accéder à tous les foyers
    - RESIDENT ne peut accéder qu'à son foyer
    """
    
    message = "Vous n'avez pas accès à ce foyer."
    
    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur a accès au foyer.
        obj peut être un Foyer, Consommation, Anomalie ou Alerte.
        """
        # ADMIN a accès à tout
        if request.user.role == 'ADMIN':
            return True
        
        # Pour RESIDENT, récupérer le foyer
        if hasattr(obj, 'foyer'):
            foyer = obj.foyer
        else:
            foyer = obj
        
        # RESIDENT ne peut accéder qu'à son propre foyer
        return (
            request.user.role == 'RESIDENT' and
            request.user.foyer_id == foyer.id
        )


class IsAdminRole(BasePermission):
    """
    Autorise uniquement les utilisateurs avec rôle ADMIN.
    Utilisé pour les endpoints admin du Cahier des Charges.
    """
    message = "Seuls les administrateurs peuvent accéder à cette ressource."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'ADMIN'
        )


class IsResidentRole(BasePermission):
    """
    Autorise uniquement les utilisateurs avec rôle RESIDENT.
    Utilisé pour les endpoints résident du Cahier des Charges.
    """
    message = "Seuls les résidents peuvent accéder à cette ressource."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'RESIDENT'
        )


class CanViewConsumptionReading(BasePermission):
    """
    Permissions pour les lectures de consommation (ConsumptionReading):
    - ADMIN : peut voir les lectures de ses résidents seulement
    - RESIDENT : peut voir uniquement ses propres lectures
    """
    message = "Vous n'avez pas accès à cette lecture de consommation."
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            # Admin peut voir les lectures des résidents qu'il gère
            return obj.resident.managed_by == request.user
        elif request.user.role == 'RESIDENT':
            # Résident voit uniquement ses propres lectures
            return obj.resident == request.user
        return False

