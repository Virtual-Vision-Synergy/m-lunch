from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from mlunch.core.services.zone_service import ZoneService
from mlunch.core.models import Zone, ZoneRestaurant, ZoneClient
import json

def zone_list(request):
    zones = ZoneService.get_all_zones()
    return render(request, 'backoffice/zones_management.html', {
        'zones': zones
    })

def zone_detail(request, zone_id):
    """Détail d'une zone spécifique"""
    zone = get_object_or_404(Zone, id=zone_id)
    restaurants = ZoneRestaurant.objects.filter(zone=zone).select_related('restaurant')
    clients = ZoneClient.objects.filter(zone=zone).select_related('client')

    return render(request, 'backoffice/zone_detail.html', {
        'zone': zone,
        'restaurants': restaurants,
        'clients': clients
    })

def zone_add(request):
    """Ajouter une nouvelle zone"""
    if request.method == 'POST':
        try:
            nom = request.POST.get('nom')
            description = request.POST.get('description')
            zone_polygon = request.POST.get('zone')

            zone = ZoneService.create_zone({
                'nom': nom,
                'description': description,
                'zone': zone_polygon
            })

            messages.success(request, 'Zone ajoutée avec succès')
            return redirect('backoffice:zone_detail', zone_id=zone.id)
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    return render(request, 'backoffice/zone_add.html')

@csrf_exempt
def zone_update(request, zone_id):
    """Met à jour une zone"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            zone = get_object_or_404(Zone, id=zone_id)

            ZoneService.update_zone(zone, data)

            return JsonResponse({'success': True, 'message': 'Zone mise à jour avec succès'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@csrf_exempt
def zone_delete(request, zone_id):
    """Supprime une zone"""
    if request.method == 'DELETE':
        try:
            zone = get_object_or_404(Zone, id=zone_id)
            ZoneService.delete_zone(zone)

            return JsonResponse({'success': True, 'message': 'Zone supprimée avec succès'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})
