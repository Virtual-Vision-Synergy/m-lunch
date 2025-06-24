from ...database.db import execute_query, fetch_query, fetch_one

class Zone:
    """Classe représentant une zone de livraison dans le système."""
    
    @staticmethod
    def create(nom, description=None, polygon=None):
        """Crée une nouvelle zone de livraison."""
        query = """
            INSERT INTO zones (nom, description, zone)
            VALUES (%s, %s, ST_GeomFromText(%s, 4326))
            RETURNING id, nom, description, ST_AsText(zone) as zone
        """
        result = fetch_one(query, (nom, description, polygon))
        return result

    @staticmethod
    def get_by_id(zone_id):
        """Récupère une zone par son ID."""
        query = """
            SELECT id, nom, description, ST_AsText(zone) as zone
            FROM zones
            WHERE id = %s
        """
        return fetch_one(query, (zone_id,))

    @staticmethod
    def update(zone_id, nom=None, description=None, polygon=None):
        """Met à jour les informations d'une zone."""
        query = """
            UPDATE zones
            SET nom = COALESCE(%s, nom),
                description = COALESCE(%s, description),
                zone = COALESCE(ST_GeomFromText(%s, 4326), zone)
            WHERE id = %s
            RETURNING id, nom, description, ST_AsText(zone) as zone
        """
        result = fetch_one(query, (nom, description, polygon, zone_id))
        return result

    @staticmethod
    def delete(zone_id):
        """Supprime une zone."""
        query = "DELETE FROM zones WHERE id = %s"
        return execute_query(query, (zone_id,))