from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Client, ZoneClient, ZoneRestaurant, Restaurant, RepasRestaurant, TypeRepas
import random
from django.contrib.auth.hashers import check_password

def connexion_view(request):
    error_message = None

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            client = Client.objects.get(email=email)
            if check_password(password, client.mot_de_passe):
                request.session['client_id'] = client.id  # simple session login
                return redirect('frontoffice_accueil')  # change to your home URL name
            else:
                error_message = "Mot de passe incorrect."
        except Client.DoesNotExist:
            error_message = "Email introuvable."

    return render(request, 'frontoffice/connexion.html', {
        'error_message': error_message
    })

def restaurants_geojson(request):
    client_id = request.session.get('client_id')
    if not client_id:
        return JsonResponse({'error': 'Non connecté'}, status=401)

    zones = ZoneClient.objects.filter(client_id=client_id).values_list('zone_id', flat=True)
    zone_restaurants = ZoneRestaurant.objects.filter(zone_id__in=zones).select_related('restaurant')

    features = []
    for zr in zone_restaurants:
        r = zr.restaurant
        if not r.geo_position:
            continue

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [r.geo_position.x, r.geo_position.y],
            },
            "properties": {
                "id": r.id,
                "nom": r.nom,
                "note": "N/A",  # Tu peux ajouter une colonne `note` plus tard si nécessaire
                "image_url": r.image,
            }
        })

    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })

def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Get selected type if filtered
    selected_type = request.GET.get('type')

    repas_qs = RepasRestaurant.objects.filter(restaurant=restaurant).select_related('repas', 'repas__type')

    if selected_type:
        repas_qs = repas_qs.filter(repas__type__id=selected_type)

    repas_list = [rr.repas for rr in repas_qs]
    types = TypeRepas.objects.all()
    #note = round(random.uniform(3.0, 5.0), 1)

    return render(request, 'frontoffice/restaurant_detail.html', {
        'restaurant': restaurant,
        'repas': repas_list,
        'note': 5,
        'types': types,
        'selected_type': int(selected_type) if selected_type else None
    })
def accueil_view(request):
    return render(request, 'frontoffice/accueil.html')
def index(request):
    return render(request, 'frontoffice/index.html')

