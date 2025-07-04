from django.shortcuts import render
from mlunch.core.services.commande_service import CommandeService

def index(request):
    """Page d'accueil du backoffice avec le dashboard principal"""
    commandes_en_attente = CommandeService.get_commandes_en_attente()
    return render(request, 'backoffice/index.html', {
        'commandes_en_attente': commandes_en_attente
    })
