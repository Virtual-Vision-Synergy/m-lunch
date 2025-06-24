from ...database.db import execute_query, fetch_query, fetch_one

class Commande:
    """Classe représentant une commande dans le système."""
    
    @staticmethod
    def create(client_id):
        """Crée une nouvelle commande."""
        query = """
            INSERT INTO commandes (client_id)
            VALUES (%s)
            RETURNING id, client_id, cree_le
        """
        result = fetch_one(query, (client_id,))
        return result

    @staticmethod
    def get_by_id(commande_id):
        """Récupère une commande par son ID."""
        query = """
            SELECT id, client_id, cree_le
            FROM commandes
            WHERE id = %s
        """
        return fetch_one(query, (commande_id,))

    @staticmethod
    def add_repas(commande_id, repas_id, quantite):
        """Ajoute un repas à une commande."""
        query = """
            INSERT INTO commande_repas (commande_id, repas_id, quantite)
            VALUES (%s, %s, %s)
            RETURNING id, commande_id, repas_id, quantite, ajoute_le
        """
        result = fetch_one(query, (commande_id, repas_id, quantite))
        return result

    @staticmethod
    def delete(commande_id):
        """Supprime une commande (et ses repas associés grâce à ON DELETE CASCADE)."""
        query = "DELETE FROM commandes WHERE id = %s"
        return execute_query(query, (commande_id,))