from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from mlunch.core.models import Zone, ZoneClient, ZoneLivreur
from mlunch.core.services.zone_service import ZoneService


def zone_list(request):
    """Liste toutes les zones avec leurs informations et coordonnées pour la carte"""
    zones = Zone.objects.all()
    zones_data = []

    for zone in zones:
        zone_data = {
            'id': zone.id,
            'nom': zone.nom,
            'description': zone.description,
            'zone': zone.zone,
            'clients_count': ZoneClient.objects.filter(zone=zone).count(),
            'livreurs_count': ZoneLivreur.objects.filter(zone=zone).count()
        }
        zones_data.append(zone_data)

    return render(request, 'backoffice/zones/zone_list.html', {
        'zones': zones_data
    })


def zone_detail(request, zone_id):
    """Affiche les détails d'une zone avec sa carte"""
    zone = get_object_or_404(Zone, id=zone_id)
    clients = ZoneClient.objects.filter(zone=zone).select_related('client')
    livreurs = ZoneLivreur.objects.filter(zone=zone).select_related('livreur')

    zone_data = {
        'id': zone.id,
        'nom': zone.nom,
        'description': zone.description,
        'zone': zone.zone,
        'clients': clients,
        'livreurs': livreurs
    }

    return render(request, 'backoffice/zones/zone_detail.html', {
        'zone': zone_data
    })


def zone_create(request):
    """Création d'une nouvelle zone avec dessin sur carte"""
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description', '')
        coordinates = request.POST.get('coordinates')

        if not nom or not coordinates:
            messages.error(request, 'Le nom et les coordonnées sont requis')
            return render(request, 'backoffice/zones/zone_create.html')

        try:
            # Parser les coordonnées JSON
            coords_data = json.loads(coordinates)
            if len(coords_data) < 3:
                messages.error(request, 'Au minimum 3 points sont requis pour définir une zone')
                return render(request, 'backoffice/zones/zone_create.html')

            # Utiliser le service pour créer la zone
            result = ZoneService.create_zone(nom, description, coords_data, 1)

            if 'error' in result:
                messages.error(request, result['error'])
                return render(request, 'backoffice/zones/zone_create.html')

            messages.success(request, f'Zone "{nom}" créée avec succès!')
            return redirect('zone_detail', zone_id=result['zone']['id'])

        except json.JSONDecodeError:
            messages.error(request, 'Format de coordonnées invalide')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')

    return render(request, 'backoffice/zones/zone_create.html')


def zone_edit(request, zone_id):
    """Modification d'une zone existante"""
    zone = get_object_or_404(Zone, id=zone_id)

    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description', '')
        coordinates = request.POST.get('coordinates')

        if not nom:
            messages.error(request, 'Le nom est requis')
            return render(request, 'backoffice/zones/zone_edit.html', {'zone': zone})

        try:
            zone.nom = nom
            zone.description = description

            if coordinates:
                coords_data = json.loads(coordinates)
                if len(coords_data) >= 3:
                    # Convertir en format WKT si nécessaire
                    polygon_coords = ', '.join([f"{coord['lng']} {coord['lat']}" for coord in coords_data])
                    # Fermer le polygone en ajoutant le premier point à la fin
                    first_coord = coords_data[0]
                    polygon_coords += f", {first_coord['lng']} {first_coord['lat']}"
                    zone.zone = f"POLYGON(({polygon_coords}))"

            zone.save()
            messages.success(request, f'Zone "{nom}" modifiée avec succès!')
            return redirect('zone_detail', zone_id=zone.id)

        except json.JSONDecodeError:
            messages.error(request, 'Format de coordonnées invalide')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    return render(request, 'backoffice/zones/zone_edit.html', {'zone': zone})


@require_http_methods(["DELETE", "POST"])
def zone_delete(request, zone_id):
    """Suppression d'une zone"""
    zone = get_object_or_404(Zone, id=zone_id)

    try:
        zone_nom = zone.nom
        zone.delete()

        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': True, 'message': f'Zone "{zone_nom}" supprimée avec succès'})
        else:
            messages.success(request, f'Zone "{zone_nom}" supprimée avec succès!')
            return redirect('zone_list')

    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'error': str(e)})
        else:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')
            return redirect('zone_detail', zone_id=zone_id)


@csrf_exempt
def get_zone_by_coordinates(request):
    """API pour récupérer une zone par coordonnées"""
    if request.method == 'POST':
        data = json.loads(request.body)
        lat = data.get('lat')
        lng = data.get('lng')

        if lat and lng:
            result = ZoneService.get_zone_by_coord(lat, lng)
            return JsonResponse(result if result else {'error': 'Aucune zone trouvée'})

    return JsonResponse({'error': 'Paramètres invalides'})
