"""
Service IA pour l'assistant conversationnel SmartMeter.

Fournit:
1. Récupération du contexte MySQL (consommation du foyer)
2. Intégration Nvidia/OpenAI API (LLaMA 3.1 Nemotron)
3. Génération de réponses IA en français
"""

import logging
import os
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Max, Count
from django.conf import settings

from energy.models import Consommation, Anomalie

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


def appeler_nvidia(prompt: str) -> str:
    """
    Appelle l'API Nvidia pour générer une réponse IA.
    
    Utilise LLaMA 3.1 Nemotron via OpenAI compatible API.
    
    Args:
        prompt: Prompt complète avec contexte
        
    Returns:
        str: Réponse générée en français, ou message d'erreur gracieux
        
    Example:
        >>> reponse = appeler_nvidia("Quelle est ma consommation moyenne?")
        >>> print(reponse)
        "D'après vos données, votre consommation moyenne..."
    """
    # Graceful mode: si pas de clé API ou openai non disponible, retourner réponse par défaut
    if not NVIDIA_API_KEY or not OPENAI_AVAILABLE:
        logger.warning("Nvidia API key ou openai module non disponibles, mode graceful")
        return (
            "Je suis en mode démo. Pour des recommandations personnalisées, "
            "configurez votre clé Nvidia API dans les variables d'environnement."
        )
    
    try:
        # Créer client OpenAI pointant vers Nvidia
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=NVIDIA_API_KEY
        )
        
        # Appeler le modèle
        response = client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un assistant intelligent pour l'analyse de consommation électrique. Réponds en français, de manière concise et utile."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300,
            top_p=0.9
        )
        
        # Extraire la réponse
        generated_text = response.choices[0].message.content.strip()
        logger.info(f"Réponse Nvidia reçue: {len(generated_text)} chars")
        return generated_text
        
    except Exception as e:
        logger.error(f"Erreur lors de l'appel Nvidia API: {str(e)}")
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
        
        # Appeler Nvidia API
        reponse = appeler_nvidia(prompt)
        
        logger.info(f"Réponse IA générée pour foyer {foyer_id}")
        return reponse
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération de réponse IA: {str(e)}")
        return "Désolé, une erreur s'est produite lors de la génération de la réponse."
