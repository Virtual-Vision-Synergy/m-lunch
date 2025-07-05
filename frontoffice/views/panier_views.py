import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from mlunch.core.services import PanierService


def panier_view(request):
    """
    Vue principale du panier
    """
    # Récupérer l'ID du client depuis la session
    client_id = request.session.get('client_id')

    # Si pas connecté, utiliser un ID par défaut pour les tests
    if not client_id:
        client_id = 1  # ID de test - à remplacer par une redirection vers la connexion

    # Récupérer les articles du panier via le service
    items = PanierService.get_panier_items(client_id)

    # Calculer les totaux via le service
    totals = PanierService.calculate_totals(client_id)

    # Récupérer les points de récupération via le service
    points_recuperation = PanierService.get_points_recuperation()

    # Gérer les erreurs
    if isinstance(items, dict) and 'error' in items:
        items = []

    if isinstance(totals, dict) and 'error' in totals:
        totals = {'sous_total': 0, 'frais_livraison': 0, 'total': 0, 'nb_items': 0}

    if isinstance(points_recuperation, dict) and 'error' in points_recuperation:
        points_recuperation = []

    context = {
        'items': items,
        'totals': totals,
        'points_recuperation': points_recuperation,
        'client_id': client_id
    }

    return render(request, 'frontoffice/panier.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def add_to_panier(request):
    """
    Ajouter un article au panier via AJAX
    """
    try:
        data = json.loads(request.body)
        repas_id = data.get('repas_id')
        quantite = data.get('quantite', 1)

        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({
                'success': False,
                'message': 'Vous devez être connecté pour ajouter au panier'
            })

        # Ajouter au panier via le service
        result = PanierService.add_to_panier(client_id, repas_id, quantite)

        if 'error' in result:
            return JsonResponse({
                'success': False,
                'message': result['error']
            })

        # Récalculer les totaux
        totals = PanierService.calculate_totals(client_id)
        if isinstance(totals, dict) and 'error' in totals:
            totals = {'sous_total': 0, 'frais_livraison': 0, 'total': 0, 'nb_items': 0}

        return JsonResponse({
            'success': True,
            'message': result.get('message', 'Article ajouté au panier'),
            'totals': totals
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def update_quantity(request):
    """
    Mettre à jour la quantité d'un article
    """
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        nouvelle_quantite = data.get('quantite')

        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({
                'success': False,
                'message': 'Vous devez être connecté'
            })

        # Mettre à jour la quantité via le service
        result = PanierService.update_quantity(client_id, item_id, nouvelle_quantite)

        if 'error' in result:
            return JsonResponse({
                'success': False,
                'message': result['error']
            })

        # Récalculer les totaux
        totals = PanierService.calculate_totals(client_id)
        if isinstance(totals, dict) and 'error' in totals:
            totals = {'sous_total': 0, 'frais_livraison': 0, 'total': 0, 'nb_items': 0}

        return JsonResponse({
            'success': True,
            'message': result.get('message', 'Quantité mise à jour'),
            'totals': totals
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def remove_from_panier(request):
    """
    Supprimer un article du panier
    """
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')

        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({
                'success': False,
                'message': 'Vous devez être connecté'
            })

        # Supprimer l'article via le service
        result = PanierService.remove_from_panier(client_id, item_id)

        if 'error' in result:
            return JsonResponse({
                'success': False,
                'message': result['error']
            })

        # Récalculer les totaux
        totals = PanierService.calculate_totals(client_id)
        if isinstance(totals, dict) and 'error' in totals:
            totals = {'sous_total': 0, 'frais_livraison': 0, 'total': 0, 'nb_items': 0}

        return JsonResponse({
            'success': True,
            'message': result.get('message', 'Article supprimé'),
            'totals': totals
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def clear_panier(request):
    """
    Vider complètement le panier
    """
    try:
        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({
                'success': False,
                'message': 'Vous devez être connecté'
            })

        # Vider le panier via le service
        result = PanierService.clear_panier(client_id)

        if 'error' in result:
            return JsonResponse({
                'success': False,
                'message': result['error']
            })

        return JsonResponse({
            'success': True,
            'message': result.get('message', 'Panier vidé avec succès')
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def validate_commande(request):
    """
    Valider la commande et procéder au paiement
    """
    try:
        data = json.loads(request.body)
        point_recup_id = data.get('point_recup_id')
        mode_paiement = data.get('mode_paiement')

        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({
                'success': False,
                'message': 'Vous devez être connecté pour valider une commande'
            })

        # Vérifier que le panier n'est pas vide
        totals = PanierService.calculate_totals(client_id)
        if isinstance(totals, dict) and 'error' in totals:
            return JsonResponse({
                'success': False,
                'message': totals['error']
            })

        if totals['nb_items'] == 0:
            return JsonResponse({
                'success': False,
                'message': 'Votre panier est vide'
            })

        # Valider la commande via le service
        success, message = PanierService.validate_commande(client_id, point_recup_id, mode_paiement)

        if success:
            return JsonResponse({
                'success': True,
                'message': message,
                'redirect_url': '/commandes/confirmation/'  # Page de confirmation
            })
        else:
            return JsonResponse({
                'success': False,
                'message': message
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


def get_panier_count(request):
    """
    Récupérer le nombre d'articles dans le panier (pour le badge)
    """
    try:
        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({'count': 0})

        # Calculer les totaux via le service
        totals = PanierService.calculate_totals(client_id)

        if isinstance(totals, dict) and 'error' in totals:
            return JsonResponse({'count': 0})

        # Calculer la quantité totale
        items = PanierService.get_panier_items(client_id)
        if isinstance(items, dict) and 'error' in items:
            return JsonResponse({'count': 0})

        quantite_totale = sum(item.get('quantite', 0) for item in items)

        return JsonResponse({
            'count': quantite_totale
        })

    except Exception as e:
        return JsonResponse({
            'count': 0
        })