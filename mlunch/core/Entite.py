import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Entite:
    """Classe représentant une entité dans le système."""

    @staticmethod
    def CreateEntite(nom):
        """Crée une nouvelle entité avec un statut initial 'Actif' (statut_id=1). Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(nom, str) or not nom or len(nom) > 100:
            return {"error": "Le nom doit être une chaîne non vide de 100 caractères maximum"}

        statut_id = 1  # Statut "Actif"
        try:
            # Vérifier si le statut existe
            query_check_statut = """
                SELECT id FROM statut_entite WHERE id = %s
            """
            result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
            if error or not result_check_statut:
                return {"error": "Statut 'Actif' non trouvé"}

            # Insérer dans entites
            query_entite = """
                INSERT INTO entites (nom)
                VALUES (%s)
                RETURNING id, nom
            """
            result_entite, error = fetch_one(query_entite, (nom,))
            if error:
                return {"error": f"Erreur lors de la création de l'entité : {str(error)}"}
            if not result_entite:
                return {"error": "Échec de la création de l'entité"}

            # Insérer dans historique_statut_entite
            query_historique = """
                INSERT INTO historique_statut_entite (entite_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, entite_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (result_entite['id'], statut_id))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de l'enregistrement dans l'historique"}

            return {"entite": dict(result_entite), "historique": dict(result_historique)}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetEntiteFromId(entite_id):
        """Récupère une entité par son ID avec son historique de statuts. Retourne un dictionnaire ou une erreur."""
        if not isinstance(entite_id, int) or entite_id <= 0:
            return {"error": "L'ID de l'entité doit être un entier positif"}

        query = """
            SELECT 
                e.id AS entite_id, e.nom AS entite_nom,
                h.id AS historique_id, h.statut_id, h.mis_a_jour_le,
                s.appellation AS statut_appellation
            FROM entites e
            LEFT JOIN historique_statut_entite h ON e.id = h.entite_id
            LEFT JOIN statut_entite s ON h.statut_id = s.id
            WHERE e.id = %s
            ORDER BY h.mis_a_jour_le DESC
        """
        try:
            rows, error = fetch_query(query, (entite_id,), as_dict=True)
            if error:
                return {"error": f"Erreur lors de la récupération : {str(error)}"}
            if not rows:
                return {"error": "Aucune entité trouvée"}
            return {"data": rows}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetAllEntites():
        """Récupère toutes les entités. Retourne une liste de dictionnaires ou une erreur."""
        query = """
            SELECT id, nom
            FROM entites
            ORDER BY nom
        """
        try:
            results, error = fetch_query(query)
            if error:
                return {"error": f"Erreur lors de la récupération : {str(error)}"}
            if not results:
                return {"error": "Aucune entité trouvée"}
            return [dict(row) for row in results]
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def UpdateEntite(entite_id, statut_id, nom=None):
        """Met à jour une entité et son historique de statut. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(entite_id, int) or entite_id <= 0:
            return {"error": "L'ID de l'entité doit être un entier positif"}
        if not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "L'ID du statut doit être un entier positif"}
        if nom is not None and (not isinstance(nom, str) or len(nom) > 100 or not nom):
            return {"error": "Le nom doit être une chaîne non vide de 100 caractères maximum"}

        try:
            # Vérifier si l'entité existe
            query_check_entite = """
                SELECT id FROM entites WHERE id = %s
            """
            result_check_entite, error = fetch_one(query_check_entite, (entite_id,))
            if error or not result_check_entite:
                return {"error": "Entité non trouvée"}

            # Vérifier si le statut existe
            query_check_statut = """
                SELECT id FROM statut_entite WHERE id = %s
            """
            result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
            if error or not result_check_statut:
                return {"error": "Statut non trouvé"}

            # Mettre à jour la table entites
            query_update_entite = """
                UPDATE entites
                SET nom = COALESCE(%s, nom)
                WHERE id = %s
                RETURNING id, nom
            """
            result_entite, error = fetch_one(query_update_entite, (nom, entite_id))
            if error:
                return {"error": f"Erreur lors de la mise à jour de l'entité : {str(error)}"}
            if not result_entite:
                return {"error": "Échec de la mise à jour de l'entité"}

            # Insérer dans historique_statut_entite
            query_historique = """
                INSERT INTO historique_statut_entite (entite_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, entite_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (entite_id, statut_id))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de l'enregistrement dans l'historique"}

            return {"entite": dict(result_entite), "historique": dict(result_historique)}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
    @staticmethod
    def DeleteEntite(entite_id,statut_id):
        """Marque une entité comme inactive (statut_id=2) dans l'historique. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(entite_id, int) or entite_id <= 0:
            return {"error": "L'ID de l'entité doit être un entier positif"}
        if not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "L'ID du statut doit être un entier positif"}
            
        try:
            # Vérifier si l'entité existe
            query_check_entite = """
                SELECT id FROM entites WHERE id = %s
            """
            result_check_entite, error = fetch_one(query_check_entite, (entite_id,))
            if error or not result_check_entite:
                return {"error": "Entité non trouvée"}

            # Vérifier si le statut "Inactif" existe
            query_check_statut = """
                SELECT id FROM statut_entite WHERE id = %s
            """
            result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
            if error or not result_check_statut:
                return {"error": "Statut 'Inactif' non trouvé"}

            # Insérer dans historique_statut_entite
            query_historique = """
                INSERT INTO historique_statut_entite (entite_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, entite_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (entite_id, statut_id))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de l'enregistrement dans l'historique"}

            return dict(result_historique)
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}