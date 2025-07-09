from mlunch.core.models import PointRecup


class PointRecupService:
    @staticmethod
    def get_all_points_recup_geojson():
        from .geo_distance_service import GeoDistanceService

        points = PointRecup.objects.all()
        features = []
        for point in points:
            if not point.geo_position:
                continue

            # Utiliser la fonction de parsing améliorée
            coords = GeoDistanceService.parse_coordinates(point.geo_position)
            if not coords:
                continue

            lat, lng = coords

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat],  # GeoJSON format: [longitude, latitude]
                },
                "properties": {
                    "id": point.id,
                    "nom": point.nom,
                }
            })
        return {
            "type": "FeatureCollection",
            "features": features
        }
