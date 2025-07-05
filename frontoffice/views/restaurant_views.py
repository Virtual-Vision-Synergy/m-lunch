from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from frontoffice.views.commande_views import authentification_requise
from mlunch.core.models import Restaurant, Zone, ZoneClient
from mlunch.core.services import RestaurantService, ZoneService, RepasService, CommandeService


def restaurant_list(request):
    """Liste des restaurants pour les clients"""
    zone_id = request.GET.get('zone')
    search_query = request.GET.get('q')

    if zone_id:
        restaurants = RestaurantService.list_restaurants_by_zone(zone_id)
    elif search_query:
        restaurants = RestaurantService.search_restaurants(search_query)
    else:
        restaurants = RestaurantService.list_restaurants_actifs()

    zones = ZoneService.get_all_zones()

    return render(request, 'frontoffice/restaurant.html', {
        'restaurants': restaurants,
        'zones': zones,
        'selected_zone': int(zone_id) if zone_id else None,
        'search_query': search_query
    })


# def restaurant_detail(request, restaurant_id):
#     """Détail d'un restaurant avec ses repas"""
#     restaurant = get_object_or_404(Restaurant, id=restaurant_id)
#     repas_disponibles = RepasService.list_repas_by_restaurant(restaurant_id)

#     repas_par_type = {}
#     for repas in repas_disponibles:
#         type_nom = repas.type.nom if repas.type else 'Autres'
#         if type_nom not in repas_par_type:
#             repas_par_type[type_nom] = []
#         repas_par_type[type_nom].append(repas)

#     return render(request, 'frontoffice/restaurant_detail.html', {
#         'restaurant': restaurant,
#         'repas_par_type': repas_par_type
#     })

def restaurant_detail(request, restaurant_id):
    selected_type = request.GET.get('type')

    data = RestaurantService.get_repas_for_restaurant(restaurant_id, selected_type)
    if "error" in data:
        return render(request, 'frontoffice/restaurant_detail.html', {
            'error': data["error"]
        })

    return render(request, 'frontoffice/restaurant_detail.html', {
        'restaurant': data['restaurant'],
        'repas': data['repas'],
        'note': data['note'],
        'types': data['types'],
        'selected_type': data['selected_type']
    })


def restaurants_geojson(request):
    client_id = request.session.get('client_id')
    if not client_id:
        return JsonResponse({'error': 'Non connecté'}, status=401)

    data = RestaurantService.get_restaurants_by_client_zones(client_id)
    return JsonResponse(data)


def all_restaurants(request):
    data = RestaurantService.get_all_restaurants_geojson()
    return JsonResponse(data)


def barre_recherche_view(request):
    """Vue pour la page de recherche de restaurants"""
    # Récupérer toutes les zones pour le dropdown
    zones = Zone.objects.all().order_by('nom')

    # Initialiser les variables de recherche
    secteur_recherche = ""
    nom_recherche = ""
    adresse_recherche = ""
    restaurants = []
    nb_resultats = 0
    user_zone = None

    # Récupérer la zone de l'utilisateur connecté
    if request.session.get('client_id'):
        try:
            zone_client = ZoneClient.objects.filter(client_id=request.session['client_id']).first()
            if zone_client:
                user_zone = zone_client.zone.nom
        except:
            pass

    # Traitement du formulaire de recherche
    if request.method == 'POST':
        secteur_recherche = request.POST.get('secteur', '').strip()
        nom_recherche = request.POST.get('nom', '').strip()
        adresse_recherche = request.POST.get('adresse', '').strip()

        # Construction de la requête de recherche
        query = Q()

        # Filtre par nom de restaurant
        if nom_recherche:
            query &= Q(nom__icontains=nom_recherche)

        # Filtre par adresse
        if adresse_recherche:
            query &= Q(adresse__icontains=adresse_recherche)

        # Filtre par secteur/zone (si implémenté dans le modèle)
        if secteur_recherche:
            # Note: Vous devrez peut-être ajuster cette logique selon votre modèle
            # Si les restaurants sont liés aux zones, adaptez cette requête
            query &= Q(adresse__icontains=secteur_recherche)

        # Exécuter la recherche
        if query:
            restaurants = Restaurant.objects.filter(query).distinct()
        else:
            # Si aucun critère n'est spécifié, afficher tous les restaurants
            restaurants = Restaurant.objects.all()

        nb_resultats = restaurants.count()

    context = {
        'zones': zones,
        'restaurants': restaurants,
        'nb_resultats': nb_resultats,
        'secteur_recherche': secteur_recherche,
        'nom_recherche': nom_recherche,
        'adresse_recherche': adresse_recherche,
        'user_zone': user_zone,
    }

    return render(request, 'frontoffice/barre_recherche.html', context)



def restaurants_geojson(request):
    client_id = request.session.get('client_id')
    if not client_id:
        return JsonResponse({'error': 'Non connecté'}, status=401)

    data = RestaurantService.get_restaurants_by_client_zones(client_id)
    return JsonResponse(data)

def mes_commandes(request):
    client_id = request.session.get("client_id")

    commandes_data = CommandeService.get_commandes_by_client(client_id)
    return render(request, 'frontoffice/mes_commandes.html', {
        'commandes': commandes_data
    })

def detail_commande(request, commande_id):
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