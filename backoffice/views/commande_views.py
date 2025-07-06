from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from mlunch.core.services.commande_service import CommandeService
from mlunch.core.models import Commande, StatutCommande
import json

def commande_list(request):
    """Liste toutes les commandes pour le backoffice"""
    commandes = CommandeService.get_all_commandes()
    statuts = StatutCommande.objects.all()

    # Filtrage par statut si spécifié
    statut_id = request.GET.get('statut')
    if statut_id:
        commandes = commandes.filter(statut_id=statut_id)

    return render(request, 'backoffice/commande.html', {
        'commandes': commandes,
        'statuts': statuts,
        'selected_statut': int(statut_id) if statut_id else None
    })

def commande_detail(request, commande_id):
    """Détail d'une commande spécifique"""
    commande = get_object_or_404(Commande, id=commande_id)
    return render(request, 'backoffice/commande_detail.html', {
        'commande': commande
    })

@csrf_exempt
def commande_update_statut(request, commande_id):
    """Met à jour le statut d'une commande"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nouveau_statut_id = data.get('statut_id')

            commande = get_object_or_404(Commande, id=commande_id)
            CommandeService.update_statut_commande(commande, nouveau_statut_id)

            return JsonResponse({'success': True, 'message': 'Statut mis à jour avec succès'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

def commandes_en_attente(request):
    """Liste des commandes en attente pour le dashboard"""
    commandes = CommandeService.get_commandes_en_attente()
    return render(request, 'backoffice/commandes_en_attente.html', {
        'commandes': commandes
    })

def commande_attribuer(request, commande_id):
    """Page d'attribution d'une commande à un livreur"""
    from mlunch.core.models import Livreur, ZoneLivreur, ZoneClient, Restaurant, CommandeRepas, RestaurantRepas
    from mlunch.core.services.distance_service import DistanceService
    from mlunch.core.services.zone_service import ZoneService
    from mlunch.core.services.geo_distance_service import GeoDistanceService

    commande = get_object_or_404(Commande, id=commande_id)

    # Récupérer la position du point de récupération de la commande
    point_recup = commande.point_recup
    livreurs_disponibles = []
    zones_couvertes = []

    if point_recup and point_recup.geo_position:
        try:
            # Parser les coordonnées du point de récupération (format "lat,lng")
            coords = point_recup.geo_position.split(',')
            if len(coords) == 2:
                lat = float(coords[0].strip())
                lng = float(coords[1].strip())

                # Récupérer TOUTES les zones qui couvrent ce point
                zones_trouvees = ZoneService.get_zones_by_coord(lat, lng)

                if zones_trouvees:
                    zone_ids = [zone['id'] for zone in zones_trouvees]
                    zones_couvertes = zones_trouvees

                    # Récupérer tous les livreurs de toutes ces zones (sans doublons)
                    livreurs_zone = ZoneLivreur.objects.filter(
                        zone_id__in=zone_ids
                    ).select_related('livreur', 'zone').distinct()

                    # Créer un dictionnaire pour éviter les doublons de livreurs
                    livreurs_dict = {}
                    for zl in livreurs_zone:
                        if zl.livreur.id not in livreurs_dict:
                            livreurs_dict[zl.livreur.id] = {
                                'livreur': zl.livreur,
                                'zones': []
                            }
                        livreurs_dict[zl.livreur.id]['zones'].append(zl.zone.nom)

                    livreurs_disponibles = list(livreurs_dict.values())

        except (ValueError, IndexError) as e:
            # Si erreur de parsing des coordonnées, continuer avec la logique de fallback
            pass

    # Fallback : si pas de zones trouvées ou erreur, utiliser l'ancienne logique
    if not livreurs_disponibles:
        try:
            zone_client = ZoneClient.objects.get(client=commande.client)
            zone = zone_client.zone
            livreurs_zone = ZoneLivreur.objects.filter(zone=zone).select_related('livreur')
            livreurs_disponibles = [{'livreur': zl.livreur, 'zones': [zone.nom]} for zl in livreurs_zone]
            zones_couvertes = [{'id': zone.id, 'nom': zone.nom, 'distance': 0}]
        except ZoneClient.DoesNotExist:
            # Si le client n'a pas de zone définie, récupérer tous les livreurs
            tous_livreurs = Livreur.objects.all()
            livreurs_disponibles = [{'livreur': livreur, 'zones': ['Toutes zones']} for livreur in tous_livreurs]
            zones_couvertes = []

    # Calculer la distance pour chaque livreur en utilisant les coordonnées géographiques
    livreurs_avec_distance = []
    for livreur_data in livreurs_disponibles:
        livreur = livreur_data['livreur']

        # Nouveau calcul basé sur les coordonnées géographiques
        if livreur.geo_position and point_recup.geo_position:
            # Récupérer les restaurants de la commande pour calcul multi-stops
            commande_repas = CommandeRepas.objects.filter(commande=commande).select_related('repas')
            restaurants_positions = []

            for cr in commande_repas:
                # Trouver les restaurants qui servent ce repas
                restaurant_repas = RestaurantRepas.objects.filter(repas=cr.repas).select_related('restaurant')
                for rr in restaurant_repas:
                    if rr.restaurant.geo_position and rr.restaurant.geo_position != "0,0":
                        restaurants_positions.append(rr.restaurant.geo_position)

            # Supprimer les doublons de restaurants
            restaurants_positions = list(set(restaurants_positions))

            if restaurants_positions:
                # Calcul multi-stops (livreur -> restaurants -> point de récupération)
                distance_info = GeoDistanceService.calculate_multi_stop_distance(
                    livreur.geo_position,
                    restaurants_positions,
                    point_recup.geo_position
                )
                livreur_final = {
                    'livreur': livreur,
                    'zones': livreur_data['zones'],
                    'distance_totale': distance_info.get('distance_totale_km', 0),
                    'temps_estime': distance_info.get('temps_estime_min', 0),
                    'nombre_restaurants': distance_info.get('nombre_restaurants', 0),
                    'error': distance_info.get('error', None),
                    'calcul_type': 'géographique'
                }
            else:
                # Calcul direct (livreur -> point de récupération)
                distance_info = GeoDistanceService.calculate_delivery_distance(
                    livreur.geo_position,
                    point_recup.geo_position
                )
                livreur_final = {
                    'livreur': livreur,
                    'zones': livreur_data['zones'],
                    'distance_totale': distance_info.get('distance_km', 0),
                    'temps_estime': distance_info.get('temps_estime_min', 0),
                    'nombre_restaurants': 0,
                    'error': distance_info.get('error', None),
                    'calcul_type': 'géographique'
                }
        else:
            # Fallback vers l'ancien système si pas de coordonnées géographiques
            try:
                distance_info = DistanceService.get_distance(livreur.id, commande_id)
                livreur_final = {
                    'livreur': livreur,
                    'zones': livreur_data['zones'],
                    'distance_totale': distance_info.get('distance_totale', 0),
                    'temps_estime': distance_info.get('temps_estime', 0),
                    'nombre_restaurants': distance_info.get('nombre_restaurants', 0),
                    'error': distance_info.get('error', None),
                    'calcul_type': 'ancien système'
                }
            except:
                livreur_final = {
                    'livreur': livreur,
                    'zones': livreur_data['zones'],
                    'distance_totale': 0,
                    'temps_estime': 0,
                    'nombre_restaurants': 0,
                    'error': 'Impossible de calculer la distance',
                    'calcul_type': 'erreur'
                }

        livreurs_avec_distance.append(livreur_final)

    # Trier les livreurs par distance (les plus proches en premier)
    livreurs_avec_distance.sort(key=lambda x: x['distance_totale'])

    return render(request, 'backoffice/commande_attribuer.html', {
        'commande': commande,
        'livreurs_avec_distance': livreurs_avec_distance,
        'zones_couvertes': zones_couvertes,
        'nombre_zones': len(zones_couvertes),
        'nombre_livreurs': len(livreurs_avec_distance)
    })

def commande_attribuer_confirmer(request, commande_id):
    """Confirme l'attribution d'une commande à un livreur"""
    from mlunch.core.services.livraison_service import LivraisonService
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"Début de commande_attribuer_confirmer pour commande {commande_id}")

    if request.method == 'POST':
        commande = get_object_or_404(Commande, id=commande_id)
        livreur_id = request.POST.get('livreur_id')

        logger.info(f"POST reçu - commande: {commande_id}, livreur_id: {livreur_id}")

        if not livreur_id:
            logger.warning("Aucun livreur sélectionné")
            messages.error(request, 'Veuillez sélectionner un livreur.')
            return redirect('commande_attribuer', commande_id=commande_id)

        try:
            logger.info(f"Tentative de création de livraison - livreur: {livreur_id}, commande: {commande_id}")
            # Utiliser le service de livraison pour créer la livraison
            result = LivraisonService.create_livraison(livreur_id, commande_id)

            logger.info(f"Résultat du service: {result}")

            if "error" in result:
                logger.error(f"Erreur du service: {result['error']}")
                messages.error(request, result["error"])
                return redirect('commande_attribuer', commande_id=commande_id)

            # Succès
            logger.info(f"Attribution réussie, redirection vers index")
            messages.success(request, f'Commande #{commande.id} attribuée avec succès à {result["livraison"]["livreur"]}.')
            return redirect('index')

        except Exception as e:
            logger.error(f"Exception lors de l'attribution: {str(e)}")
            messages.error(request, f'Erreur lors de l\'attribution : {str(e)}')
            return redirect('commande_attribuer', commande_id=commande_id)

    logger.info("Méthode non POST, redirection vers commande_attribuer")
    return redirect('commande_attribuer', commande_id=commande_id)
