import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Entite:
    """Classe représentant une entité dans le système."""

    @staticmethod
    def create(nom):
        """Crée une nouvelle entité et enregistre dans l'historique. Retourne les données insérées ou un message d'erreur."""
        if nom is not None and (not isinstance(nom, str) or len(nom) > 100):
            return {"error": "Nom invalide : doit être une chaîne de 100 caractères maximum"}

        # Vérifier si statut_id = 1 (Actif) existe
        statut_id = 1  # Statut "Actif"
        query_check_statut = """
            SELECT id FROM statut_entite WHERE id = %s
        """
        result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
        if error or not result_check_statut:
            return {"error": "Statut d'entité non trouvé"}

        try:
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

            return {"data": {"entite": result_entite, "historique": result_historique}}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def get_by_id(entite_id):
        """
        Récupère toutes les lignes d'une entité par son ID, incluant l'historique des statuts.
        
        Args:
            entite_id (int): L'ID de l'entité à récupérer.
        
        Returns:
            dict: Dictionnaire avec une clé 'data' contenant une liste de dictionnaires (chaque dictionnaire représente une ligne).
                En cas d'erreur ou si aucune entité n'est trouvée, retourne un dictionnaire avec une clé 'error'.
        """
        if not isinstance(entite_id, int) or entite_id <= 0:
            return {"error": "ID invalide"}

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
    def get_all() -> List[Dict[str, Any]]:
        """Récupère toutes les entités."""
        query = """
            SELECT id, nom
            FROM entites
            ORDER BY nom
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    def update(entite_id, statut_id, nom=None):
        """Met à jour une entité et son historique. Retourne les données mises à jour ou None si non trouvé."""
        if not isinstance(entite_id, int) or entite_id <= 0 or not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "ID invalide"}
        if nom is not None and (not isinstance(nom, str) or len(nom) > 100):
            return {"error": "Nom invalide : doit être une chaîne de 100 caractères maximum"}

        # Vérifier si entite_id existe
        query_check_entite = """
            SELECT id FROM entites WHERE id = %s
        """
        result_check_entite, error = fetch_one(query_check_entite, (entite_id,))
        if error or not result_check_entite:
            return {"error": "Entité non trouvée"}

        # Vérifier si statut_id existe
        query_check_statut = """
            SELECT id FROM statut_entite WHERE id = %s
        """
        result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
        if error or not result_check_statut:
            return {"error": "Statut d'entité non trouvé"}

        try:
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
            result_historique, error = fetch_one(query_historique, (result_entite['id'], statut_id))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}

            return result_historique if result_historique else None
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def delete(entite_id):
        """Marque une entité comme inactive dans l'historique. Retourne les données mises à jour ou None si non trouvé."""
        if not isinstance(entite_id, int) or entite_id <= 0:
            return {"error": "ID invalide"}

        # Vérifier si entite_id existe
        query_check_entite = """
            SELECT id FROM entites WHERE id = %s
        """
        result_check_entite, error = fetch_one(query_check_entite, (entite_id,))
        if error or not result_check_entite:
            return {"error": "Entité non trouvée"}

        # Vérifier si statut_id = 2 (Inactif) existe
        statut_id = 2  # Statut "Inactif"
        query_check_statut = """
            SELECT id FROM statut_entite WHERE id = %s
        """
        result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
        if error or not result_check_statut:
            return {"error": "Statut d'entité non trouvé"}

        try:
            # Insérer dans historique_statut_entite
            query_historique = """
                INSERT INTO historique_statut_entite (entite_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, entite_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (entite_id, statut_id))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}
            return result_historique if result_historique else None
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
