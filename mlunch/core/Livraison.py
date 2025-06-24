import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Livraison:
    """Classe représentant une livraison dans le système."""

    @staticmethod
    def create(livreur_id,commande_id,initial_statut_id):
        """Crée une nouvelle livraison."""
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "ID livreur invalide"}
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "ID commande invalide"}

        # Démarrer une transaction
        try:
            # Insérer la livraison
            query_livraisons = """
                INSERT INTO livraisons (livreur_id, commande_id)
                VALUES (%s, %s)
            """
            result_livraison, error = fetch_one(query_livraisons, (livreur_id, commande_id))
            if error:
                if isinstance(error, psycopg2.errors.ForeignKeyViolation):
                    return {"error": "Livreur ou commande non trouvé"}
                return {"error": f"Erreur lors de la création : {str(error)}"}
            if not result_livraison:
                return {"error": "Échec de la création de la livraison"}
            
            livraison_id = result_livraison['id']

            # Vérifier si le statut existe
            query_statut = """
                    SELECT id FROM statut_livraison WHERE id = %s
                """
            result_statut, error = fetch_one(query_statut, (initial_statut_id,))
            if error or not result_statut:
                return {"error": "Statut non trouvé"}

            # Insérer dans l'historique
            query_historique = """
                    INSERT INTO historique_statut_livraison (livraison_id, statut_id)
                    VALUES (%s, %s)
                    RETURNING id, livraison_id, statut_id, mis_a_jour_le
                """
            result_historique, error = fetch_one(query_historique, ( livraison_id,initial_statut_id))
            if error:
                return {"error": f"Erreur lors de la création de l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de la création de l'historique"}

            # Retourner les informations complètes
            return {
                    "commande": dict(result_livraison),
                    "historique": dict(result_historique)
            }
            
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
        
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
