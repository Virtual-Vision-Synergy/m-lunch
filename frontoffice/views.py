from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Client, ZoneClient, ZoneRestaurant, Restaurant
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
    print("Client's zone IDs:", list(zones))  # Convert queryset to list to print

    zone_restaurants = ZoneRestaurant.objects.filter(zone_id__in=zones).select_related('restaurant')
    print("Restaurants in client's zones:")
    for zr in zone_restaurants:
        print("-", zr.restaurant.nom, f"(Zone ID: {zr.zone_id})")

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

def accueil_view(request):
    return render(request, 'frontoffice/accueil.html')
def index(request):
    return render(request, 'frontoffice/index.html')

