import json
from functools import wraps

from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from mlunch.core.models import Client, Restaurant
from mlunch.core.services import CommandeService, PointRecupService, PanierService


def authentification_requise(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('client_id'):
            return HttpResponseRedirect('/connexion/')  # Change to your login URL if different
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def logout_view(request):
    """Déconnexion de l'utilisateur"""
    if 'client_id' in request.session:
        del request.session['client_id']
    return redirect('frontoffice:index')



def mes_commandes(request):
    client_id = request.session.get("client_id")

    commandes_data = CommandeService.get_commandes_by_client(client_id)
    return render(request, 'frontoffice/mes_commandes.html', {
        'commandes': commandes_data
    })


def detail_commande(request, commande_id):
    #commande = get_object_or_404(Commande, id=commande_id)
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





def historique_commandes(request):
    """
    Vue pour afficher l'historique complet des commandes du client
    """
    # Récupérer l'ID du client depuis la session
    client_id = request.session.get('client_id')

    if not client_id:
        return redirect('frontoffice_connexion')

    # Récupérer l'historique via le service
    historique = CommandeService.get_historique_commandes(client_id)

    # Gérer les erreurs
    if isinstance(historique, dict) and 'error' in historique:
        historique = []

    context = {
        'commandes': historique,
        'nb_commandes': len(historique)
    }

    return render(request, 'frontoffice/historique_commandes.html', context)


def commandes_en_cours(request):
    """
    Vue pour afficher les commandes en cours du client connecté
    """
    # Récupérer l'ID du client depuis la session
    client_id = request.session.get('client_id')

    if not client_id:
        return redirect('frontoffice_connexion')

    # Récupérer les commandes en cours via le service
    commandes = CommandeService.get_commandes_en_cours(client_id)

    # Gérer les erreurs
    if isinstance(commandes, dict) and 'error' in commandes:
        commandes = []

    context = {
        'commandes': commandes,
        'nb_commandes': len(commandes)
    }

    return render(request, 'frontoffice/commandes_en_cours.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def annuler_commande(request, commande_id):
    """
    Vue pour annuler une commande
    """
    try:
        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')

        if not client_id:
            return JsonResponse({
                'success': False,
                'message': "Vous devez être connecté pour annuler une commande"
            })

        # Tenter l'annulation via le service
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


def deconnexion(request):
    request.session.flush()  # Supprimer toutes les données de session
    return redirect('frontoffice_index')
