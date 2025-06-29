from django.shortcuts import render, redirect
from database.db import fetch_query
from django.http import JsonResponse

from django.contrib import messages
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from mlunch.core.services import ClientService, ZoneService
from mlunch.core.models import Zone, Client, ZoneClient  # Import du modèle de liaison
from shapely import wkt

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
