import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Commande:
    """Classe représentant une commande dans le système."""

    @staticmethod
    def create(client_id: int) -> Dict[str, Any]:
        """Crée une nouvelle commande."""
        if not isinstance(client_id, int) or client_id <= 0:
            return {"error": "ID client invalide"}

        query = """
            INSERT INTO commandes (client_id)
            VALUES (%s)
            RETURNING id, client_id, cree_le
        """
        result, error = fetch_one(query, (client_id,))
        if error:
            if isinstance(error, psycopg2.errors.ForeignKeyViolation):
                return {"error": "Client non trouvé"}
            return {"error": f"Erreur lors de la création : {str(error)}"}
        if not result:
            return {"error": "Échec de la création de la commande"}
        return dict(result)

    @staticmethod
    def get_by_id(commande_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une commande par son ID."""
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT id, client_id, cree_le
            FROM commandes
            WHERE id = %s
        """
        result, error = fetch_one(query, (commande_id,))
        if error:
            return {"error": f"Erreur lors de la récupération : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Récupère toutes les commandes."""
        query = """
            SELECT id, client_id, cree_le
            FROM commandes
            ORDER BY cree_le DESC
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    def add_repas(commande_id: int, repas_id: int, quantite: int) -> Dict[str, Any]:
        """Ajoute un repas à une commande."""
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "ID commande invalide"}
        if not isinstance(repas_id, int) or repas_id <= 0:
            return {"error": "ID repas invalide"}
        if not isinstance(quantite, int) or quantite <= 0:
            return {"error": "Quantité invalide"}

        query = """
            INSERT INTO commande_repas (commande_id, repas_id, quantite)
            VALUES (%s, %s, %s)
            RETURNING id, commande_id, repas_id, quantite, ajoute_le
        """
        result, error = fetch_one(query, (commande_id, repas_id, quantite))
        if error:
            if isinstance(error, psycopg2.errors.ForeignKeyViolation):
                return {"error": "Commande ou repas non trouvé"}
            return {"error": f"Erreur lors de l'ajout du repas : {str(error)}"}
        if not result:
            return {"error": "Échec de l'ajout du repas"}
        return dict(result)

    @staticmethod
    def delete(commande_id: int) -> Dict[str, Any]:
        """Supprime une commande."""
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "ID invalide"}

        query = """
            DELETE FROM commandes
            WHERE id = %s
            RETURNING id
        """
        result, error = fetch_one(query, (commande_id,))
        if error:
            return {"error": f"Erreur lors de la suppression : {str(error)}"}
        return {"success": bool(result), "id": commande_id}
