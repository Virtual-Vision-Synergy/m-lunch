from django.shortcuts import render
from mlunch.core.services.commande_service import CommandeService
import logging

logger = logging.getLogger(__name__)

def index(request):
    """Page d'accueil du backoffice avec le dashboard principal"""
    logger.info("=== DÉBUT INDEX VIEW ===")

    try:
        logger.info("Récupération des commandes en attente...")
        commandes_en_attente = CommandeService.get_commandes_en_attente()
        logger.info(f"Nombre de commandes récupérées: {len(commandes_en_attente) if isinstance(commandes_en_attente, list) else 'Erreur'}")

        if isinstance(commandes_en_attente, list):
            for i, commande in enumerate(commandes_en_attente):
                logger.info(f"Commande {i+1}: ID={commande.get('id', 'N/A')}, Client={commande.get('client', 'N/A')}")
        else:
            logger.error(f"Erreur lors de la récupération des commandes: {commandes_en_attente}")

        return render(request, 'backoffice/index.html', {
            'commandes_en_attente': commandes_en_attente
        })

    except Exception as e:
        logger.error(f"Exception dans index view: {str(e)}")
        return render(request, 'backoffice/index.html', {
            'commandes_en_attente': []
        })
