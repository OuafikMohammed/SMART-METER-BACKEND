"""
Service de détection et classification des anomalies.
RG7, RG8, RG9, RG10: Détection, score Nvidia API, statuts, alertes.
"""
import logging
import os
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail

from energy.models import Anomalie, Alerte, Consommation

logger = logging.getLogger(__name__)

# Configuration Nvidia API
NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY') or getattr(settings, 'NVIDIA_API_KEY', None)
NVIDIA_MODEL = "nvidia/llama-3.1-nemotron-nano-8b-v1"

# Import OpenAI client (compatible with Nvidia API)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai module not available")


def obtenir_score_nvidia(kwh_value: float) -> float:
    """
    Obtient un score de confiance d'anomalie via Nvidia API.
    
    RG8: Score Nvidia de [0.0, 1.0]
    
    Args:
        kwh_value: Valeur de consommation en kWh
        
    Returns:
        float: Score de confiance entre 0.0 et 1.0
        En cas d'erreur (timeout, API down), retourne 0.5
    """
    # Si pas de clé API ou openai non disponible, retourner score neutre
    if not NVIDIA_API_KEY or not OPENAI_AVAILABLE:
        logger.warning("Nvidia API key ou openai module non disponibles, retour score neutre 0.5")
        return 0.5
    
    try:
        # Créer client OpenAI pointant vers Nvidia
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=NVIDIA_API_KEY
        )
        
        # Prompt pour obtenir un score d'anomalie
        prompt = (
            f"Given an electricity consumption value of {kwh_value} kWh, "
            f"determine if this represents an anomaly on a scale from 0.0 (definitely normal) to 1.0 (definitely anomalous). "
            f"Consider typical household consumption patterns. "
            f"Respond with ONLY a decimal number between 0.0 and 1.0, nothing else."
        )
        
        # Appeler le modèle
        response = client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[
                {"role": "system", "content": "You are an anomaly detection system. Respond with only a decimal score between 0.0 and 1.0."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent scoring
            max_tokens=10
        )
        
        # Extraire et parser le score
        score_text = response.choices[0].message.content.strip()
        try:
            score = float(score_text)
            # Assurer que le score est dans [0.0, 1.0]
            score = max(0.0, min(1.0, score))
            logger.info(f"Score Nvidia obtenu: {score} pour {kwh_value} kWh")
            return score
        except ValueError:
            logger.warning(f"Score Nvidia non parsable: {score_text}")
            return 0.5
        
    except Exception as e:
        logger.error(f"Erreur lors de l'appel Nvidia API: {str(e)}")
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
                # RG8: Obtenir le score Nvidia
                score = obtenir_score_nvidia(consommation.kwh)
                
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
