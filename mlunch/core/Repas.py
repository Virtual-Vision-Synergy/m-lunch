import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Repas:
    """Classe représentant un repas dans le système."""

    @staticmethod
    # def create(nom, description, image, type_id, prix):
    #     """Crée un nouveau repas. Retourne les données insérées ou un message d'erreur."""
    #     # Validation des paramètres
    #     if not isinstance(prix, (int, float)) or prix <= 0:
    #         return {"error": "Prix invalide : doit être un nombre positif"}
    #     if nom and (not isinstance(nom, str) or len(nom) > 100):
    #         return {"error": "Nom invalide : doit être une chaîne de 100 caractères maximum"}
    #     if description and not isinstance(description, str):
    #         return {"error": "Description invalide : doit être une chaîne"}
    #     if image and not isinstance(image, str):
    #         return {"error": "Image invalide : doit être une chaîne"}
    #     if type_id and (not isinstance(type_id, int) or type_id <= 0):
    #         return {"error": "ID type invalide : doit être un entier positif"}

    #     # Vérifier si type_id existe (si fourni)
    #     if type_id:
    #         query_check = """
    #             SELECT id FROM types_repas WHERE id = %s
    #         """
    #         result_check, error = fetch_one(query_check, (type_id,))
    #         if error or not result_check:
    #             return {"error": "Type de repas non trouvé"}

    #     # Insérer le repas
    #     try:
    #         query = """
    #             INSERT INTO repas (nom, description, image, type_id, prix)
    #             VALUES (%s, %s, %s, %s, %s)
    #             RETURNING id, nom, description, image, type_id, prix
    #         """
    #         result, error = fetch_one(query, (nom, description, image, type_id, prix))
    #         if error:
    #             if isinstance(error, psycopg2.errors.ForeignKeyViolation):
    #                 return {"error": "Type de repas non trouvé"}
    #             return {"error": f"Erreur lors de la création du repas : {str(error)}"}
    #         if not result:
    #             return {"error": "Échec de la création du repas"}
    #         return result
    #     except Exception as e:
    #         return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def CreateRepas(nom, type_id, prix, description=None, image=None, est_dispo=True):
        """Crée un nouveau repas avec une disponibilité initiale. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(nom, str) or not nom or len(nom) > 100:
            return {"error": "Le nom doit être une chaîne non vide de 100 caractères maximum"}
        if not isinstance(type_id, int) or type_id <= 0:
            return {"error": "L'ID du type de repas doit être un entier positif"}
        if not isinstance(prix, int) or prix <= 0:
            return {"error": "Le prix doit être un entier positif"}
        if description is not None and not isinstance(description, str):
            return {"error": "La description doit être une chaîne"}
        if image is not None and not isinstance(image, str):
            return {"error": "L'image doit être une chaîne"}
        if not isinstance(est_dispo, bool):
            return {"error": "La disponibilité doit être un booléen"}

        try:
            # Vérifier si le type de repas existe
            query_check_type = """
                SELECT id FROM types_repas WHERE id = %s
            """
            result_check_type, error = fetch_one(query_check_type, (type_id,))
            if error or not result_check_type:
                return {"error": "Type de repas non trouvé"}

            # Insérer dans repas
            query_repas = """
                INSERT INTO repas (nom, description, image, type_id, prix)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, nom, description, image, type_id, prix
            """
            result_repas, error = fetch_one(query_repas, (nom, description, image, type_id, prix))
            if error:
                if isinstance(error, psycopg2.errors.ForeignKeyViolation):
                    return {"error": "Type de repas non trouvé"}
                return {"error": f"Erreur lors de la création du repas : {str(error)}"}
            if not result_repas:
                return {"error": "Échec de la création du repas"}

            # Insérer dans disponibilite_repas
            query_disponibilite = """
                INSERT INTO disponibilite_repas (repas_id, est_dispo)
                VALUES (%s, %s)
                RETURNING id, repas_id, est_dispo, mis_a_jour_le
            """
            result_disponibilite, error = fetch_one(query_disponibilite, (result_repas['id'], est_dispo))
            if error:
                return {"error": f"Erreur lors de l'enregistrement de la disponibilité : {str(error)}"}
            if not result_disponibilite:
                return {"error": "Échec de l'enregistrement de la disponibilité"}

            return {"repas": dict(result_repas), "disponibilite": dict(result_disponibilite)}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
    
    @staticmethod
    def GetRepasFromId(repas_id):
        """Récupère un repas par son ID avec son historique de disponibilité. Retourne un dictionnaire ou une erreur."""
        if not isinstance(repas_id, int) or repas_id <= 0:
            return {"error": "L'ID du repas doit être un entier positif"}

        query = """
            SELECT 
                r.id AS repas_id, r.nom, r.description, r.image, r.type_id, r.prix,
                t.nom AS type_nom,
                d.id AS disponibilite_id, d.est_dispo, d.mis_a_jour_le
            FROM repas r
            LEFT JOIN types_repas t ON r.type_id = t.id
            LEFT JOIN disponibilite_repas d ON r.id = d.repas_id
            WHERE r.id = %s
            ORDER BY d.mis_a_jour_le DESC
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
    def GetAllRepas():
        """Récupère tous les repas avec leur disponibilité actuelle. Retourne une liste de dictionnaires ou une erreur."""
        query = """
            SELECT 
                r.id, r.nom, r.description, r.image, r.type_id, r.prix,
                t.nom AS type_nom,
                d.est_dispo
            FROM repas r
            LEFT JOIN types_repas t ON r.type_id = t.id
            LEFT JOIN (
                SELECT repas_id, est_dispo
                FROM disponibilite_repas
                WHERE (repas_id, mis_a_jour_le) IN (
                    SELECT repas_id, MAX(mis_a_jour_le)
                    FROM disponibilite_repas
                    GROUP BY repas_id
                )
            ) d ON r.id = d.repas_id
            ORDER BY r.nom
        """
        try:
            results, error = fetch_query(query)
            if error:
                return {"error": f"Erreur lors de la récupération : {str(error)}"}
            if not results:
                return {"error": "Aucun repas trouvé"}
            return [dict(row) for row in results]
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def UpdateRepas(repas_id, type_id=None, prix=None, nom=None, description=None, image=None, est_dispo=None):
        """Met à jour un repas et sa disponibilité. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(repas_id, int) or repas_id <= 0:
            return {"error": "L'ID du repas doit être un entier positif"}
        if type_id is not None and (not isinstance(type_id, int) or type_id <= 0):
            return {"error": "L'ID du type de repas doit être un entier positif"}
        if prix is not None and (not isinstance(prix, int) or prix <= 0):
            return {"error": "Le prix doit être un entier positif"}
        if nom is not None and (not isinstance(nom, str) or not nom or len(nom) > 100):
            return {"error": "Le nom doit être une chaîne non vide de 100 caractères maximum"}
        if description is not None and not isinstance(description, str):
            return {"error": "La description doit être une chaîne"}
        if image is not None and not isinstance(image, str):
            return {"error": "L'image doit être une chaîne"}
        if est_dispo is not None and not isinstance(est_dispo, bool):
            return {"error": "La disponibilité doit être un booléen"}

        try:
            # Vérifier si le repas existe
            query_check_repas = """
                SELECT id FROM repas WHERE id = %s
            """
            result_check_repas, error = fetch_one(query_check_repas, (repas_id,))
            if error or not result_check_repas:
                return {"error": "Repas non trouvé"}

            # Vérifier si le type de repas existe (si fourni)
            if type_id is not None:
                query_check_type = """
                    SELECT id FROM types_repas WHERE id = %s
                """
                result_check_type, error = fetch_one(query_check_type, (type_id,))
                if error or not result_check_type:
                    return {"error": "Type de repas non trouvé"}

            # Mettre à jour la table repas
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
                if isinstance(error, psycopg2.errors.ForeignKeyViolation):
                    return {"error": "Type de repas non trouvé"}
                return {"error": f"Erreur lors de la mise à jour du repas : {str(error)}"}
            if not result_repas:
                return {"error": "Échec de la mise à jour du repas"}

            # Si est_dispo est fourni, mettre à jour la disponibilité
            if est_dispo is not None:
                query_disponibilite = """
                    INSERT INTO disponibilite_repas (repas_id, est_dispo)
                    VALUES (%s, %s)
                    RETURNING id, repas_id, est_dispo, mis_a_jour_le
                """
                result_disponibilite, error = fetch_one(query_disponibilite, (repas_id, est_dispo))
                if error:
                    return {"error": f"Erreur lors de l'enregistrement de la disponibilité : {str(error)}"}
                if not result_disponibilite:
                    return {"error": "Échec de l'enregistrement de la disponibilité"}
            else:
                result_disponibilite = None

            return {"repas": dict(result_repas), "disponibilite": dict(result_disponibilite) if result_disponibilite else None}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def DeleteRepas(repas_id):
        """Marque un repas comme non disponible (est_dispo=False) dans l'historique de disponibilité. Retourne un dictionnaire ou une erreur."""
        if not isinstance(repas_id, int) or repas_id <= 0:
            return {"error": "L'ID du repas doit être un entier positif"}

        try:
            # Vérifier si le repas existe
            query_check_repas = """
                SELECT id FROM repas WHERE id = %s
            """
            result_check_repas, error = fetch_one(query_check_repas, (repas_id,))
            if error or not result_check_repas:
                return {"error": "Repas non trouvé"}

            # Insérer dans disponibilite_repas avec est_dispo=False
            query_disponibilite = """
                INSERT INTO disponibilite_repas (repas_id, est_dispo)
                VALUES (%s, %s)
                RETURNING id, repas_id, est_dispo, mis_a_jour_le
            """
            result_disponibilite, error = fetch_one(query_disponibilite, (repas_id, False))
            if error:
                return {"error": f"Erreur lors de l'enregistrement de la disponibilité : {str(error)}"}
            if not result_disponibilite:
                return {"error": "Échec de l'enregistrement de la disponibilité"}

            return dict(result_disponibilite)
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}