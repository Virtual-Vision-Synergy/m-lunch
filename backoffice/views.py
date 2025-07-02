from django.shortcuts import render
from mlunch.core.services import CommandeService
from mlunch.core.services import RestaurantService  
from mlunch.core.services import ZoneService


def index(request):
    commandes_en_attente = CommandeService.get_commandes_en_attente()
    return render(request, 'backoffice/index.html', {'commandes_en_attente': commandes_en_attente})

def restaurant(request):
    zone_id = request.GET.get('zone')
    statut_id = request.GET.get('statut')
    if zone_id or statut_id:
        restaurants = RestaurantService.list_restaurant_filtrer(zone_id, statut_id)
    else:
        restaurants = RestaurantService.list_restaurants_all_details()
    zones = ZoneService.get_all_zones()
    statuts = RestaurantService.get_all_statuts()
    selected_zone = int(zone_id) if zone_id else None
    selected_statut = int(statut_id) if statut_id else None
    return render(request, 'backoffice/restaurant.html', {
        'restaurants': restaurants,
        'zones': zones,
        'statuts': statuts,
        'selected_zone': selected_zone,
        'selected_statut': selected_statut
    })
