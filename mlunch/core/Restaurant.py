import psycopg2.errors
from typing import Optional, Dict, List, Any, Tuple
from database.db import execute_query, fetch_query, fetch_one

class Restaurant:
    """Classe représentant un restaurant dans le système."""

    @staticmethod
    def create(nom, horaire_debut, horaire_fin, adresse, image, geo_position, initial_statut_id):
        """Crée un nouveau restaurant avec son historique et statut initial."""
        # Validation des entrées
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "ID statut invalide"}
        if not nom or not isinstance(nom, str):
            return {"error": "Nom de restaurant invalide"}
        if not adresse or not isinstance(adresse, str):
            return {"error": "Adresse invalide"}

        # Démarrer une transaction
        try:
            # Insérer le restaurant
            query_restaurant = """
                INSERT INTO restaurants (nom, horaire_debut, horaire_fin, adresse, image, geo_position)
                VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
                RETURNING id, nom, horaire_debut, horaire_fin, adresse, image, geo_position
            """
            point_wkt = f"POINT({geo_position[0]} {geo_position[1]})" if geo_position else None
            
            result_restaurant, error = fetch_one(query_restaurant, 
                                            (nom, horaire_debut, horaire_fin, adresse, image, point_wkt))
            
            if error:
                return {"error": f"Erreur lors de la création du restaurant : {str(error)}"}
            if not result_restaurant:
                return {"error": "Échec de la création du restaurant"}

            restaurant_id = result_restaurant['id']

            # Vérifier si le statut existe
            query_statut = """
                SELECT id FROM statut_restaurant WHERE id = %s
            """
            result_statut, error = fetch_one(query_statut, (initial_statut_id,))
            if error or not result_statut:
                return {"error": "Statut restaurant non trouvé"}

            # Insérer dans l'historique
            query_historique = """
                INSERT INTO historique_statut_restaurant (restaurant_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, restaurant_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (restaurant_id, initial_statut_id))
            if error:
                return {"error": f"Erreur lors de la création de l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de la création de l'historique"}

            # Retourner les informations complètes
            return {
                "restaurant": dict(result_restaurant),
                "historique": dict(result_historique)
            }

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def get_by_id(restaurant_id):
        """
        Récupère un restaurant par son ID avec son historique complet des statuts.
        
        Args:
            restaurant_id (int): L'ID du restaurant à récupérer.
        
        Returns:
            dict: Dictionnaire avec:
                - 'restaurant': les infos du restaurant
                - 'statuts': liste des statuts historiques
                En cas d'erreur, retourne un dictionnaire avec une clé 'error'.
        """
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "ID restaurant invalide"}

        try:
            # Requête pour les infos du restaurant
            query_restaurant = """
                SELECT 
                    r.id, r.nom, r.horaire_debut, r.horaire_fin, 
                    r.adresse, r.image, ST_AsText(r.geo_position) as geo_position,
                    sr.appellation as statut_actuel
                FROM restaurants r
                LEFT JOIN (
                    SELECT restaurant_id, statut_id
                    FROM historique_statut_restaurant
                    WHERE id = (
                        SELECT MAX(id) 
                        FROM historique_statut_restaurant 
                        WHERE restaurant_id = %s
                    )
                ) latest ON r.id = latest.restaurant_id
                LEFT JOIN statut_restaurant sr ON latest.statut_id = sr.id
                WHERE r.id = %s
            """
            
            # Requête pour l'historique des statuts
            query_historique = """
                SELECT 
                    h.id, h.statut_id, h.mis_a_jour_le,
                    sr.appellation as statut_nom
                FROM historique_statut_restaurant h
                JOIN statut_restaurant sr ON h.statut_id = sr.id
                WHERE h.restaurant_id = %s
                ORDER BY h.mis_a_jour_le DESC
            """

            # Exécution des requêtes
            restaurant, error = fetch_one(query_restaurant, (restaurant_id, restaurant_id))
            if error or not restaurant:
                return {"error": "Restaurant non trouvé" if not error else f"Erreur : {str(error)}"}
            
            historiques, error = fetch_query(query_historique, (restaurant_id,))
            if error:
                return {"error": f"Erreur historique : {str(error)}"}

            # Formatage des résultats
            result = {
                "restaurant": dict(restaurant),
                "statuts": [dict(h) for h in historiques] if historiques else []
            }
            
            return result

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
            """Récupère tous les restaurants."""
            query = """
                SELECT id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
                FROM restaurants
                ORDER BY nom
            """
            results, error = fetch_query(query)
            if error:
                return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
            return [dict(row) for row in results]

    @staticmethod
    def update(restaurant_id, statut_id=None, nom=None, horaire_debut=None, horaire_fin=None, 
                     adresse=None, image=None, geo_position=None):
        """
        Met à jour un restaurant et son historique de statut.
        Retourne les données mises à jour ou un dictionnaire d'erreur.
        """
        # Validation des paramètres
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "ID restaurant invalide"}
        if statut_id is not None and (not isinstance(statut_id, int) or statut_id <= 0):
            return {"error": "ID statut invalide"}
        if nom is not None and (not isinstance(nom, str) or len(nom) > 150):
            return {"error": "Nom invalide : doit être une chaîne de 150 caractères maximum"}
        if adresse is not None and not isinstance(adresse, str):
            return {"error": "Adresse invalide : doit être une chaîne"}
        if image is not None and not isinstance(image, str):
            return {"error": "Image invalide : doit être une chaîne"}
        if geo_position is not None and (
            not isinstance(geo_position, (tuple, list)) or 
            len(geo_position) != 2 or 
            not all(isinstance(x, (int, float)) for x in geo_position)
        ):
            return {"error": "Position géographique invalide : doit être un tuple (longitude, latitude)"}

        try:
            # Vérifier si le restaurant existe
            query_check_restaurant = """
                SELECT id FROM restaurants WHERE id = %s
            """
            result_check, error = fetch_one(query_check_restaurant, (restaurant_id,))
            if error or not result_check:
                return {"error": "Restaurant non trouvé"}

            # Vérifier si le statut existe (si fourni)
            if statut_id is not None:
                query_check_statut = """
                    SELECT id FROM statut_restaurant WHERE id = %s
                """
                result_statut, error = fetch_one(query_check_statut, (statut_id,))
                if error or not result_statut:
                    return {"error": "Statut restaurant non trouvé"}

            # Préparation de la position géographique
            geo_wkt = None
            if geo_position is not None:
                geo_wkt = f"POINT({geo_position[0]} {geo_position[1]})"

            # Mettre à jour le restaurant
            query_update = """
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
            result_restaurant, error = fetch_one(query_update, (
                nom, horaire_debut, horaire_fin, adresse, image, 
                geo_wkt, geo_wkt, restaurant_id
            ))
            if error:
                return {"error": f"Erreur lors de la mise à jour du restaurant : {str(error)}"}

            # Si statut fourni, mettre à jour l'historique
            result_historique = None
            if statut_id is not None:
                query_historique = """
                    INSERT INTO historique_statut_restaurant (restaurant_id, statut_id)
                    VALUES (%s, %s)
                    RETURNING id, restaurant_id, statut_id, mis_a_jour_le
                """
                result_historique, error = fetch_one(query_historique, (restaurant_id, statut_id))
                if error:
                    return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}

            # Préparation du résultat
            response = {
                "restaurant": dict(result_restaurant) if result_restaurant else None,
                "historique": dict(result_historique) if result_historique else None
            }

            return response

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def delete(restaurant_id,statut_id):
        """Met à jour un restaurant Retourne les données mises à jour ou None si non trouvé."""
        if not restaurant_id or statut_id <= 0:
            return {"error": "ID invalide"}

        query = """
            insert into historique_statut_restaurant (restaurant_id,statut_id)
            values(%s,%s) 
            RETURNING id, restaurant_id, statut_id
        """
        result, error = fetch_one(query, (restaurant_id,statut_id))
        if error:
            return {"error": str(error)}
        return result if result else None