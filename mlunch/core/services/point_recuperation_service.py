from mlunch.core.models import PointRecup


class PointRecupService:
    @staticmethod
    def get_all_points_recup_geojson():
        points = PointRecup.objects.all()
        features = []
        for point in points:
            if not point.geo_position:
                continue
            try:
                # Ex: "POINT(47.5310 -18.9120)"
                coords_str = point.geo_position.replace("POINT(", "").replace(")", "")
                x_str, y_str = coords_str.split()
                x, y = float(x_str), float(y_str)
            except Exception:
                continue
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [x, y],
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

