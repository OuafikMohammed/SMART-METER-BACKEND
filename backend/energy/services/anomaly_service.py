"""
Service de détection et classification des anomalies.
RG7, RG8, RG9, RG10: Détection, score Hugging Face, statuts, alertes.
"""
import logging
import requests
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail

from energy.models import Anomalie, Alerte, Consommation

logger = logging.getLogger(__name__)


def obtenir_score_huggingface(kwh_value: float) -> float:
    """
    Appelle l'API Hugging Face pour obtenir un score de confiance (0.0 → 1.0).
    
    RG8: Score Hugging Face de [0.0, 1.0]
    
    Args:
        kwh_value: Valeur de consommation en kWh
        
    Returns:
        float: Score de confiance entre 0.0 et 1.0
        En cas d'erreur (timeout, rate limit, API down), retourne 0.5
    """
    try:
        # Vérifier que la clé API Hugging Face est configurée
        hf_api_key = getattr(settings, 'HUGGINGFACE_API_KEY', None)
        if not hf_api_key:
            logger.warning("HUGGINGFACE_API_KEY non configurée en settings")
            return 0.5
        
        # Constructeur du prompt pour classification texte
        prompt = f"Electricity consumption spike detected: {kwh_value} kWh unusually high"
        
        # URL de l'API Hugging Face
        api_url = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
        
        # Headers avec authentification
        headers = {
            "Authorization": f"Bearer {hf_api_key}",
            "Content-Type": "application/json"
        }
        
        # Payload pour l'API
        payload = {
            "inputs": prompt,
            "options": {"wait_for_model": True}  # Attendre si le modèle est chargé
        }
        
        # Appel à l'API (timeout 15s)
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=15
        )
        
        # Vérifier le code de statut
        if response.status_code != 200:
            logger.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            return 0.5
        
        # Parser la réponse
        result = response.json()
        
        # Extraire le score du label POSITIVE
        # Format attendu: [{"label": "POSITIVE", "score": 0.95}, {"label": "NEGATIVE", "score": 0.05}]
        if isinstance(result, list) and len(result) > 0:
            scores = {item['label']: item['score'] for item in result}
            # Retourner le score POSITIVE (ou 0.5 par défaut)
            return scores.get('POSITIVE', 0.5)
        
        logger.warning(f"Format de réponse Hugging Face inattendu: {result}")
        return 0.5
        
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de l'appel Hugging Face API")
        return 0.5
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'appel Hugging Face API: {e}")
        return 0.5
    except Exception as e:
        logger.error(f"Erreur inattendue dans obtenir_score_huggingface: {e}")
        return 0.5


def classifier_severite(score: float) -> str:
    """
    Classe la sévérité d'une anomalie basée sur le score Hugging Face.
    
    RG8: Classification des sévérités
    - warning: score < 0.6
    - high: 0.6 <= score <= 0.8
    - critical: score > 0.8
    
    Args:
        score: Score de confiance [0.0, 1.0]
        
    Returns:
        str: Sévérité 'warning', 'high' ou 'critical'
    """
    if score > 0.8:
        return 'HAUTE'  # critical
    elif score >= 0.6:
        return 'HAUTE'  # high (mapped to HAUTE)
    else:
        return 'MOYENNE'  # warning (mapped to MOYENNE)


def traiter_nouvelles_anomalies() -> dict:
    """
    Traite les nouvelles anomalies détectées dans la BD.
    
    RG7: Détecte les anomalies depuis anomaly_label=1 (non encore traitées)
    RG8: Appelle Hugging Face pour obtenir le score de confiance
    RG9: Crée les anomalies avec statut 'NOUVELLE'
    RG10: Crée les alertes correspondantes
    RG11: Envoie des emails aux admins
    
    Returns:
        dict: Statistiques du traitement {created: N, errors: N}
    """
    results = {
        'created': 0,
        'errors': 0,
        'failed_anomalies': []
    }
    
    try:
        # RG7: Requête pour les consommations anormales non encore traitées
        consommations_anormales = Consommation.objects.filter(
            anomaly_label=1,  # Label d'anomalie du dataset
            anomalie__isnull=True  # Pas encore traitée
        ).select_related('foyer')
        
        logger.info(f"Trouvé {consommations_anormales.count()} anomalies à traiter")
        
        for consommation in consommations_anormales:
            try:
                # RG8: Obtenir le score Hugging Face
                score = obtenir_score_huggingface(consommation.kwh)
                
                # Classifier la sévérité
                severite = classifier_severite(score)
                
                # RG9: Créer l'Anomalie avec statut 'NOUVELLE'
                anomalie = Anomalie.objects.create(
                    consommation=consommation,
                    score_confiance=score,
                    severite=severite,
                    statut='NOUVELLE',
                    description=f"Anomalie détectée: consommation {consommation.kwh} kWh avec score {score:.2%}"
                )
                
                # RG10: Créer l'Alerte
                alerte = Alerte.objects.create(
                    anomalie=anomalie,
                    statut='NOUVELLE'
                )
                
                # RG11: Envoyer email à l'admin
                envoyer_email_alerte(anomalie)
                
                results['created'] += 1
                logger.info(f"Anomalie créée: {anomalie.id} (score: {score:.2%}, severite: {severite})")
                
            except Exception as e:
                results['errors'] += 1
                results['failed_anomalies'].append({
                    'consommation_id': consommation.id,
                    'error': str(e)
                })
                logger.error(f"Erreur lors du traitement de consommation {consommation.id}: {e}")
        
        logger.info(f"Traitement anomalies terminé: {results['created']} créées, {results['errors']} erreurs")
        return results
        
    except Exception as e:
        logger.error(f"Erreur critique dans traiter_nouvelles_anomalies: {e}")
        results['errors'] += 1
        return results


def envoyer_email_alerte(anomalie: Anomalie) -> bool:
    """
    Envoie un email d'alerte aux admins quand une anomalie est détectée.
    
    RG11: Notification email automatique en moins de 5 minutes
    
    Args:
        anomalie: Instance Anomalie
        
    Returns:
        bool: True si email envoyé, False sinon
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Récupérer tous les admins
        admins = User.objects.filter(role='ADMIN').values_list('email', flat=True)
        
        if not admins:
            logger.warning("Aucun admin trouvé pour recevoir l'alerte")
            return False
        
        # Construire le contenu de l'email
        foyer = anomalie.consommation.foyer
        timestamp = anomalie.consommation.timestamp
        kwh = anomalie.consommation.kwh
        score_percent = f"{anomalie.score_confiance * 100:.1f}%"
        severite = anomalie.get_severite_display()
        
        subject = f"⚠️ [{anomalie.severite}] Anomalie Foyer {foyer.numero_foyer} — SmartMeter"
        
        message = f"""
Nouvelle anomalie détectée sur SmartMeter

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DÉTAILS DE L'ANOMALIE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Foyer : {foyer.numero_foyer}
Adresse : {foyer.adresse}, {foyer.code_postal} {foyer.ville}

Timestamp : {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Consommation : {kwh} kWh
Score Hugging Face : {score_percent}
Sévérité : {severite}
Statut : NOUVELLE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Veuillez consulter l'interface d'administration pour traiter cette alerte.

SmartMeter Platform
"""
        
        # Envoyer l'email
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@smartmeter.local'),
            recipient_list=list(admins),
            fail_silently=False
        )
        
        logger.info(f"Email d'alerte envoyé pour anomalie {anomalie.id} à {len(admins)} admin(s)")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi d'email pour anomalie {anomalie.id}: {e}")
        return False
