from ...database.db import execute_query, fetch_query, fetch_one

class Repas:
    """Classe représentant un repas dans le système."""
    
    @staticmethod
    def create(nom, description=None, image=None, type_id=None, prix=None):
        """Crée un nouveau repas."""
        query = """
            INSERT INTO repas (nom, description, image, type_id, prix)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, nom, description, image, type_id, prix
        """
        result = fetch_one(query, (nom, description, image, type_id, prix))
        return result

    @staticmethod
    def get_by_id(repas_id):
        """Récupère un repas par son ID."""
        query = """
            SELECT id, nom, description, image, type_id, prix
            FROM repas
            WHERE id = %s
        """
        return fetch_one(query, (repas_id,))

    @staticmethod
    def update(repas_id, nom=None, description=None, image=None, type_id=None, prix=None):
        """Met à jour les informations d'un repas."""
        query = """
            UPDATE repas
            SET nom = COALESCE(%s, nom),
                description = COALESCE(%s, description),
                image = COALESCE(%s, image),
                type_id = COALESCE(%s, type_id),
                prix = COALESCE(%s, prix)
            WHERE id = %s
            RETURNING id, nom, description, image, type_id, prix
        """
        result = fetch_one(query, (nom, description, image, type_id, prix, repas_id))
        return result

    @staticmethod
    def delete(repas_id):
        """Supprime un repas."""
        query = "DELETE FROM repas WHERE id = %s"
        return execute_query(query, (repas_id,))