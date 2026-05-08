"""
Helper pour tracer les actions utilisateur (RG20).
Toutes les actions importantes doivent être loggées via log_action().
"""
from .models import ActionLog
import json


def log_action(user, action, details=None, ip_address=None):
    """
    Enregistre une action utilisateur dans le journal d'audit (RG20).
    
    Args:
        user: L'utilisateur qui effectue l'action
        action (str): Type d'action (ex: 'CONSULTER_CONSOMMATION')
        details (dict): Détails supplémentaires (ex: {'foyer_id': 1})
        ip_address (str): Adresse IP optionnelle de l'utilisateur
    
    Returns:
        ActionLog: L'enregistrement créé ou None en cas d'erreur
    
    Exemple:
        log_action(
            user=request.user,
            action='ACQUITTER_ANOMALIE',
            details={'anomalie_id': 5, 'foyer_id': 1},
            ip_address=get_client_ip(request)
        )
    """
    try:
        action_log = ActionLog.objects.create(
            utilisateur=user,
            action=action,
            details=details or {},
            ip_address=ip_address
        )
        return action_log
    except Exception as e:
        # En production, logger l'erreur mais ne pas lever l'exception
        print(f"Erreur lors de l'enregistrement de l'action: {str(e)}")
        return None


def get_client_ip(request):
    """
    Récupère l'adresse IP du client à partir de la requête.
    Prend en compte les proxies (X-Forwarded-For, X-Real-IP).
    
    Args:
        request: L'objet requête Django
    
    Returns:
        str: L'adresse IP du client
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
