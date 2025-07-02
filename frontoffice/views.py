from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import random
import json
from django.contrib.auth.hashers import check_password
from django.utils.timezone import now
from django.db.models import Max, Sum, F
from django.http import HttpResponseRedirect
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from mlunch.core.services import ClientService, ZoneService, RestaurantService,CommandeService, PointRecupService
from mlunch.core.models import Zone, Client, ZoneClient  # Import du modèle de liaison
from shapely import wkt

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

    data = RestaurantService.get_restaurants_by_client_zones(client_id)
    return JsonResponse(data)

def restaurant_detail(request, restaurant_id):
    #restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Get selected type if filtered
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
    return JsonResponse(data)

def all_restaurants(request):
    data = RestaurantService.get_all_restaurants_geojson()
    return JsonResponse(data)

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


@csrf_exempt  # Adding this to allow testing without CSRF
def inscription_page(request):
    # Initialize error variable to None
    error = None

    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        mot_de_passe = request.POST.get('mot_de_passe')
        telephone = request.POST.get('telephone')
        secteur_nom = request.POST.get('secteur')

        # Vérifier que tous les champs sont remplis
        if not all([nom, prenom, email, mot_de_passe, telephone]):
            error = "Tous les champs sont obligatoires."
        # Vérifier que le secteur est fourni
        elif not secteur_nom:
            error = "Veuillez sélectionner un secteur en cliquant sur la carte."
        else:
            # 1. Insérer client via ORM
            result = ClientService.create_client(email, mot_de_passe, contact=telephone, prenom=prenom, nom=nom)
            if 'error' in result:
                error = result['error']
            else:
                client_id = result['client']['id']

                # 2. Vérifier que la zone existe et récupérer son instance
                try:
                    zone = Zone.objects.get(nom=secteur_nom)
                except Zone.DoesNotExist:
                    error = f"Secteur '{secteur_nom}' introuvable."
                else:
                    # 3. Lier client/zone via ZoneClient
                    try:
                        client = Client.objects.get(id=client_id)
                        ZoneClient.objects.create(client=client, zone=zone)
                        # Si tout s'est bien passé, rediriger vers la page d'accueil
                        return redirect('frontoffice_index')
                    except Exception as e:
                        error = f"Erreur lors de l'insertion dans zones_clients: {e}"

    # Préparer les données des zones pour l'affichage de la carte
    zones = Zone.objects.all()
    zones_features = []
    for z in zones:
        try:
            geom = wkt.loads(z.zone)
            zones_features.append({
                'type': 'Feature',
                'geometry': json.loads(geom.to_geojson()),
                'properties': {'id': z.id, 'nom': z.nom}
            })
        except Exception:
            continue

    # Retourner le template avec les zones et l'erreur si elle existe
    return render(request, 'frontoffice/inscription.html', {
        'zones': zones_features,
        'erreur': error
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


def deconnexion(request):
    request.session.flush()  # Supprimer toutes les données de session
    return redirect('frontoffice_index') 
