"""
Service IA pour l'assistant conversationnel SmartMeter.

Fournit:
1. Récupération du contexte MySQL (consommation du foyer)
2. Intégration Hugging Face (Mistral ou Flan-T5)
3. Génération de réponses IA en français
"""

import logging
import requests
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Max, Count
from django.conf import settings

from energy.models import Consommation, Anomalie

logger = logging.getLogger(__name__)

# Configuration Hugging Face
HUGGINGFACE_API_KEY = getattr(settings, 'HUGGINGFACE_API_KEY', None)
HF_API_URL = "https://api-inference.huggingface.co/models"
HF_MODEL_PRIMARY = "mistralai/Mistral-7B-Instruct-v0.1"
HF_MODEL_FALLBACK = "google/flan-t5-large"


def construire_contexte_consommation(foyer_id: int) -> str:
    """
    Construit un contexte contextuel à partir des données MySQL du foyer.
    
    Agrège depuis MySQL:
    - Consommation totale de la semaine
    - Consommation moyenne quotidienne
    - Pic de consommation
    - Nombre d'anomalies détectées
    
    Args:
        foyer_id: ID du foyer
        
    Returns:
        str: Contexte formaté en français pour l'IA
        
    Example:
        >>> contexte = construire_contexte_consommation(1)
        >>> print(contexte)
        "Au cours des 7 derniers jours, votre foyer a consommé 150 kWh..."
    """
    try:
        # Calculer les dates
        date_fin = timezone.now()
        date_debut = date_fin - timedelta(days=7)
        
        # Agrégation des données de consommation
        stats = Consommation.objects.filter(
            foyer_id=foyer_id,
            timestamp__gte=date_debut,
            timestamp__lte=date_fin
        ).aggregate(
            kwh_total=Sum('kwh'),
            kwh_moyen=Avg('kwh'),
            kwh_max=Max('kwh')
        )
        
        # Compter les anomalies
        anomalies_count = Anomalie.objects.filter(
            consommation__foyer_id=foyer_id,
            consommation__timestamp__gte=date_debut,
            consommation__timestamp__lte=date_fin,
            consommation__anomaly_label__isnull=False
        ).count()
        
        # Formatter les valeurs
        kwh_total = round(stats.get('kwh_total', 0) or 0, 2)
        kwh_moyen = round(stats.get('kwh_moyen', 0) or 0, 2)
        kwh_max = round(stats.get('kwh_max', 0) or 0, 2)
        
        # Construire le contexte
        contexte = (
            f"Contexte de consommation du foyer:\n"
            f"- Consommation totale (7 derniers jours): {kwh_total} kWh\n"
            f"- Consommation moyenne quotidienne: {kwh_moyen} kWh\n"
            f"- Pic de consommation: {kwh_max} kWh\n"
            f"- Anomalies détectées (7 derniers jours): {anomalies_count}\n"
        )
        
        logger.info(f"Contexte construit pour foyer {foyer_id}: {kwh_total} kWh total")
        return contexte
        
    except Exception as e:
        logger.error(f"Erreur lors de la construction du contexte: {str(e)}")
        return "Contexte de consommation: données indisponibles."


def appeler_huggingface(prompt: str, model: str = None) -> str:
    """
    Appelle l'API Hugging Face pour générer une réponse IA.
    
    Utilise Mistral-7B par défaut, fallback sur Flan-T5 en cas d'erreur.
    Accepte aussi directement les prompts sans clé API (mode graceful).
    
    Args:
        prompt: Prompt complète avec contexte
        model: Modèle optionnel (fallback sur PRIMARY si None)
        
    Returns:
        str: Réponse générée en français, ou message d'erreur gracieux
        
    Example:
        >>> reponse = appeler_huggingface("Quelle est ma consommation moyenne?")
        >>> print(reponse)
        "D'après vos données, votre consommation moyenne..."
    """
    if model is None:
        model = HF_MODEL_PRIMARY
    
    # Graceful mode: si pas de clé API, retourner réponse par défaut
    if not HUGGINGFACE_API_KEY:
        logger.warning("Aucune clé HuggingFace API configurée, mode graceful")
        return (
            "Je suis en mode démo. Pour des recommandations personnalisées, "
            "configurez votre clé Hugging Face dans les variables d'environnement."
        )
    
    try:
        url = f"{HF_API_URL}/{model}"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 300,
                "temperature": 0.7,
                "return_full_text": False,
            },
        }
        
        # Appeler l'API avec timeout
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parser la réponse
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get('generated_text', '')
            logger.info(f"Réponse HF reçue ({model}): {len(generated_text)} chars")
            return generated_text.strip()
        
        logger.warning(f"Réponse HF vide ou format inattendu: {result}")
        return "Désolé, je n'ai pas pu générer de réponse. Veuillez réessayer."
        
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de l'appel HuggingFace")
        return "L'IA met trop de temps à répondre. Veuillez réessayer plus tard."
    except requests.exceptions.HTTPError as e:
        logger.error(f"Erreur HTTP HuggingFace: {str(e)}")
        
        # Si erreur 429 (rate limit), utiliser fallback
        if e.response.status_code == 429 and model == HF_MODEL_PRIMARY:
            logger.info(f"Rate limit atteint, tentative avec {HF_MODEL_FALLBACK}")
            return appeler_huggingface(prompt, model=HF_MODEL_FALLBACK)
        
        return "Erreur lors de la communication avec l'IA. Veuillez réessayer."
    except Exception as e:
        logger.error(f"Erreur lors de l'appel HuggingFace: {str(e)}")
        return "Une erreur inattendue s'est produite. Veuillez réessayer."


def generer_reponse_ia(foyer_id: int, question: str) -> str:
    """
    Génère une réponse IA personnalisée basée sur le contexte du foyer.
    
    Processus:
    1. Construire le contexte de consommation depuis MySQL
    2. Créer un prompt complet
    3. Appeler Hugging Face
    4. Retourner la réponse
    
    Args:
        foyer_id: ID du foyer
        question: Question de l'utilisateur
        
    Returns:
        str: Réponse personnalisée en français
        
    Example:
        >>> reponse = generer_reponse_ia(1, "Pourquoi ma consommation a augmenté?")
        >>> print(reponse)
        "Selon vos données, votre consommation a augmenté..."
    """
    try:
        # Construire le contexte
        contexte = construire_contexte_consommation(foyer_id)
        
        # Construire le prompt complet
        prompt = (
            f"{contexte}\n"
            f"Question de l'utilisateur: {question}\n\n"
            f"Répondez en français, de manière concise (max 3 phrases), "
            f"basée sur les données fournies. Donnez des recommandations d'économies d'énergie si pertinent."
        )
        
        logger.info(f"Générant réponse IA pour foyer {foyer_id}")
        
        # Appeler Hugging Face
        reponse = appeler_huggingface(prompt)
        
        logger.info(f"Réponse IA générée pour foyer {foyer_id}")
        return reponse
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération de réponse IA: {str(e)}")
        return "Désolé, une erreur s'est produite lors de la génération de la réponse."
