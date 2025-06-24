from ...database.db import execute_query, fetch_query, fetch_one

class Livreur:
    """Classe représentant un livreur dans le système."""
    
    @staticmethod
    def create(nom, contact=None, position=None):
        """Crée un nouveau livreur."""
        query = """
            INSERT INTO livreurs (nom, contact, position)
            VALUES (%s, %s, ST_GeomFromText(%s, 4326))
            RETURNING id, nom, contact, position
        """
        position_wkt = f'POINT({position[0]} {position[1]})' if position else None
        result = fetch_one(query, (nom, contact, position_wkt))
        return result

    @staticmethod
    def get_by_id(livreur_id):
        """Récupère un livreur par son ID."""
        query = """
            SELECT id, nom, contact, ST_AsText(position) as position
            FROM livreurs
            WHERE id = %s
        """
        return fetch_one(query, (livreur_id,))

    @staticmethod
    def update(livreur_id, nom=None, contact=None, position=None):
        """Met à jour les informations d'un livreur."""
        query = """
            UPDATE livreurs
            SET nom = COALESCE(%s, nom),
                contact = COALESCE(%s, contact),
                position = COALESCE(ST_GeomFromText(%s, 4326), position)
            WHERE id = %s
            RETURNING id, nom, contact, ST_AsText(position) as position
        """
        position_wkt = f'POINT({position[0]} {position[1]})' if position else None
        result = fetch_one(query, (nom, contact, position_wkt, livreur_id))
        return result

    @staticmethod
    def delete(livreur_id):
        """Supprime un livreur."""
        query = "DELETE FROM livreurs WHERE id = %s"
        return execute_query(query, (livreur_id,))