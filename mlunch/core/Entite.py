from ...database.db import execute_query, fetch_query, fetch_one

class Entite:
    """Classe représentant une entité dans le système."""
    
    @staticmethod
    def create(nom):
        """Crée une nouvelle entité."""
        query = """
            INSERT INTO entites (nom)
            VALUES (%s)
            RETURNING id, nom
        """
        result = fetch_one(query, (nom,))
        return result

    @staticmethod
    def get_by_id(entite_id):
        """Récupère une entité par son ID."""
        query = """
            SELECT id, nom
            FROM entites
            WHERE id = %s
        """
        return fetch_one(query, (entite_id,))

    @staticmethod
    def update(entite_id, nom=None):
        """Met à jour les informations d'une entité."""
        query = """
            UPDATE entites
            SET nom = COALESCE(%s, nom)
            WHERE id = %s
            RETURNING id, nom
        """
        result = fetch_one(query, (nom, entite_id))
        return result

    @staticmethod
    def delete(entite_id):
        """Supprime une entité."""
        query = "DELETE FROM entites WHERE id = %s"
        return execute_query(query, (entite_id,))