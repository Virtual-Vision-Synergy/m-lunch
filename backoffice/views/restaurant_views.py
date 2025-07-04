from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from mlunch.core.services.restaurant_service import RestaurantService
from mlunch.core.services.zone_service import ZoneService
from mlunch.core.models import Restaurant, Zone, StatutRestaurant
import json
import os
from django.conf import settings
from math import radians, cos, sin, asin, sqrt
from django.db import transaction

def restaurant(request):
    """Page de liste des restaurants avec filtres."""
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

def restaurant_detail(request, restaurant_id):
    """Détail d'un restaurant spécifique"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return render(request, 'backoffice/restaurant_detail.html', {
        'restaurant': restaurant
    })

def restaurant_commandes(request, restaurant_id):
    """Commandes d'un restaurant spécifique"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
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

def restaurant_ajouter(request):
    """Affiche le formulaire d'ajout de restaurant."""
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

def extract_coordinates(request):
    """Extrait les coordonnées GPS de la requête."""
    try:
        lat = float(request.POST.get('geo_position_lat'))
        lng = float(request.POST.get('geo_position_lng'))
        return lat, lng
    except (ValueError, TypeError):
        raise Exception("Coordonnées GPS invalides")

def save_image(image_file):
    """Sauvegarde une image uploadée."""
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

def create_restaurant_and_statut(nom, initial_statut_id, adresse, image_name, geo_position):
    """Crée un restaurant avec son statut initial."""
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
    """Insère la commission d'un restaurant."""
    Commission.objects.create(
        restaurant=restaurant,
        valeur=int(commission_value)
    )

def insert_horaires(restaurant, request):
    """Insère les horaires d'ouverture d'un restaurant."""
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
    """Extrait le premier point d'un polygone WKT."""
    try:
        points_str = wkt_polygon.replace('POLYGON((', '').replace('))', '')
        first_point_str = points_str.split(',')[0].strip()
        lon_str, lat_str = first_point_str.split()
        return float(lon_str), float(lat_str)
    except Exception:
        return None, None

def find_closest_zone(lat, lng, max_distance_km=5):
    """Trouve la zone la plus proche d'un point donné."""
    closest_zone = None
    min_distance = float('inf')
    for zone in Zone.objects.all():
        if not zone.zone:
            continue
        zone_lon, zone_lat = extract_first_point_from_polygon(zone.zone)
        if zone_lat is None or zone_lon is None:
            continue
        distance = haversine(lng, lat, zone_lon, zone_lat)
        print(f"Zone {zone.nom}: distance={distance} km")
        if distance < min_distance and distance <= max_distance_km:
            min_distance = distance
            closest_zone = zone
    if not closest_zone:
        raise Exception("Aucune zone trouvée à moins de 5 km")
    return closest_zone

def assign_zone_to_restaurant(restaurant, zone):
    """Assigne une zone à un restaurant."""
    ZoneRestaurant.objects.create(restaurant=restaurant, zone=zone)

def ajouter_restaurant(request):
    """Traite l'ajout d'un nouveau restaurant."""
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

@csrf_exempt
def get_restaurant_detail(request, restaurant_id):
    """API pour récupérer les détails d'un restaurant."""
    try:
        from mlunch.core.models import RestaurantRepas, HoraireSpecial

        restaurant = Restaurant.objects.get(id=restaurant_id)

        # Récupérer le statut actuel
        from mlunch.core.models import HistoriqueStatutRestaurant
        latest_statut = HistoriqueStatutRestaurant.objects.filter(
            restaurant=restaurant
        ).select_related('statut').order_by('-id').first()

        # Récupérer les repas proposés
        repas_data = []
        repas_restaurants = RestaurantRepas.objects.filter(restaurant=restaurant).select_related('repas__type')

        for rr in repas_restaurants:
            repas = rr.repas
            repas_data.append({
                'id': repas.id,
                'nom': repas.nom,
                'description': repas.description,
                'prix': float(repas.prix),
                'type_repas': repas.type.nom if repas.type else 'Inconnu'
            })

        # Récupérer les horaires réguliers
        horaires_data = []
        horaires = Horaire.objects.filter(restaurant=restaurant).order_by('le_jour')

        for horaire in horaires:
            horaires_data.append({
                'le_jour': horaire.le_jour,
                'horaire_debut': str(horaire.horaire_debut),
                'horaire_fin': str(horaire.horaire_fin)
            })

        # Récupérer les horaires exceptionnels
        horaires_special_data = []
        horaires_special = HoraireSpecial.objects.filter(restaurant=restaurant).order_by('date_concerne')

        for hs in horaires_special:
            horaires_special_data.append({
                'date_concerne': str(hs.date_concerne),
                'horaire_debut': str(hs.horaire_debut),
                'horaire_fin': str(hs.horaire_fin)
            })

        response = {
            'restaurant': {
                'id': restaurant.id,
                'nom': restaurant.nom,
                'adresse': restaurant.adresse,
                'geo_position': restaurant.geo_position,
                'statut_actuel': latest_statut.statut.appellation if latest_statut else 'Inconnu'
            },
            'repas': repas_data,
            'horaires': horaires_data,
            'horaires_special': horaires_special_data
        }

        print(f"Détails du restaurant {restaurant_id}: {response}")
        return JsonResponse(response, status=200)
    except Restaurant.DoesNotExist:
        print(f"Erreur: Restaurant ID {restaurant_id} non trouvé")
        return JsonResponse({"error": f"Restaurant ID {restaurant_id} non trouvé"}, status=404)
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return JsonResponse({"error": f"Erreur inattendue : {str(e)}"}, status=500)

@csrf_exempt
def restaurant_update_statut(request, restaurant_id):
    """Met à jour le statut d'un restaurant"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nouveau_statut_id = data.get('statut_id')

            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
            RestaurantService.update_statut_restaurant(restaurant, nouveau_statut_id)

            return JsonResponse({'success': True, 'message': 'Statut mis à jour avec succès'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})
