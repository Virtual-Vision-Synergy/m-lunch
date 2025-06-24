import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Livraison:
    """Classe représentant une livraison dans le système."""

    @staticmethod
    def create(livreur_id: int, commande_id: int) -> Dict[str, Any]:
        """Crée une nouvelle livraison."""
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "ID livreur invalide"}
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "ID commande invalide"}

        query = """
            INSERT INTO livraisons (livreur_id, commande_id)
            VALUES (%s, %s)
            RETURNING id, livreur_id, commande_id, attribue_le
        """
        result, error = fetch_one(query, (livreur_id, commande_id))
        if error:
            if isinstance(error, psycopg2.errors.ForeignKeyViolation):
                return {"error": "Livreur ou commande non trouvé"}
            return {"error": f"Erreur lors de la création : {str(error)}"}
        if not result:
            return {"error": "Échec de la création de la livraison"}
        return dict(result)

    @staticmethod
    def get_by_id(livraison_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une livraison par son ID."""
        if not isinstance(livraison_id, int) or livraison_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT id, livreur_id, commande_id, attribue_le
            FROM livraisons
            WHERE id = %s
        """
        result, error = fetch_one(query, (livraison_id,))
        if error:
            return {"error": f"Erreur lors de la récupération : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Récupère toutes les livraisons."""
        query = """
            SELECT id, livreur_id, commande_id, attribue_le
            FROM livraisons
            ORDER BY attribue_le DESC
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    def delete(livraison_id: int) -> Dict[str, Any]:
        """Supprime une livraison."""
        if not isinstance(livraison_id, int) or livraison_id <= 0:
            return {"error": "ID invalide"}

        query = """
            DELETE FROM livraisons
            WHERE id = %s
            RETURNING id
        """
        result, error = fetch_one(query, (livraison_id,))
        if error:
            return {"error": f"Erreur lors de la suppression : {str(error)}"}
        return {"success": bool(result), "id": livraison_id}
