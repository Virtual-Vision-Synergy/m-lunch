from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Client, ZoneClient, ZoneRestaurant, Restaurant, RepasRestaurant, TypeRepas, DisponibiliteRepas, Commande, HistoriqueStatutCommande, CommandeRepas, PointDeRecuperation
import random
from django.contrib.auth.hashers import check_password
from django.utils.timezone import now
from django.db.models import Max, Sum, F
from django.http import HttpResponseRedirect
from functools import wraps

def connexion_view(request):
    error_message = None

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            client = Client.objects.get(email=email)
            if check_password(password, client.mot_de_passe):
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
    current_time = now()
    for r in repas_list:
        is_dispo = DisponibiliteRepas.objects.filter(
            repas=r,
            debut__lte=current_time,
            fin__gte=current_time
        ).exists()
        r.disponible = is_dispo

    types = TypeRepas.objects.all()
    #note = round(random.uniform(3.0, 5.0), 1)

    return render(request, 'frontoffice/restaurant_detail.html', {
        'restaurant': restaurant,
        'repas': repas_list,
        'note': 5,
        'types': types,
        'selected_type': int(selected_type) if selected_type else None
    })

def mes_commandes(request):
    client_id = request.session.get("client_id")

    commandes = (
        Commande.objects
        .filter(client_id=client_id)
        .order_by('-cree_le')
    )

    # Attach additional data (number of items, total, last status)
    commandes_data = []
    for c in commandes:
        repas = CommandeRepas.objects.filter(commande=c)
        total_articles = repas.aggregate(Sum('quantite'))['quantite__sum'] or 0
        total_prix = sum([r.repas.prix * r.quantite for r in repas])
        statut = (
            HistoriqueStatutCommande.objects
            .filter(commande=c)
            .order_by('-mis_a_jour_le')
            .first()
        )
        commandes_data.append({
            'commande': c,
            'articles': total_articles,
            'total': total_prix,
            'statut': statut.statut.appellation if statut else "Inconnu"
        })

    return render(request, 'frontoffice/mes_commandes.html', {
        'commandes': commandes_data
    })

def detail_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    repas = CommandeRepas.objects.filter(commande=commande)
    statut = (
        HistoriqueStatutCommande.objects
        .filter(commande=commande)
        .order_by('-mis_a_jour_le')
        .first()
    )

    total = sum([r.repas.prix * r.quantite for r in repas])

    return render(request, 'frontoffice/detail_commande.html', {
        'commande': commande,
        'repas': repas,
        'statut': statut.statut.appellation if statut else "Inconnu",
        'total': total
    })

def points_de_recuperation(request):
    points = PointDeRecuperation.objects.all()

    features = []
    for point in points:
        if not point.geo_position:
            continue

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [point.geo_position.x, point.geo_position.y],
            },
            "properties": {
                "id": point.id,
                "nom": point.nom,
            }
        })

    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })

def all_restaurants(request):
    restaurants = Restaurant.objects.all()

    features = []
    for r in restaurants:
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
                "note": "N/A",
                "image_url": r.image,
                "adresse": r.adresse,
                "description": r.description if r.description else "Aucune description disponible",
            }
        })

    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })

def restaurant_view(request):
    return render(request, 'frontoffice/restaurant.html')

def accueil_view(request):
    return render(request, 'frontoffice/accueil.html')

def logout_view(request):
    # Clear Django session
    request.session.flush()  # Deletes session data and cookie
    # OR alternative:
    # del request.session['client_id']  # Remove only specific key
    
    return redirect('frontoffice_connexion')  # Redirect to login

def index(request):
    return render(request, 'frontoffice/index.html')

