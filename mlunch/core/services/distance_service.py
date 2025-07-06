import math
from typing import List, Tuple
from mlunch.core.models import Livreur, Commande, Restaurant, PointRecup, CommandeRepas, RestaurantRepas

class DistanceService:
    @staticmethod
    def parse_coordinates(coord_string: str) -> Tuple[float, float]:
        """Parse une chaîne de coordonnées 'lat,lng' en tuple (lat, lng)"""
        try:
            if not coord_string or coord_string == "0,0":
                return (0.0, 0.0)
            parts = coord_string.split(',')
            if len(parts) != 2:
                return (0.0, 0.0)
            return (float(parts[0].strip()), float(parts[1].strip()))
        except (ValueError, AttributeError):
            return (0.0, 0.0)

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcule la distance entre deux points géographiques en utilisant la formule de Haversine.
        Retourne la distance en kilomètres.
        """
        # Rayon de la Terre en kilomètres
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

        # Distance en kilomètres
        distance = R * c
        return distance

    @staticmethod
    def get_restaurants_for_commande(commande_id: int) -> List[Restaurant]:
        """
        Récupère tous les restaurants uniques qui préparent des plats pour une commande donnée.
        """
        try:
            # Récupérer tous les repas de la commande
            repas_commandes = CommandeRepas.objects.filter(commande_id=commande_id).select_related('repas')

            # Récupérer les restaurants correspondants
            restaurants = []
            restaurants_ids = set()

            for repas_commande in repas_commandes:
                # Trouver le restaurant qui sert ce repas
                restaurant_repas = RestaurantRepas.objects.filter(repas=repas_commande.repas).select_related('restaurant').first()
                if restaurant_repas and restaurant_repas.restaurant.id not in restaurants_ids:
                    restaurants.append(restaurant_repas.restaurant)
                    restaurants_ids.add(restaurant_repas.restaurant.id)

            return restaurants
        except Exception as e:
            print(f"Erreur lors de la récupération des restaurants: {str(e)}")
            return []

    @staticmethod
    def get_distance(livreur_id: int, commande_id: int) -> dict:
        """
        Calcule la distance totale qu'un livreur doit parcourir pour effectuer une commande.

        Parcours:
        1. Position du livreur -> Chaque restaurant (pour récupérer les plats)
        2. Dernier restaurant -> Point de récupération

        Retourne un dictionnaire avec les détails du parcours et la distance totale.
        """
        try:
            # Récupérer le livreur
            livreur = Livreur.objects.get(id=livreur_id)
            livreur_lat, livreur_lng = DistanceService.parse_coordinates(livreur.position)

            # Récupérer la commande
            commande = Commande.objects.select_related('point_recup').get(id=commande_id)
            point_recup_lat, point_recup_lng = DistanceService.parse_coordinates(commande.point_recup.geo_position)

            # Récupérer tous les restaurants concernés par la commande
            restaurants = DistanceService.get_restaurants_for_commande(commande_id)

            if not restaurants:
                return {
                    'error': 'Aucun restaurant trouvé pour cette commande',
                    'distance_totale': 0,
                    'parcours': []
                }

            # Calculer le parcours optimisé (simple: dans l'ordre des restaurants)
            parcours = []
            distance_totale = 0
            current_lat, current_lng = livreur_lat, livreur_lng

            # Étape 1: Aller vers chaque restaurant
            for i, restaurant in enumerate(restaurants):
                rest_lat, rest_lng = DistanceService.parse_coordinates(restaurant.geo_position)

                # Calculer la distance depuis la position actuelle
                distance = DistanceService.haversine_distance(current_lat, current_lng, rest_lat, rest_lng)

                parcours.append({
                    'etape': i + 1,
                    'type': 'restaurant',
                    'nom': restaurant.nom,
                    'adresse': restaurant.adresse or 'Adresse non définie',
                    'coordinates': f"{rest_lat},{rest_lng}",
                    'distance_depuis_precedent': round(distance, 2),
                    'distance_cumulee': round(distance_totale + distance, 2)
                })

                distance_totale += distance
                current_lat, current_lng = rest_lat, rest_lng

            # Étape 2: Aller vers le point de récupération
            distance_finale = DistanceService.haversine_distance(current_lat, current_lng, point_recup_lat, point_recup_lng)

            parcours.append({
                'etape': len(restaurants) + 1,
                'type': 'point_recup',
                'nom': commande.point_recup.nom,
                'adresse': 'Point de récupération',
                'coordinates': f"{point_recup_lat},{point_recup_lng}",
                'distance_depuis_precedent': round(distance_finale, 2),
                'distance_cumulee': round(distance_totale + distance_finale, 2)
            })

            distance_totale += distance_finale

            return {
                'livreur': livreur.nom,
                'commande_id': commande_id,
                'distance_totale': round(distance_totale, 2),
                'nombre_restaurants': len(restaurants),
                'parcours': parcours,
                'temps_estime': round(distance_totale * 4, 0)  # Estimation: 4 minutes par km
            }

        except Livreur.DoesNotExist:
            return {
                'error': 'Livreur non trouvé',
                'distance_totale': 0,
                'parcours': []
            }
        except Commande.DoesNotExist:
            return {
                'error': 'Commande non trouvée',
                'distance_totale': 0,
                'parcours': []
            }
        except Exception as e:
            return {
                'error': f'Erreur lors du calcul: {str(e)}',
                'distance_totale': 0,
                'parcours': []
            }

    @staticmethod
    def get_distance_simple(livreur_id: int, commande_id: int) -> float:
        """
        Version simplifiée qui retourne seulement la distance totale en km.
        """
        result = DistanceService.get_distance(livreur_id, commande_id)
        return result.get('distance_totale', 0)
