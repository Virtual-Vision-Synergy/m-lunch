import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_GET
import json

from mlunch.core.services import PanierService


def panier_view(request):
    """
    Vue principale du panier
    """
    client_id = request.session.get('client_id')

    if not client_id:
        client_id = 1  # ID de test - à remplacer par une redirection vers la connexion

    items = PanierService.get_panier_items(client_id)
    totals = PanierService.calculate_totals(client_id)

    points_recuperation = PanierService.get_points_recuperation(client_id)
    if isinstance(items, dict) and 'error' in items:
        items = []

    if isinstance(totals, dict) and 'error' in totals:
        totals = {'sous_total': 0, 'frais_livraison': 0, 'total': 0, 'nb_items': 0}

    if isinstance(points_recuperation, dict) and 'error' in points_recuperation:
        points_recuperation = []

    
    context = {
        'items': items,
        'totals': totals,
        'points_recuperation': points_recuperation,
        'client_id': client_id
    }

    return render(request, 'frontoffice/panier.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def add_to_panier(request):
    """
    Ajouter un repas au panier (commande en cours ou nouvelle commande).
    """
    try:
        data = json.loads(request.body)
        repas_id = data.get('repas_id')
        quantite = data.get('quantite', 1)

        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({
                'success': False,
                'message': 'Vous devez être connecté pour ajouter au panier'
            })

        result = PanierService.add_to_panier(client_id, repas_id, quantite)

        if 'error' in result:
            return JsonResponse({
                'success': False,
                'message': result['error']
            })

        return JsonResponse({
            'success': True,
            'message': result.get('message', 'Article ajouté au panier')
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })
        
@csrf_exempt
@require_http_methods(["POST"])
def update_quantity(request, item_id):
    """
    Mettre à jour la quantité d'un article
    """
    try:
        data = json.loads(request.body)
        nouvelle_quantite = data.get('quantite')

        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({
                'success': False,
                'message': 'Vous devez être connecté'
            })

        # Mettre à jour la quantité via le service
        result = PanierService.update_quantity(client_id, item_id, nouvelle_quantite)

        if 'error' in result:
            return JsonResponse({
                'success': False,
                'message': result['error']
            })

        # Récalculer les totaux
        totals = PanierService.calculate_totals(client_id)
        if isinstance(totals, dict) and 'error' in totals:
            totals = {'sous_total': 0, 'frais_livraison': 0, 'total': 0, 'nb_items': 0}

        return JsonResponse({
            'success': True,
            'message': result.get('message', 'Quantité mise à jour'),
            'totals': totals
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def remove_from_panier(request, item_id):
    """
    Supprimer un article du panier
    """
    try:
        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({
                'success': False,
                'message': 'Vous devez être connecté'
            })

        # Supprimer l'article via le service
        result = PanierService.remove_from_panier(client_id, item_id)

        if 'error' in result:
            return JsonResponse({
                'success': False,
                'message': result['error']
            })

        # Récalculer les totaux
        totals = PanierService.calculate_totals(client_id)
        if isinstance(totals, dict) and 'error' in totals:
            totals = {'sous_total': 0, 'frais_livraison': 0, 'total': 0, 'nb_items': 0}

        return JsonResponse({
            'success': True,
            'message': result.get('message', 'Article supprimé'),
            'totals': totals
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def clear_panier(request):
    """
    Vider complètement le panier
    """
    try:
        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({
                'success': False,
                'message': 'Vous devez être connecté'
            })

        # Vider le panier via le service
        result = PanierService.clear_panier(client_id)

        if 'error' in result:
            return JsonResponse({
                'success': False,
                'message': result['error']
            })

        return JsonResponse({
            'success': True,
            'message': result.get('message', 'Panier vidé avec succès')
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def validate_commande(request):
    """
    Valider la commande et procéder au paiement
    """
    try:
        data = json.loads(request.body)
        point_recup_id = data.get('point_recup_id')
        mode_paiement = data.get('mode_paiement')

        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({
                'success': False,
                'message': 'Vous devez être connecté pour valider une commande'
            })

        # Vérifier que le panier n'est pas vide
        totals = PanierService.calculate_totals(client_id)
        if isinstance(totals, dict) and 'error' in totals:
            return JsonResponse({
                'success': False,
                'message': totals['error']
            })

        if totals['nb_items'] == 0:
            return JsonResponse({
                'success': False,
                'message': 'Votre panier est vide'
            })

        # Valider la commande via le service
        success, message = PanierService.validate_commande(client_id, point_recup_id, mode_paiement)

        if success:
            return JsonResponse({
                'success': True,
                'message': message,
                'redirect_url': '/commandes/confirmation/'  # Page de confirmation
            })
        else:
            return JsonResponse({
                'success': False,
                'message': message
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


def get_panier_count(request):
    """
    Récupérer le nombre d'articles dans le panier (pour le badge)
    """
    try:
        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({'count': 0})

        # Calculer les totaux via le service
        totals = PanierService.calculate_totals(client_id)

        if isinstance(totals, dict) and 'error' in totals:
            return JsonResponse({'count': 0})

        # Calculer la quantité totale
        items = PanierService.get_panier_items(client_id)
        if isinstance(items, dict) and 'error' in items:
            return JsonResponse({'count': 0})

        quantite_totale = sum(item.get('quantite', 0) for item in items)

        return JsonResponse({
            'count': quantite_totale
        })

    except Exception as e:
        return JsonResponse({
            'count': 0
        })
        

@csrf_exempt
@require_http_methods(["POST"])
def finalize_commande(request):
    """
    Finalise la commande : met à jour le statut à 3, le point de récupération et le mode de paiement.
    """
    try:
        data = json.loads(request.body)
        point_recup_id = data.get('point_recup_id')
        mode_paiement_id = data.get('mode_paiement_id')

        # Récupérer l'ID du client depuis la session
        client_id = request.session.get('client_id')
        if not client_id:
            return JsonResponse({
                'success': False,
                'message': 'Vous devez être connecté pour finaliser la commande'
            })

        result = PanierService.finalize_commande(client_id, point_recup_id, mode_paiement_id)

        if 'error' in result:
            return JsonResponse({
                'success': False,
                'message': result['error']
            })

        return JsonResponse({
            'success': True,
            'message': result.get('message', 'Commande finalisée avec succès')
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@require_GET
def get_modes_paiement(request):
    """
    Récupère tous les modes de paiement disponibles.
    """
    try:
        modes = PanierService.get_all_modes_paiement()
        if isinstance(modes, dict) and 'error' in modes:
            return JsonResponse({'success': False, 'error': modes['error']})
        return JsonResponse({'success': True, 'modes': list(modes)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
@staticmethod
def get_points_recuperation(client_id):
    """
    Récupère les points de récupération dans un rayon de 3.5 km du centre des zones du client.
    """
    try:
        from shapely import wkt
        from shapely.geometry import Point
        import math

        # 1️⃣ Zones du client
        zones = ZoneClient.objects.filter(client_id=client_id).select_related('zone')
        if not zones:
            return {"error": "Le client n'a aucune zone associée."}

        points_dans_rayon = []
        rayon_km = 3.5

        # 2️⃣ Pour chaque zone du client
        for zone_client in zones:
            zone = zone_client.zone
            
            try:
                # Calculer le centre de la zone (centroïde du polygone)
                if zone.zone:
                    poly = wkt.loads(zone.zone)
                    centre_zone = poly.centroid
                    centre_lat = centre_zone.y
                    centre_lon = centre_zone.x
                    
                    # 3️⃣ Récupérer tous les points de récupération
                    tous_points = PointRecup.objects.all()
                    
                    for point in tous_points:
                        if point.geo_position and point.geo_position != "0,0":
                            try:
                                # Extraire les coordonnées du point (format: "lat,lon")
                                coords = point.geo_position.split(',')
                                if len(coords) == 2:
                                    point_lat = float(coords[0])
                                    point_lon = float(coords[1])
                                    
                                    # Calculer la distance en km en utilisant la formule de Haversine
                                    distance_km = PanierService._calculate_distance(
                                        centre_lat, centre_lon, point_lat, point_lon
                                    )
                                    
                                    # Si le point est dans le rayon, l'ajouter
                                    if distance_km <= rayon_km:
                                        point_info = {
                                            'id': point.id,
                                            'nom': point.nom,
                                            'geo_position': point.geo_position,
                                            'distance_km': round(distance_km, 2),
                                            'zone_nom': zone.nom
                                        }
                                        # Éviter les doublons
                                        if not any(p['id'] == point.id for p in points_dans_rayon):
                                            points_dans_rayon.append(point_info)
                            except (ValueError, IndexError):
                                continue
            except Exception as e:
                print(f"Erreur lors du traitement de la zone {zone.nom}: {str(e)}")
                continue

        # 4️⃣ Trier par distance
        points_dans_rayon.sort(key=lambda x: x['distance_km'])
        
        return points_dans_rayon

    except Exception as e:
        return {"error": f"Erreur lors de la récupération des points de récupération : {str(e)}"}

@staticmethod
def _calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calcule la distance entre deux points géographiques en utilisant la formule de Haversine.
    Retourne la distance en kilomètres.
    """
    # Rayon de la Terre en km
    R = 6371.0
    
    # Convertir les degrés en radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Différences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Formule de Haversine
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    # Distance en km
    distance = R * c
    return distance