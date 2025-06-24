from ...database.db import execute_query, fetch_query, fetch_one

class Livraison:
    """Classe représentant une livraison dans le système."""
    
    @staticmethod
    def create(livreur_id, commande_id):
        """Crée une nouvelle livraison."""
        query = """
            INSERT INTO livraisons (livreur_id, commande_id)
            VALUES (%s, %s)
            RETURNING id, livreur_id, commande_id, attribue_le
        """
        result = fetch_one(query, (livreur_id, commande_id))
        return result

    @staticmethod
    def get_by_id(livraison_id):
        """Récupère une livraison par son ID."""
        query = """
            SELECT id, livreur_id, commande_id, attribue_le
            FROM livraisons
            WHERE id = %s
        """
        return fetch_one(query, (livraison_id,))

    @staticmethod
    def delete(livraison_id):
        """Supprime une livraison."""
        query = "DELETE FROM livraisons WHERE id = %s"
        return execute_query(query, (livraison_id,))