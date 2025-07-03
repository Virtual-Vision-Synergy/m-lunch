from django.shortcuts import render
from mlunch.core.services import CommandeService
from mlunch.core.services import RestaurantService  
from mlunch.core.services import ZoneService
from mlunch.core.models import StatutCommande, ModePaiement


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

def commande(request):
    commandes = CommandeService.get_all_commandes()
    return render(request, 'backoffice/commande.html', {'commandes': commandes})

def restaurant_commandes(request, restaurant_id):
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    idstatut = request.GET.get('statut')
    idmodepaiement = request.GET.get('mode_paiement')

    commandes = RestaurantService.get_commandes_by_restaurant_filtrer(
        restaurant_id,
        date_debut=date_debut if date_debut else None,
        date_fin=date_fin if date_fin else None,
        idstatut=idstatut if idstatut else None,
        idmodepaiement=idmodepaiement if idmodepaiement else None
    )

    statuts = StatutCommande.objects.all()
    modes_paiement = ModePaiement.objects.all()

    return render(request, 'backoffice/restaurant_commandes.html', {
        'commandes_resto': commandes,
        'restaurant_id': restaurant_id,
        'statuts': statuts,
        'modes_paiement': modes_paiement,
        'selected_statut': int(idstatut) if idstatut else None,
        'selected_mode_paiement': int(idmodepaiement) if idmodepaiement else None,
        'date_debut': date_debut,
        'date_fin': date_fin,
    })