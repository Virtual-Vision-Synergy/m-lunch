from mlunch.core.models import PointRecup


class PointRecupService:
    @staticmethod
    def get_all_points_recup_geojson():
        # points = PointRecup.objects.all()
        # features = []
        # for point in points:
        #     if not point.geo_position:
        #         continue
        #     features.append({
        #         "type": "Feature",
        #         "geometry": {
        #             "type": "Point",
        #             "coordinates": [point.geo_position.x, point.geo_position.y],
        #         },
        #         "properties": {
        #             "id": point.id,
        #             "nom": point.nom,
        #         }
        #     })
        # return {
        #     "type": "FeatureCollection",
        #     "features": features
        # }
        pass