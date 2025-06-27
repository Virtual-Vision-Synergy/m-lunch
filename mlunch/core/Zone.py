import psycopg2.errors
from typing import Optional, List, Dict, Any
from database.db import execute_query, fetch_query, fetch_one

class Zone:
    def __init__(
        self,
        id: Optional[int] = None,
        nom: Optional[str] = None,
        description: Optional[str] = None,
        zone: Optional[str] = None  # WKT string "POLYGON(...)"
    ):
        self.id = id
        self.nom = nom
        self.description = description
        self.zone = zone  # WKT polygon string
        self.historique_statut: Optional[List[Dict[str, Any]]] = None

    @staticmethod
    def Create(
        nom: str,
        description: str,
        coordinates: List[List[float]],  # [[lon, lat], ...] minimum 3 points
        initial_statut_id: int
    ):
        if not isinstance(nom, str) or len(nom) > 100 or not nom.strip():
            return {"error": "Nom de zone invalide"}
        if not isinstance(description, str) or len(description) > 100:
            return {"error": "Description invalide"}
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "ID statut invalide"}
        if not isinstance(coordinates, list) or len(coordinates) < 3:
            return {"error": "Coordonnées du polygone invalides (minimum 3 points)"}

        try:
            polygon_wkt = "POLYGON((" + ",".join(f"{lon} {lat}" for lon, lat in coordinates) + "))"

            query_zone = """
                INSERT INTO zones (nom, description, zone)
                VALUES (%s, %s, ST_GeomFromText(%s, 4326))
                RETURNING id, nom, description, ST_AsText(zone) as zone
            """
            result_zone, error = fetch_one(query_zone, (nom, description, polygon_wkt))
            if error:
                if isinstance(error, psycopg2.errors.UniqueViolation):
                    return {"error": "Zone déjà existante"}
                return {"error": f"Erreur création zone : {str(error)}"}
            if not result_zone:
                return {"error": "Échec de la création de la zone"}

            zone_id = result_zone["id"]

            query_statut = "SELECT id FROM statut_zone WHERE id = %s"
            statut_res, error = fetch_one(query_statut, (initial_statut_id,))
            if error or not statut_res:
                return {"error": "Statut zone non trouvé"}

            query_historique = """
                INSERT INTO historique_statut_zone (zone_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, zone_id, statut_id, mis_a_jour_le
            """
            hist_res, error = fetch_one(query_historique, (zone_id, initial_statut_id))
            if error or not hist_res:
                return {"error": f"Erreur création historique statut : {str(error)}"}

            zone = Zone(**result_zone)
            zone.historique_statut = [dict(hist_res)]
            return zone

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetById(zone_id: int):
        if not isinstance(zone_id, int) or zone_id <= 0:
            return {"error": "ID zone invalide"}

        try:
            query_zone = """
                SELECT 
                    z.id, z.nom, z.description, ST_AsText(z.zone) as zone
                FROM zones z
                WHERE z.id = %s
            """
            zone_res, error = fetch_one(query_zone, (zone_id,))
            if error:
                return {"error": str(error)}
            if not zone_res:
                return None

            query_hist = """
                SELECT h.id, h.statut_id, h.mis_a_jour_le, sz.appellation
                FROM historique_statut_zone h
                JOIN statut_zone sz ON h.statut_id = sz.id
                WHERE h.zone_id = %s
                ORDER BY h.mis_a_jour_le DESC
            """
            histos, error = fetch_query(query_hist, (zone_id,))
            if error:
                return {"error": str(error)}

            zone = Zone(**zone_res)
            zone.historique_statut = [dict(h) for h in histos] if histos else []
            return zone

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetAll() -> List["Zone"]:
        query = """
            SELECT id, nom, description, ST_AsText(zone) as zone
            FROM zones
            ORDER BY nom
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": str(error)}]
        return [Zone(**row) for row in results]

    def Update(
        self,
        statut_id: Optional[int] = None,
        nom: Optional[str] = None,
        description: Optional[str] = None,
        coordinates: Optional[List[List[float]]] = None
    ):
        if not self.id or self.id <= 0:
            return {"error": "ID zone invalide"}

        if statut_id is not None and (not isinstance(statut_id, int) or statut_id <= 0):
            return {"error": "ID statut invalide"}

        if nom is not None and (not isinstance(nom, str) or len(nom) > 100):
            return {"error": "Nom invalide (100 caractères max)"}

        if description is not None and (not isinstance(description, str) or len(description) > 100):
            return {"error": "Description invalide (100 caractères max)"}

        if coordinates is not None:
            if not isinstance(coordinates, list) or len(coordinates) < 3:
                return {"error": "Coordonnées invalides (minimum 3 points)"}

        try:
            check_q = "SELECT id FROM zones WHERE id = %s"
            res_check, error = fetch_one(check_q, (self.id,))
            if error or not res_check:
                return {"error": "Zone non trouvée"}

            if statut_id is not None:
                check_statut_q = "SELECT id FROM statut_zone WHERE id = %s"
                res_statut, error = fetch_one(check_statut_q, (statut_id,))
                if error or not res_statut:
                    return {"error": "Statut zone non trouvé"}

            zone_wkt = None
            if coordinates is not None:
                zone_wkt = "POLYGON((" + ",".join(f"{lon} {lat}" for lon, lat in coordinates) + "))"

            update_q = """
                UPDATE zones
                SET
                    nom = COALESCE(%s, nom),
                    description = COALESCE(%s, description),
                    zone = CASE WHEN %s IS NULL THEN zone ELSE ST_GeomFromText(%s, 4326) END
                WHERE id = %s
                RETURNING id, nom, description, ST_AsText(zone) as zone
            """
            res_upd, error = fetch_one(update_q, (
                nom, description,
                zone_wkt, zone_wkt,
                self.id
            ))
            if error:
                return {"error": f"Erreur mise à jour zone : {str(error)}"}

            self.__init__(**res_upd)

            hist_res = None
            if statut_id is not None:
                hist_q = """
                    INSERT INTO historique_statut_zone (zone_id, statut_id)
                    VALUES (%s, %s)
                    RETURNING id, zone_id, statut_id, mis_a_jour_le
                """
                hist_res, error = fetch_one(hist_q, (self.id, statut_id))
                if error:
                    return {"error": f"Erreur insertion historique statut : {str(error)}"}

            self.historique_statut = [dict(hist_res)] if hist_res else None
            return self

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    def Delete(self, statut_id: int):
        if not self.id or self.id <= 0:
            return {"error": "ID zone invalide"}
        if not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "ID statut invalide"}

        try:
            query_check_zone = "SELECT id FROM zones WHERE id = %s"
            zone_exists, error = fetch_one(query_check_zone, (self.id,))
            if error or not zone_exists:
                return {"error": "Zone non trouvée"}

            query_check_statut = "SELECT id FROM statut_zone WHERE id = %s"
            statut_exists, error = fetch_one(query_check_statut, (statut_id,))
            if error or not statut_exists:
                return {"error": "Statut zone non trouvé"}

            query = """
                INSERT INTO historique_statut_zone (zone_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, zone_id, statut_id, mis_a_jour_le
            """
            result, error = fetch_one(query, (self.id, statut_id))
            if error:
                return {"error": str(error)}

            return {"success": True, "historique": dict(result)} if result else {"success": False}

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
