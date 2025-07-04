import json

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from mlunch.core.services import RestaurantService, CommandeService, PointRecupService, PanierService
from mlunch.core.services.restaurant_service import RestaurantService
from mlunch.core.services.repas_service import RepasService
from mlunch.core.services.zone_service import ZoneService
from mlunch.core.models import Zone, Client, ZoneClient, Restaurant, Repas  # Import du modèle de liaison
from shapely import wkt
from mlunch.core.services import ClientService
from mlunch.core.services import ZoneService


def connexion_view(request):
    error_message = None

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        #print(password)
        try:
            client = Client.objects.get(email=email)
            if password == client.mot_de_passe:
                request.session['client_id'] = client.id  # simple session login
                return redirect('frontoffice_restaurant')  # change to your home URL name
            else:
                error_message = "Mot de passe incorrect."
        except Client.DoesNotExist:
            error_message = "Email introuvable."

    return render(request, 'frontoffice/connexion.html', {
        'error_message': error_message
    })


def authentification_requise(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('client_id'):
            return HttpResponseRedirect('/connexion/')  # Change to your login URL if different
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@authentification_requise
def restaurants_geojson(request):
    client_id = request.session.get('client_id')
    if not client_id:
        return JsonResponse({'error': 'Non connecté'}, status=401)

    data = RestaurantService.get_restaurants_by_client_zones(client_id)
    return JsonResponse(data)


def index(request):
    """Page d'accueil du frontoffice"""
    restaurants_populaires = RestaurantService.get_restaurants_populaires()[:6]
    zones_disponibles = ZoneService.get_all_zones()

    return render(request, 'frontoffice/index.html', {
        'restaurants_populaires': restaurants_populaires,
        'zones_disponibles': zones_disponibles
    })


def accueil(request):
    """Page d'accueil alternative avec recherche"""
    return render(request, 'frontoffice/accueil.html')


def restaurant_list(request):
    """Liste des restaurants pour les clients"""
    zone_id = request.GET.get('zone')
    search_query = request.GET.get('q')

    if zone_id:
        restaurants = RestaurantService.get_restaurants_by_zone(zone_id)
    elif search_query:
        restaurants = RestaurantService.search_restaurants(search_query)
    else:
        restaurants = RestaurantService.get_restaurants_actifs()

    zones = ZoneService.get_all_zones()

    return render(request, 'frontoffice/restaurant.html', {
        'restaurants': restaurants,
        'zones': zones,
        'selected_zone': int(zone_id) if zone_id else None,
        'search_query': search_query
    })


def restaurant_detail(request, restaurant_id):
    """Détail d'un restaurant avec ses repas"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    repas_disponibles = RepasService.get_repas_by_restaurant(restaurant_id)

    # Organiser les repas par type
    repas_par_type = {}
    for repas in repas_disponibles:
        type_nom = repas.type.nom if repas.type else 'Autres'
        if type_nom not in repas_par_type:
            repas_par_type[type_nom] = []
        repas_par_type[type_nom].append(repas)

    return render(request, 'frontoffice/restaurant_detail.html', {
        'restaurant': restaurant,
        'repas_par_type': repas_par_type
    })


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


def points_de_recuperation(request):
    data = PointRecupService.get_all_points_recup_geojson()
    print(data)
    return JsonResponse(data)


def all_restaurants(request):
    data = RestaurantService.get_all_restaurants_geojson()
    #print(data)
    return JsonResponse(data)


def logout_view(request):
    # Clear Django session
    request.session.flush()  # Deletes session data and cookie
    # OR alternative:
    # del request.session['client_id']  # Remove only specific key

    return redirect('frontoffice_connexion')  # Redirect to login


def barre_recherche(request):
    """
    Vue pour la recherche de restaurants par secteur, nom ou adresse
    """
    restaurants = []
    secteur = ""
    nom = ""
    adresse = ""

    # Récupérer la zone de l'utilisateur connecté
    user_zone = None
    client_id = request.session.get('client_id')

    if client_id:
        # Récupérer la zone du client via le service
        client_zone_data = ClientService.get_client_zone(client_id)
        if client_zone_data and 'zone_nom' in client_zone_data:
            user_zone = client_zone_data['zone_nom']

    if request.method == 'POST':
        secteur = request.POST.get('secteur', '').strip()
        nom = request.POST.get('nom', '').strip()
        adresse = request.POST.get('adresse', '').strip()

        # Rechercher les restaurants en utilisant le service
        if secteur or nom or adresse:
            if adresse:
                restaurants = RestaurantService.search_restaurants(adresse=adresse)
            else:
                restaurants = RestaurantService.search_restaurants(
                    secteur=secteur if secteur else None,
                    nom=nom if nom else None
                )
        else:
            # Si aucun critère, afficher tous les restaurants
            restaurants = RestaurantService.search_restaurants()

    elif request.method == 'GET':
        # Pour les requêtes AJAX ou paramètres GET
        secteur = request.GET.get('secteur', '').strip()
        nom = request.GET.get('nom', '').strip()
        adresse = request.GET.get('adresse', '').strip()

        if secteur or nom or adresse:
            if adresse:
                restaurants = RestaurantService.search_restaurants(adresse=adresse)
            else:
                restaurants = RestaurantService.search_restaurants(
                    secteur=secteur if secteur else None,
                    nom=nom if nom else None
                )

        # Si c'est une requête AJAX, retourner du JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Ajouter l'information de disponibilité dans la zone utilisateur
            restaurants_with_availability = []
            if restaurants and not isinstance(restaurants, dict):  # Vérifier que ce n'est pas une erreur
                for resto in restaurants:
                    resto['available_in_user_zone'] = (
                        resto.get('zone_nom') == user_zone if user_zone else True
                    )
                    restaurants_with_availability.append(resto)

            return JsonResponse({
                'success': True,
                'restaurants': restaurants_with_availability,
                'count': len(restaurants_with_availability),
                'user_zone': user_zone
            })

    # Ajouter l'information de disponibilité pour l'affichage
    if restaurants and not isinstance(restaurants, dict):  # Vérifier que ce n'est pas une erreur
        restaurants_with_availability = []
        for resto in restaurants:
            resto['available_in_user_zone'] = (
                resto.get('zone_nom') == user_zone if user_zone else True
            )
            restaurants_with_availability.append(resto)
        restaurants = restaurants_with_availability

    # Récupérer toutes les zones pour le dropdown via le service
    zones_data = ZoneService.get_all_zones()
    zones = []
    if zones_data and not isinstance(zones_data, dict):  # Vérifier que ce n'est pas une erreur
        zones = [{'nom': zone['nom']} for zone in zones_data]

    context = {
        'restaurants': restaurants if not isinstance(restaurants, dict) else [],
        'zones': zones,
        'secteur_recherche': secteur,
        'nom_recherche': nom,
        'adresse_recherche': adresse,
        'nb_resultats': len(restaurants) if restaurants and not isinstance(restaurants, dict) else 0,
        'user_zone': user_zone
    }

    return render(request, 'frontoffice/barre_recherche.html', context)


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


def api_zone_from_coord(request):
    try:
        lat = float(request.GET.get('lat'))
        lon = float(request.GET.get('lon'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Coordonnées invalides'})

    zone = ZoneService.get_zone_by_coord(lat, lon)
    if zone:
        return JsonResponse({'success': True, 'nom': zone['nom'], 'zone_id': zone['id']})
    else:
        return JsonResponse({'success': False})


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
