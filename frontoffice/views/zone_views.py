from django.http import JsonResponse

from mlunch.core.services import ZoneService, PointRecupService


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

def points_de_recuperation(request):
    data = PointRecupService.get_all_points_recup_geojson()
    return JsonResponse(data)