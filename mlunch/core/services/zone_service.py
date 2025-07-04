import pdb
from shapely import wkt
from shapely.geometry import Point


from ..models import Zone, StatutZone, HistoriqueStatutZone


class ZoneService:
    @staticmethod
    def create_zone(nom, description, coordinates, initial_statut_id):
<<<<<<< Updated upstream
        # pdb.set_trace()
=======
        #pdb.set_trace()
>>>>>>> Stashed changes
        from django.db import transaction
        if not nom or len(nom) > 100 or not nom.strip():
            return {"error": "Nom de zone invalide"}
        if not isinstance(description, str) or len(description) > 200:
            return {"error": "Description invalide"}
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "ID statut invalide"}
        if not isinstance(coordinates, list) or len(coordinates) < 3:
            return {"error": "Coordonnées du polygone invalides (minimum 3 points)"}
        try:
            with transaction.atomic():
                if not StatutZone.objects.filter(id=initial_statut_id).exists():
                    return {"error": "Statut zone non trouvé"}
                polygon_wkt = "POLYGON((" + ",".join([f"{lon} {lat}" for lon, lat in coordinates]) + "))"
                zone = Zone.objects.create(
                    nom=nom,
                    description=description,
                    zone=polygon_wkt
                )
                historique = HistoriqueStatutZone.objects.create(
                    zone=zone,
                    statut_id=initial_statut_id
                )
                return {
                    "zone": {
                        "id": zone.id,
                        "nom": zone.nom,
                        "description": zone.description,
                        "zone": zone.zone
                    },
                    "historique": {
                        "id": historique.id,
                        "zone_id": historique.zone_id,
                        "statut_id": historique.statut_id,
                        "mis_a_jour_le": historique.mis_a_jour_le
                    }
                }
        except Exception as e:
            return {"error": f"Erreur lors de la création de la zone : {str(e)}"}

    @staticmethod
    def get_zone_by_coord(lat, lon, max_distance_m=5000):
        #pdb.set_trace()
        """
        Retourne la zone contenant ou la plus proche (à < max_distance_m) d'un point (lat, lon).
        """
        point = Point(float(lon), float(lat))
        closest_zone = None
        closest_dist = None
        for zone in Zone.objects.all():
            try:
                poly = wkt.loads(zone.zone)
                if poly.contains(point):
                    return {'id': zone.id, 'nom': zone.nom}
                dist = poly.distance(point) * 111320
                if closest_dist is None or dist < closest_dist:
                    closest_zone = zone
                    closest_dist = dist
            except Exception:
                continue
        if closest_zone and closest_dist < max_distance_m:
            return {'id': closest_zone.id, 'nom': closest_zone.nom}
        return None

    @staticmethod
    def list_zones_actives():
<<<<<<< Updated upstream
        # pdb.set_trace()
=======
        #pdb.set_trace()
>>>>>>> Stashed changes
        """Liste toutes les zones actives (dernier statut = actif)."""
        try:
            actifs = []
            for z in Zone.objects.all():
                dernier_statut = z.historiques.order_by('-mis_a_jour_le').first()
                if dernier_statut and dernier_statut.statut.appellation and dernier_statut.statut.appellation.lower() == "actif":
                    actifs.append({
                        "id": z.id,
                        "nom": z.nom,
                        "description": z.description,
                        "zone": z.zone
                    })
            return actifs
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des zones actives : {str(e)}"}

    @staticmethod
    def get_all_zones():
        """
        Retourne la liste de toutes les zones (secteurs) disponibles.
        """
        try:
            return list(Zone.objects.values('id', 'nom', 'description', 'zone'))
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des zones : {str(e)}"}
