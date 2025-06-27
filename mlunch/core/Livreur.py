import psycopg2.errors
from typing import Optional, Dict, List, Any, Tuple
from database.db import execute_query, fetch_query, fetch_one

class Livreur:
    def __init__(self, id=None, nom=None, contact=None, position=None, date_inscri=None):
        self.id = id
        self.nom = nom
        self.contact = contact
        self.position = position  # format texte WKT "POINT(x y)" ou None
        self.date_inscri = date_inscri

    @staticmethod
    def create(nom, initial_statut_id, contact=None, position=None):
        if not nom:
            return {"error": "Le nom est requis"}
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "ID statut invalide"}

        try:
            position_wkt = f'POINT({position[0]} {position[1]})' if position else None

            query_livreur = """
                INSERT INTO livreurs (nom, contact, position)
                VALUES (%s, %s, ST_GeomFromText(%s, 4326))
                RETURNING id, nom, contact, ST_AsText(position) as position, date_inscri
            """
            result_livreur, error = fetch_one(query_livreur, (nom, contact, position_wkt))
            if error:
                if isinstance(error, psycopg2.errors.UniqueViolation):
                    return {"error": f"Le nom {nom} est déjà utilisé"}
                return {"error": f"Erreur lors de la création du livreur : {str(error)}"}
            if not result_livreur:
                return {"error": "Échec de la création du livreur"}

            livreur_id = result_livreur['id']

            query_statut = "SELECT id FROM statut_livreur WHERE id = %s"
            result_statut, error = fetch_one(query_statut, (initial_statut_id,))
            if error or not result_statut:
                return {"error": "Statut non trouvé"}

            query_historique = """
                INSERT INTO historique_statut_livreur (livreur_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, livreur_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (livreur_id, initial_statut_id))
            if error:
                return {"error": f"Erreur lors de la création de l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de la création de l'historique"}

            return {
                "livreur": dict(result_livreur),
                "historique": dict(result_historique)
            }

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def get_by_id(livreur_id: int):
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT id, nom, contact, ST_AsText(position) as position, date_inscri
            FROM livreurs
            WHERE id = %s
        """
        result, error = fetch_one(query, (livreur_id,))
        if error:
            return {"error": f"Erreur lors de la récupération : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def get_all():
        query = """
            SELECT id, nom, contact, ST_AsText(position) as position, date_inscri
            FROM livreurs
            ORDER BY nom
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    def update(livreur_id, nom=None, contact=None, position=None):
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "ID invalide"}

        position_wkt = None
        if position:
            if not (isinstance(position, tuple) and len(position) == 2 and
                    all(isinstance(coord, (int, float)) for coord in position)):
                return {"error": "Position invalide : doit être un tuple de deux nombres"}
            position_wkt = f'POINT({position[0]} {position[1]})'

        if nom and len(nom) > 100:
            return {"error": "Le nom dépasse la limite de 100 caractères"}

        query = """
            UPDATE livreurs
            SET nom = COALESCE(%s, nom),
                contact = COALESCE(%s, contact),
                position = COALESCE(ST_GeomFromText(%s, 4326), position)
            WHERE id = %s
            RETURNING id, nom, contact, ST_AsText(position) AS position, date_inscri
        """
        try:
            result, error = fetch_one(query, (nom, contact, position_wkt, livreur_id))
            if error:
                return {"error": f"Erreur lors de la mise à jour : {str(error)}"}
            if not result:
                return {"error": "Livreur non trouvé"}
            return {"data": dict(result)}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def delete(livreur_id):
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "ID invalide"}

        statut_id = 3
        query = """
            INSERT INTO historique_statut_livreur (livreur_id, statut_id)
            VALUES (%s, %s)
            RETURNING id, livreur_id, statut_id, mis_a_jour_le
        """
        result, error = fetch_one(query, (livreur_id, statut_id))
        if error:
            return {"error": str(error)}
        return dict(result) if result else None
