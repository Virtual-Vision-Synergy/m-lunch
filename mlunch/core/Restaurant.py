import psycopg2.errors
from typing import Optional, Dict, List, Any, Tuple
from database.db import execute_query, fetch_query, fetch_one

class Restaurant:
    """Classe représentant un restaurant dans le système."""

    @staticmethod
    def CreateRestaurant(nom, initial_statut_id, adresse=None, image=None, geo_position=None):
        """Crée un nouveau restaurant avec un statut initial. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(nom, str) or not nom or len(nom) > 150:
            return {"error": "Le nom doit être une chaîne non vide de 150 caractères maximum"}
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "L'ID du statut doit être un entier positif"}
        if adresse is not None and not isinstance(adresse, str):
            return {"error": "L'adresse doit être une chaîne"}
        if image is not None and not isinstance(image, str):
            return {"error": "L'image doit être une chaîne"}
        if geo_position is not None and not (isinstance(geo_position, tuple) and len(geo_position) == 2 and all(isinstance(coord, (int, float)) for coord in geo_position)):
            return {"error": "Position invalide : doit être un tuple de deux nombres (longitude, latitude)"}

        position_wkt = f'POINT({geo_position[0]} {geo_position[1]})' if geo_position else None
        try:
            # Vérifier si le statut existe
            query_statut = """
                SELECT id FROM statut_restaurant WHERE id = %s
            """
            result_statut, error = fetch_one(query_statut, (initial_statut_id,))
            if error or not result_statut:
                return {"error": "Statut non trouvé"}

            # Insérer dans restaurants
            query_restaurant = """
                INSERT INTO restaurants (nom, adresse, image, geo_position)
                VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326))
                RETURNING id, nom, adresse, image, ST_AsText(geo_position) AS geo_position
            """
            result_restaurant, error = fetch_one(query_restaurant, (nom, adresse, image, position_wkt))
            if error:
                if isinstance(error, psycopg2.errors.UniqueViolation):
                    return {"error": f"Le nom {nom} est déjà utilisé"}
                return {"error": f"Erreur lors de la création du restaurant : {str(error)}"}
            if not result_restaurant:
                return {"error": "Échec de la création du restaurant"}

            restaurant_id = result_restaurant['id']

            # Insérer dans historique_statut_restaurant
            query_historique = """
                INSERT INTO historique_statut_restaurant (restaurant_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, restaurant_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (restaurant_id, initial_statut_id))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de l'enregistrement dans l'historique"}

            return {"restaurant": dict(result_restaurant), "historique": dict(result_historique)}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
    @staticmethod
    def GetRestaurantFromId(restaurant_id):
        """Récupère un restaurant par son ID avec son historique de statuts. Retourne un dictionnaire ou une erreur."""
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "L'ID du restaurant doit être un entier positif"}

        query = """
            SELECT 
                r.id AS restaurant_id, r.nom, r.adresse, r.image, ST_AsText(r.geo_position) AS geo_position,
                h.id AS historique_id, h.statut_id, h.mis_a_jour_le,
                s.appellation AS statut_appellation
            FROM restaurants r
            LEFT JOIN historique_statut_restaurant h ON r.id = h.restaurant_id
            LEFT JOIN statut_restaurant s ON h.statut_id = s.id
            WHERE r.id = %s
            ORDER BY h.mis_a_jour_le DESC
        """
        try:
            rows, error = fetch_query(query, (restaurant_id,), as_dict=True)
            if error:
                return {"error": f"Erreur lors de la récupération : {str(error)}"}
            if not rows:
                return {"error": "Aucun restaurant trouvé"}
            return {"data": rows}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
    @staticmethod
    def GetAllRestaurants():
        """Récupère tous les restaurants. Retourne une liste de dictionnaires ou une erreur."""
        query = """
            SELECT id, nom, adresse, image, ST_AsText(geo_position) AS geo_position
            FROM restaurants
            ORDER BY nom
        """
        try:
            results, error = fetch_query(query)
            if error:
                return {"error": f"Erreur lors de la récupération : {str(error)}"}
            if not results:
                return {"error": "Aucun restaurant trouvé"}
            return [dict(row) for row in results]
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def UpdateRestaurant(restaurant_id, nom=None, adresse=None, image=None, geo_position=None, statut_id=None):
        """Met à jour les informations d'un restaurant et son historique de statut. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "L'ID du restaurant doit être un entier positif"}
        if nom is not None and (not isinstance(nom, str) or not nom or len(nom) > 150):
            return {"error": "Le nom doit être une chaîne non vide de 150 caractères maximum"}
        if adresse is not None and not isinstance(adresse, str):
            return {"error": "L'adresse doit être une chaîne"}
        if image is not None and not isinstance(image, str):
            return {"error": "L'image doit être une chaîne"}
        if geo_position is not None and not (isinstance(geo_position, tuple) and len(geo_position) == 2 and all(isinstance(coord, (int, float)) for coord in geo_position)):
            return {"error": "Position invalide : doit être un tuple de deux nombres (longitude, latitude)"}
        if statut_id is not None and (not isinstance(statut_id, int) or statut_id <= 0):
            return {"error": "L'ID du statut doit être un entier positif"}

        position_wkt = f'POINT({geo_position[0]} {geo_position[1]})' if geo_position else None
        try:
            # Vérifier si le restaurant existe
            query_check_restaurant = """
                SELECT id FROM restaurants WHERE id = %s
            """
            result_check_restaurant, error = fetch_one(query_check_restaurant, (restaurant_id,))
            if error or not result_check_restaurant:
                return {"error": "Restaurant non trouvé"}

            # Vérifier si le statut existe (si fourni)
            if statut_id is not None:
                query_check_statut = """
                    SELECT id FROM statut_restaurant WHERE id = %s
                """
                result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
                if error or not result_check_statut:
                    return {"error": "Statut non trouvé"}

            # Mettre à jour la table restaurants
            query_update_restaurant = """
                UPDATE restaurants
                SET nom = COALESCE(%s, nom),
                    adresse = COALESCE(%s, adresse),
                    image = COALESCE(%s, image),
                    geo_position = COALESCE(ST_GeomFromText(%s, 4326), geo_position)
                WHERE id = %s
                RETURNING id, nom, adresse, image, ST_AsText(geo_position) AS geo_position
            """
            result_restaurant, error = fetch_one(query_update_restaurant, (nom, adresse, image, position_wkt, restaurant_id))
            if error:
                if isinstance(error, psycopg2.errors.UniqueViolation):
                    return {"error": f"Le nom {nom} est déjà utilisé"}
                return {"error": f"Erreur lors de la mise à jour du restaurant : {str(error)}"}
            if not result_restaurant:
                return {"error": "Échec de la mise à jour du restaurant"}

            # Si statut_id est fourni, mettre à jour l'historique
            if statut_id is not None:
                query_historique = """
                    INSERT INTO historique_statut_restaurant (restaurant_id, statut_id)
                    VALUES (%s, %s)
                    RETURNING id, restaurant_id, statut_id, mis_a_jour_le
                """
                result_historique, error = fetch_one(query_historique, (restaurant_id, statut_id))
                if error:
                    return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}
                if not result_historique:
                    return {"error": "Échec de l'enregistrement dans l'historique"}
            else:
                result_historique = None

            return {"restaurant": dict(result_restaurant), "historique": dict(result_historique) if result_historique else None}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def DeleteRestaurant(restaurant_id):
        """Marque un restaurant comme fermé (statut_id=3) dans l'historique. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "L'ID du restaurant doit être un entier positif"}

        statut_id = 3  # Statut "Fermé"
        try:
            # Vérifier si le restaurant existe
            query_check_restaurant = """
                SELECT id FROM restaurants WHERE id = %s
            """
            result_check_restaurant, error = fetch_one(query_check_restaurant, (restaurant_id,))
            if error or not result_check_restaurant:
                return {"error": "Restaurant non trouvé"}

            # Vérifier si le statut "Fermé" existe
            query_check_statut = """
                SELECT id FROM statut_restaurant WHERE id = %s
            """
            result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
            if error or not result_check_statut:
                return {"error": "Statut 'Fermé' non trouvé"}

            # Insérer dans historique_statut_restaurant
            query_historique = """
                INSERT INTO historique_statut_restaurant (restaurant_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, restaurant_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (restaurant_id, statut_id))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de l'enregistrement dans l'historique"}

            return dict(result_historique)
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}