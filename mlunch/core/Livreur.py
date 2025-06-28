import psycopg2.errors
from typing import Optional, Dict, List, Any, Tuple
from database.db import execute_query, fetch_query, fetch_one

class Livreur:
    """Classe représentant un livreur dans le système."""

    @staticmethod
    def CreateLivreur(nom, initial_statut_id, contact=None, position=None):
        """Crée un nouveau livreur avec un statut initial. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(nom, str) or not nom or len(nom) > 100:
            return {"error": "Le nom doit être une chaîne non vide de 100 caractères maximum"}
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "L'ID du statut doit être un entier positif"}
        if contact is not None and not isinstance(contact, str):
            return {"error": "Le contact doit être une chaîne"}
        if position is not None and not (isinstance(position, tuple) and len(position) == 2 and all(isinstance(coord, (int, float)) for coord in position)):
            return {"error": "Position invalide : doit être un tuple de deux nombres (longitude, latitude)"}

        position_wkt = f'POINT({position[0]} {position[1]})' if position else None
        try:
            # Vérifier si le statut existe
            query_statut = """
                SELECT id FROM statut_livreur WHERE id = %s
            """
            result_statut, error = fetch_one(query_statut, (initial_statut_id,))
            if error or not result_statut:
                return {"error": "Statut non trouvé"}

            # Insérer le livreur
            query_livreur = """
                INSERT INTO livreurs (nom, contact, position)
                VALUES (%s, %s, ST_GeomFromText(%s, 4326))
                RETURNING id, nom, contact, ST_AsText(position) AS position, date_inscri
            """
            result_livreur, error = fetch_one(query_livreur, (nom, contact, position_wkt))
            if error:
                if isinstance(error, psycopg2.errors.UniqueViolation):
                    return {"error": f"Le nom {nom} est déjà utilisé"}
                return {"error": f"Erreur lors de la création du livreur : {str(error)}"}
            if not result_livreur:
                return {"error": "Échec de la création du livreur"}

            livreur_id = result_livreur['id']

            # Insérer dans l'historique
            query_historique = """
                INSERT INTO historique_statut_livreur (livreur_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, livreur_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (livreur_id, initial_statut_id))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de l'enregistrement dans l'historique"}

            return {"livreur": dict(result_livreur), "historique": dict(result_historique)}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
    @staticmethod
    def GetLivreurFromId(livreur_id):
        """Récupère un livreur par son ID avec son historique de statuts. Retourne un dictionnaire ou une erreur."""
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "L'ID du livreur doit être un entier positif"}

        query = """
            SELECT 
                l.id AS livreur_id, l.nom, l.contact, ST_AsText(l.position) AS position, l.date_inscri,
                h.id AS historique_id, h.statut_id, h.mis_a_jour_le,
                s.appellation AS statut_appellation
            FROM livreurs l
            LEFT JOIN historique_statut_livreur h ON l.id = h.livreur_id
            LEFT JOIN statut_livreur s ON h.statut_id = s.id
            WHERE l.id = %s
            ORDER BY h.mis_a_jour_le DESC
        """
        try:
            rows, error = fetch_query(query, (livreur_id,), as_dict=True)
            if error:
                return {"error": f"Erreur lors de la récupération : {str(error)}"}
            if not rows:
                return {"error": "Aucun livreur trouvé"}
            return {"data": rows}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetAllLivreurs():
        """Récupère tous les livreurs. Retourne une liste de dictionnaires ou une erreur."""
        query = """
            SELECT id, nom, contact, ST_AsText(position) AS position, date_inscri
            FROM livreurs
            ORDER BY nom
        """
        try:
            results, error = fetch_query(query)
            if error:
                return {"error": f"Erreur lors de la récupération : {str(error)}"}
            if not results:
                return {"error": "Aucun livreur trouvé"}
            return [dict(row) for row in results]
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def UpdateLivreur(livreur_id, nom=None, contact=None, position=None):
        """Met à jour les informations d'un livreur. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "L'ID du livreur doit être un entier positif"}
        if nom is not None and (not isinstance(nom, str) or not nom or len(nom) > 100):
            return {"error": "Le nom doit être une chaîne non vide de 100 caractères maximum"}
        if contact is not None and not isinstance(contact, str):
            return {"error": "Le contact doit être une chaîne"}
        if position is not None and not (isinstance(position, tuple) and len(position) == 2 and all(isinstance(coord, (int, float)) for coord in position)):
            return {"error": "Position invalide : doit être un tuple de deux nombres (longitude, latitude)"}

        position_wkt = f'POINT({position[0]} {position[1]})' if position else None
        try:
            query = """
                UPDATE livreurs
                SET nom = COALESCE(%s, nom),
                    contact = COALESCE(%s, contact),
                    position = COALESCE(ST_GeomFromText(%s, 4326), position)
                WHERE id = %s
                RETURNING id, nom, contact, ST_AsText(position) AS position, date_inscri
            """
            result, error = fetch_one(query, (nom, contact, position_wkt, livreur_id))
            if error:
                if isinstance(error, psycopg2.errors.UniqueViolation):
                    return {"error": f"Le nom {nom} est déjà utilisé"}
                return {"error": f"Erreur lors de la mise à jour : {str(error)}"}
            if not result:
                return {"error": "Livreur non trouvé"}
            return dict(result)
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def DeleteLivreur(livreur_id,statut_id):
        """Marque un livreur comme renvoyé (statut_id=3) dans l'historique. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "L'ID du livreur doit être un entier positif"}
        if not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "L'ID du statut doit être un entier positif"}

       
        try:
            # Vérifier si le livreur existe
            query_check_livreur = """
                SELECT id FROM livreurs WHERE id = %s
            """
            result_check_livreur, error = fetch_one(query_check_livreur, (livreur_id,))
            if error or not result_check_livreur:
                return {"error": "Livreur non trouvé"}

            # Vérifier si le statut "Renvoyé" existe
            query_check_statut = """
                SELECT id FROM statut_livreur WHERE id = %s
            """
            result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
            if error or not result_check_statut:
                return {"error": "Statut 'Renvoyé' non trouvé"}

            # Insérer dans historique_statut_livreur
            query_historique = """
                INSERT INTO historique_statut_livreur (livreur_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, livreur_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (livreur_id, statut_id))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de l'enregistrement dans l'historique"}

            return dict(result_historique)
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}