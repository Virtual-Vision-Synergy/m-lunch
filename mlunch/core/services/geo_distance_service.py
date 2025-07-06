import math
from typing import Tuple, Optional


class GeoDistanceService:
    """
    Service pour calculer les distances géographiques entre points
    """

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcule la distance en kilomètres entre deux points géographiques
        en utilisant la formule de Haversine

        Args:
            lat1, lon1: Latitude et longitude du premier point
            lat2, lon2: Latitude et longitude du second point

        Returns:
            Distance en kilomètres
        """
        # Rayon de la Terre en kilomètres
        R = 6371.0

        # Conversion en radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Différences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Formule de Haversine
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    @staticmethod
    def parse_coordinates(geo_position: str) -> Optional[Tuple[float, float]]:
        """
        Parse une chaîne de coordonnées au format "latitude,longitude"

        Args:
            geo_position: Chaîne au format "lat,lng"

        Returns:
            Tuple (latitude, longitude) ou None si erreur
        """
        try:
            if not geo_position or geo_position == "0,0":
                return None

            coords = geo_position.split(',')
            if len(coords) != 2:
                return None

            lat = float(coords[0].strip())
            lng = float(coords[1].strip())

            # Vérification des limites valides
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return (lat, lng)
            else:
                return None

        except (ValueError, AttributeError):
            return None

    @staticmethod
    def calculate_delivery_distance(livreur_geo_position: str, point_recup_geo_position: str) -> dict:
        """
        Calcule la distance de livraison entre un livreur et un point de récupération

        Args:
            livreur_geo_position: Position géographique du livreur
            point_recup_geo_position: Position géographique du point de récupération

        Returns:
            Dictionnaire contenant les informations de distance
        """
        # Parser les coordonnées du livreur
        livreur_coords = GeoDistanceService.parse_coordinates(livreur_geo_position)
        if not livreur_coords:
            return {
                'error': 'Position du livreur invalide ou non définie',
                'distance_km': 0,
                'temps_estime_min': 0
            }

        # Parser les coordonnées du point de récupération
        point_coords = GeoDistanceService.parse_coordinates(point_recup_geo_position)
        if not point_coords:
            return {
                'error': 'Position du point de récupération invalide ou non définie',
                'distance_km': 0,
                'temps_estime_min': 0
            }

        # Calculer la distance
        distance_km = GeoDistanceService.haversine_distance(
            livreur_coords[0], livreur_coords[1],
            point_coords[0], point_coords[1]
        )

        # Estimer le temps de trajet (en supposant une vitesse moyenne de 25 km/h pour un livreur)
        vitesse_moyenne_kmh = 25
        temps_estime_min = (distance_km / vitesse_moyenne_kmh) * 60

        return {
            'distance_km': round(distance_km, 2),
            'temps_estime_min': round(temps_estime_min, 1),
            'livreur_coords': livreur_coords,
            'point_coords': point_coords
        }

    @staticmethod
    def calculate_multi_stop_distance(livreur_geo_position: str, restaurants_positions: list, point_recup_geo_position: str) -> dict:
        """
        Calcule la distance totale pour une livraison multi-restaurants

        Args:
            livreur_geo_position: Position du livreur
            restaurants_positions: Liste des positions des restaurants
            point_recup_geo_position: Position du point de récupération

        Returns:
            Dictionnaire avec les informations de distance totale
        """
        livreur_coords = GeoDistanceService.parse_coordinates(livreur_geo_position)
        if not livreur_coords:
            return {
                'error': 'Position du livreur invalide',
                'distance_totale_km': 0,
                'temps_estime_min': 0,
                'nombre_restaurants': 0
            }

        point_coords = GeoDistanceService.parse_coordinates(point_recup_geo_position)
        if not point_coords:
            return {
                'error': 'Position du point de récupération invalide',
                'distance_totale_km': 0,
                'temps_estime_min': 0,
                'nombre_restaurants': 0
            }

        distance_totale = 0
        position_actuelle = livreur_coords
        restaurants_valides = []

        # Calculer le trajet optimal (simple : dans l'ordre donné)
        for resto_position in restaurants_positions:
            resto_coords = GeoDistanceService.parse_coordinates(resto_position)
            if resto_coords:
                distance_totale += GeoDistanceService.haversine_distance(
                    position_actuelle[0], position_actuelle[1],
                    resto_coords[0], resto_coords[1]
                )
                position_actuelle = resto_coords
                restaurants_valides.append(resto_coords)

        # Distance du dernier restaurant au point de récupération
        if position_actuelle != livreur_coords:  # Si au moins un restaurant visité
            distance_totale += GeoDistanceService.haversine_distance(
                position_actuelle[0], position_actuelle[1],
                point_coords[0], point_coords[1]
            )
        else:
            # Direct du livreur au point de récupération
            distance_totale = GeoDistanceService.haversine_distance(
                livreur_coords[0], livreur_coords[1],
                point_coords[0], point_coords[1]
            )

        # Estimation du temps (avec arrêts)
        vitesse_moyenne_kmh = 20  # Plus lent avec les arrêts
        temps_trajet = (distance_totale / vitesse_moyenne_kmh) * 60
        temps_arrets = len(restaurants_valides) * 5  # 5 min par restaurant
        temps_total = temps_trajet + temps_arrets

        return {
            'distance_totale_km': round(distance_totale, 2),
            'temps_estime_min': round(temps_total, 1),
            'nombre_restaurants': len(restaurants_valides),
            'restaurants_visites': len(restaurants_valides)
        }
