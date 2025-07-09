from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from functools import wraps
from mlunch.core.services.commande_service import CommandeService
from mlunch.core.models import Commande
import json

def authentification_requise(view_func):
    """Décorateur pour vérifier l'authentification du client"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('client_id'):
            return redirect('connexion')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@authentification_requise
def mes_commandes(request):
    """Liste des commandes du client connecté"""
    client_id = request.session.get('client_id')
    commandes_data = CommandeService.get_commandes_by_client(client_id)

    if isinstance(commandes_data, dict) and 'error' in commandes_data:
        commandes_data = []

    return render(request, 'frontoffice/mes_commandes.html', {
        'commandes': commandes_data
    })

@authentification_requise
def commandes_en_cours(request):
    """Commandes en cours du client connecté"""
    client_id = request.session.get('client_id')
    commandes = CommandeService.get_commandes_en_cours(client_id)

    if isinstance(commandes, dict) and 'error' in commandes:
        commandes = []

    return render(request, 'frontoffice/commandes_en_cours.html', {
        'commandes': commandes,
        'nb_commandes': len(commandes)
    })

@authentification_requise
def detail_commande(request, commande_id):
    """Détail d'une commande spécifique"""
    data = CommandeService.get_commande_detail(commande_id)

    if "error" in data:
        return render(request, 'frontoffice/detail_commande.html', {
            'error': data["error"]
        })

    return render(request, 'frontoffice/detail_commande.html', {
        'commande': data['commande'],
        'repas': data['repas'],
        'statut': data['statut'],
        'total': data['total']
    })

@authentification_requise
def historique_commandes(request):
    """Historique complet des commandes du client"""
    client_id = request.session.get('client_id')
    historique = CommandeService.get_historique_commandes(client_id)

    if isinstance(historique, dict) and 'error' in historique:
        historique = []

    return render(request, 'frontoffice/historique_commandes.html', {
        'commandes': historique,
        'nb_commandes': len(historique)
    })

@csrf_exempt
@require_http_methods(["POST"])
@authentification_requise
def annuler_commande(request, commande_id):
    """Annuler une commande"""
    try:
        client_id = request.session.get('client_id')
        success, message = CommandeService.annuler_commande(commande_id, client_id)

        return JsonResponse({
            'success': success,
            'message': message
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
@authentification_requise
def reorder_commande(request, commande_id):
    """Repasser une commande identique"""
    try:
        client_id = request.session.get('client_id')
        success, message = CommandeService.reorder_commande(commande_id, client_id)

        return JsonResponse({
            'success': success,
            'message': message
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })
