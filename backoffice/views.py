from django.shortcuts import render
from mlunch.core.services import CommandeService
from mlunch.core.services import RestaurantService  
from mlunch.core.services import ZoneService

from mlunch.core.models import StatutRestaurant, Commission, Horaire, Zone, ZoneRestaurant, Restaurant, StatutCommande, ModePaiement
import os
from django.conf import settings
from math import radians, cos, sin, asin, sqrt
from django.db import transaction

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

# AJOUT DE RESTAURANT

def restaurant_ajouter(request):
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    return render(request, 'backoffice/restaurant_ajout.html', {
        'message': None,
        'statuts': StatutRestaurant.objects.all(),
        'jours': jours,
    })


def haversine(lon1, lat1, lon2, lat2):
    """Retourne la distance en km entre deux points GPS."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return 6371 * c  # Rayon Terre

### === EXTRACTIONS FORMULAIRE === ###
def extract_coordinates(request):
    try:
        lat = float(request.POST.get('geo_position_lat'))
        lng = float(request.POST.get('geo_position_lng'))
        return lat, lng
    except (ValueError, TypeError):
        raise Exception("Coordonnées GPS invalides")

def save_image(image_file):
    if not image_file:
        return None
    images_dir = os.path.join(settings.BASE_DIR, 'backoffice', 'static', 'images')
    os.makedirs(images_dir, exist_ok=True)
    image_name = image_file.name
    image_path = os.path.join(images_dir, image_name)
    with open(image_path, 'wb+') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)
    return image_name

### === BASES DE DONNÉES === ###
def create_restaurant_and_statut(nom, initial_statut_id, adresse, image_name, geo_position):
    result = RestaurantService.create_restaurant(
        nom=nom,
        initial_statut_id=initial_statut_id,
        adresse=adresse,
        image=image_name,
        geo_position=geo_position
    )
    if "error" in result:
        raise Exception(result["error"])
    return Restaurant.objects.get(id=result["restaurant"]["id"])

def insert_commission(restaurant, commission_value):
    Commission.objects.create(
        restaurant=restaurant,
        valeur=int(commission_value)
    )

def insert_horaires(restaurant, request):
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    for i, day in enumerate(jours):
        horaire_debut = request.POST.get(f"horaire_{day}_debut")
        horaire_fin = request.POST.get(f"horaire_{day}_fin")
        if horaire_debut and horaire_fin:
            Horaire.objects.create(
                restaurant=restaurant,
                le_jour=i,
                horaire_debut=horaire_debut,
                horaire_fin=horaire_fin
            )
def extract_first_point_from_polygon(wkt_polygon):
    try:
        points_str = wkt_polygon.replace('POLYGON((', '').replace('))', '')
        first_point_str = points_str.split(',')[0].strip()
        lon_str, lat_str = first_point_str.split()
        return float(lon_str), float(lat_str)  # inversion ici -> retourne (lon, lat)
    except Exception:
        return None, None

def find_closest_zone(lat, lng, max_distance_km=5):
    closest_zone = None
    min_distance = float('inf')
    for zone in Zone.objects.all():
        if not zone.zone:
            continue
        zone_lon, zone_lat = extract_first_point_from_polygon(zone.zone)  # Notez l'ordre changé
        if zone_lat is None or zone_lon is None:
            continue
        distance = haversine(lng, lat, zone_lon, zone_lat)  # lon1, lat1, lon2, lat2
        print(f"Zone {zone.nom}: distance={distance} km")  # Debug
        if distance < min_distance and distance <= max_distance_km:
            min_distance = distance
            closest_zone = zone
    if not closest_zone:
        raise Exception("Aucune zone trouvée à moins de 5 km")
    return closest_zone

def assign_zone_to_restaurant(restaurant, zone):
    ZoneRestaurant.objects.create(restaurant=restaurant, zone=zone)

### === FONCTION PRINCIPALE === ###
def ajouter_restaurant(request):
    message = None
    message_type = None

    if request.method == 'POST':
        try:
            with transaction.atomic():

                nom = request.POST.get('nom')
                initial_statut_id = request.POST.get('initial_statut_id')
                adresse = request.POST.get('adresse')
                commission_value = request.POST.get('commission')
                image_file = request.FILES.get('image')

                lat, lng = extract_coordinates(request)
                geo_position = (lat, lng)

                image_name = save_image(image_file)
                restaurant = create_restaurant_and_statut(nom, initial_statut_id, adresse, image_name, geo_position)

                insert_commission(restaurant, commission_value)
                insert_horaires(restaurant, request)

                zone = find_closest_zone(lat, lng)
                assign_zone_to_restaurant(restaurant, zone)

                message = "Restaurant ajouté avec succès et zone attribuée"
                message_type = "success"

        except Exception as e:
            message = f"Erreur : {str(e)}"
            message_type = "error"

    statuts = StatutRestaurant.objects.all()
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    return render(request, 'backoffice/restaurant_ajout.html', {
        'message': message,
        'message_type': message_type,
        'jours': jours,
        'statuts': statuts
    })