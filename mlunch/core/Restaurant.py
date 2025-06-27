import psycopg2.errors
from typing import Optional, List, Dict, Any
from database.db import execute_query, fetch_query, fetch_one

class Restaurant:
    def __init__(
        self,
        id: Optional[int] = None,
        nom: Optional[str] = None,
        horaire_debut: Optional[str] = None,
        horaire_fin: Optional[str] = None,
        adresse: Optional[str] = None,
        image: Optional[str] = None,
        geo_position: Optional[str] = None  # WKT format string "POINT(lon lat)"
    ):
        self.id = id
        self.nom = nom
        self.horaire_debut = horaire_debut
        self.horaire_fin = horaire_fin
        self.adresse = adresse
        self.image = image
        self.geo_position = geo_position

    @staticmethod
    def Create(
        nom: str,
        horaire_debut: Optional[str],
        horaire_fin: Optional[str],
        adresse: str,
        image: Optional[str],
        geo_position: Optional[List[float]],  # [longitude, latitude]
        initial_statut_id: int
    ):
        if not nom or not isinstance(nom, str):
            return {"error": "Nom de restaurant invalide"}
        if not adresse or not isinstance(adresse, str):
            return {"error": "Adresse invalide"}
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "ID statut invalide"}

        try:
            point_wkt = None
            if geo_position and len(geo_position) == 2:
                point_wkt = f"POINT({geo_position[0]} {geo_position[1]})"

            query_restaurant = """
                INSERT INTO restaurants (nom, horaire_debut, horaire_fin, adresse, image, geo_position)
                VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
                RETURNING id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
            """
            result_restaurant, error = fetch_one(query_restaurant,
                (nom, horaire_debut, horaire_fin, adresse, image, point_wkt))

            if error:
                if isinstance(error, psycopg2.errors.UniqueViolation):
                    return {"error": "Restaurant déjà existant"}
                return {"error": f"Erreur création restaurant : {str(error)}"}
            if not result_restaurant:
                return {"error": "Échec de la création du restaurant"}

            restaurant_id = result_restaurant["id"]

            # Vérifier statut existe
            query_statut = "SELECT id FROM statut_restaurant WHERE id = %s"
            statut_res, error = fetch_one(query_statut, (initial_statut_id,))
            if error or not statut_res:
                return {"error": "Statut restaurant non trouvé"}

            # Insérer historique statut
            query_historique = """
                INSERT INTO historique_statut_restaurant (restaurant_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, restaurant_id, statut_id, mis_a_jour_le
            """
            hist_res, error = fetch_one(query_historique, (restaurant_id, initial_statut_id))
            if error or not hist_res:
                return {"error": f"Erreur création historique statut : {str(error)}"}

            restaurant = Restaurant(**result_restaurant)
            restaurant.historique_statut = dict(hist_res)
            return restaurant

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetById(restaurant_id: int):
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "ID restaurant invalide"}

        try:
            query = """
                SELECT 
                    r.id, r.nom, r.horaire_debut, r.horaire_fin, 
                    r.adresse, r.image, ST_AsText(r.geo_position) as geo_position
                FROM restaurants r
                WHERE r.id = %s
            """
            res, error = fetch_one(query, (restaurant_id,))
            if error:
                return {"error": str(error)}
            if not res:
                return None

            # Récupérer historique statuts
            query_hist = """
                SELECT h.id, h.statut_id, h.mis_a_jour_le, sr.appellation
                FROM historique_statut_restaurant h
                JOIN statut_restaurant sr ON h.statut_id = sr.id
                WHERE h.restaurant_id = %s
                ORDER BY h.mis_a_jour_le DESC
            """
            histos, error = fetch_query(query_hist, (restaurant_id,))
            if error:
                return {"error": str(error)}

            restaurant = Restaurant(**res)
            restaurant.historique_statut = [dict(h) for h in histos] if histos else []
            return restaurant

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetAll() -> List["Restaurant"]:
        query = """
            SELECT id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
            FROM restaurants
            ORDER BY nom
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": str(error)}]
        return [Restaurant(**row) for row in results]

    def Update(
        self,
        statut_id: Optional[int] = None,
        nom: Optional[str] = None,
        horaire_debut: Optional[str] = None,
        horaire_fin: Optional[str] = None,
        adresse: Optional[str] = None,
        image: Optional[str] = None,
        geo_position: Optional[List[float]] = None
    ):
        if not self.id or self.id <= 0:
            return {"error": "ID restaurant invalide"}

        if statut_id is not None and (not isinstance(statut_id, int) or statut_id <= 0):
            return {"error": "ID statut invalide"}

        if nom is not None and (not isinstance(nom, str) or len(nom) > 150):
            return {"error": "Nom invalide : max 150 caractères"}

        if adresse is not None and not isinstance(adresse, str):
            return {"error": "Adresse invalide"}

        if image is not None and not isinstance(image, str):
            return {"error": "Image invalide"}

        if geo_position is not None:
            if not isinstance(geo_position, (list, tuple)) or len(geo_position) != 2 \
               or not all(isinstance(x, (int, float)) for x in geo_position):
                return {"error": "Position géographique invalide"}

        try:
            # Vérifier existence
            check_q = "SELECT id FROM restaurants WHERE id = %s"
            res, error = fetch_one(check_q, (self.id,))
            if error or not res:
                return {"error": "Restaurant non trouvé"}

            # Vérifier statut si donné
            if statut_id is not None:
                check_statut_q = "SELECT id FROM statut_restaurant WHERE id = %s"
                res_statut, error = fetch_one(check_statut_q, (statut_id,))
                if error or not res_statut:
                    return {"error": "Statut restaurant non trouvé"}

            geo_wkt = None
            if geo_position is not None:
                geo_wkt = f"POINT({geo_position[0]} {geo_position[1]})"

            update_q = """
                UPDATE restaurants
                SET
                    nom = COALESCE(%s, nom),
                    horaire_debut = COALESCE(%s, horaire_debut),
                    horaire_fin = COALESCE(%s, horaire_fin),
                    adresse = COALESCE(%s, adresse),
                    image = COALESCE(%s, image),
                    geo_position = CASE WHEN %s IS NULL THEN geo_position ELSE ST_GeomFromText(%s, 4326) END
                WHERE id = %s
                RETURNING id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
            """
            res_upd, error = fetch_one(update_q, (
                nom, horaire_debut, horaire_fin, adresse, image, geo_wkt, geo_wkt, self.id
            ))
            if error:
                return {"error": f"Erreur mise à jour restaurant : {str(error)}"}

            self.__init__(**res_upd)

            # Ajouter historique statut si statut_id donné
            hist_res = None
            if statut_id is not None:
                hist_q = """
                    INSERT INTO historique_statut_restaurant (restaurant_id, statut_id)
                    VALUES (%s, %s)
                    RETURNING id, restaurant_id, statut_id, mis_a_jour_le
                """
                hist_res, error = fetch_one(hist_q, (self.id, statut_id))
                if error:
                    return {"error": f"Erreur insertion historique statut : {str(error)}"}

            self.historique_statut = dict(hist_res) if hist_res else None
            return self

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    def Delete(self, statut_id: int):
        if not self.id or self.id <= 0:
            return {"error": "ID restaurant invalide"}
        if not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "ID statut invalide"}

        try:
            query = """
                INSERT INTO historique_statut_restaurant (restaurant_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, restaurant_id, statut_id, mis_a_jour_le
            """
            result, error = fetch_one(query, (self.id, statut_id))
            if error:
                return {"error": str(error)}
            return {"success": True, "historique": dict(result)} if result else {"success": False}

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
