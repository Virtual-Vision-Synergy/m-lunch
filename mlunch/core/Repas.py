import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Repas:
    def __init__(self, id=None, nom=None, description=None, image=None, type_id=None, prix=None):
        self.id = id
        self.nom = nom
        self.description = description
        self.image = image
        self.type_id = type_id
        self.prix = prix

    @staticmethod
    def create(nom, description, image, type_id, prix):
        if not isinstance(prix, (int, float)) or prix <= 0:
            return {"error": "Prix invalide : doit être un nombre positif"}
        if nom and (not isinstance(nom, str) or len(nom) > 100):
            return {"error": "Nom invalide : doit être une chaîne de 100 caractères maximum"}
        if description and not isinstance(description, str):
            return {"error": "Description invalide : doit être une chaîne"}
        if image and not isinstance(image, str):
            return {"error": "Image invalide : doit être une chaîne"}
        if type_id and (not isinstance(type_id, int) or type_id <= 0):
            return {"error": "ID type invalide : doit être un entier positif"}

        # Vérifier existence type_repas
        if type_id:
            query_check_type = "SELECT id FROM types_repas WHERE id = %s"
            result_check_type, error = fetch_one(query_check_type, (type_id,))
            if error or not result_check_type:
                return {"error": "Type de repas non trouvé"}

        # Vérifier statut "Disponible" (id=1)
        statut_id = 1
        query_check_statut = "SELECT id FROM statut_repas WHERE id = %s"
        result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
        if error or not result_check_statut:
            return {"error": "Statut de repas non trouvé"}

        try:
            query_repas = """
                INSERT INTO repas (nom, description, image, type_id, prix)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, nom, description, image, type_id, prix
            """
            result_repas, error = fetch_one(query_repas, (nom, description, image, type_id, prix))
            if error:
                return {"error": f"Erreur lors de la création du repas : {str(error)}"}
            if not result_repas:
                return {"error": "Échec de la création du repas"}

            query_historique = """
                INSERT INTO historique_statut_repas (repas_id, statut_id, nom, description, image, type_id, prix)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, repas_id, statut_id, nom, description, image, type_id, prix, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (
                result_repas['id'], statut_id, nom, description, image, type_id, prix
            ))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}

            return {"data": {"repas": result_repas, "historique": result_historique}}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def get_by_id(repas_id):
        if not isinstance(repas_id, int) or repas_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT 
                r.id AS repas_id, r.nom AS repas_nom, r.description AS repas_description, 
                r.image AS repas_image, r.type_id AS repas_type_id, r.prix AS repas_prix,
                h.id AS historique_id, h.statut_id, h.nom, h.description, h.image, h.type_id, h.prix, 
                h.mis_a_jour_le, s.appellation AS statut_appellation
            FROM repas r
            LEFT JOIN historique_statut_repas h ON r.id = h.repas_id
            LEFT JOIN statut_repas s ON h.statut_id = s.id
            WHERE r.id = %s
            ORDER BY h.mis_a_jour_le DESC
        """
        try:
            rows, error = fetch_query(query, (repas_id,), as_dict=True)
            if error:
                return {"error": f"Erreur lors de la récupération : {str(error)}"}
            if not rows:
                return {"error": "Aucun repas trouvé"}
            return {"data": rows}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def get_all():
        query = "SELECT id, nom, description, image, type_id, prix FROM repas ORDER BY nom"
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    def update(repas_id, statut_id, nom=None, description=None, image=None, type_id=None, prix=None):
        if not isinstance(repas_id, int) or repas_id <= 0 or not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "ID invalide"}
        if prix is not None and (not isinstance(prix, (int, float)) or prix <= 0):
            return {"error": "Prix invalide : doit être un nombre positif"}
        if nom is not None and (not isinstance(nom, str) or len(nom) > 100):
            return {"error": "Nom invalide : doit être une chaîne de 100 caractères maximum"}
        if description is not None and not isinstance(description, str):
            return {"error": "Description invalide : doit être une chaîne"}
        if image is not None and not isinstance(image, str):
            return {"error": "Image invalide : doit être une chaîne"}
        if type_id is not None and (not isinstance(type_id, int) or type_id <= 0):
            return {"error": "ID type invalide : doit être un entier positif"}

        query_check_repas = "SELECT id FROM repas WHERE id = %s"
        result_check_repas, error = fetch_one(query_check_repas, (repas_id,))
        if error or not result_check_repas:
            return {"error": "Repas non trouvé"}

        query_check_statut = "SELECT id FROM statut_repas WHERE id = %s"
        result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
        if error or not result_check_statut:
            return {"error": "Statut de repas non trouvé"}

        if type_id is not None:
            query_check_type = "SELECT id FROM types_repas WHERE id = %s"
            result_check_type, error = fetch_one(query_check_type, (type_id,))
            if error or not result_check_type:
                return {"error": "Type de repas non trouvé"}

        try:
            query_update_repas = """
                UPDATE repas
                SET nom = COALESCE(%s, nom),
                    description = COALESCE(%s, description),
                    image = COALESCE(%s, image),
                    type_id = COALESCE(%s, type_id),
                    prix = COALESCE(%s, prix)
                WHERE id = %s
                RETURNING id, nom, description, image, type_id, prix
            """
            result_repas, error = fetch_one(query_update_repas, (nom, description, image, type_id, prix, repas_id))
            if error:
                return {"error": f"Erreur lors de la mise à jour du repas : {str(error)}"}
            if not result_repas:
                return {"error": "Échec de la mise à jour du repas"}

            query_historique = """
                INSERT INTO historique_statut_repas (repas_id, statut_id, nom, description, image, type_id, prix)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, repas_id, statut_id, nom, description, image, type_id, prix, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (
                result_repas['id'], statut_id, result_repas['nom'], result_repas['description'],
                result_repas['image'], result_repas['type_id'], result_repas['prix']
            ))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}

            return result_historique if result_historique else None
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def delete(repas_id, statut_id):
        if not repas_id or statut_id <= 0:
            return {"error": "ID invalide"}

        query = """
            INSERT INTO historique_statut_repas (repas_id, statut_id)
            VALUES (%s, %s) 
            RETURNING id, repas_id, statut_id
        """
        result, error = fetch_one(query, (repas_id, statut_id))
        if error:
            return {"error": str(error)}
        return result if result else None
