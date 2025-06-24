from ...database.db import execute_query, fetch_query, fetch_one

class Restaurant:
    """Classe représentant un restaurant dans le système."""
    
    @staticmethod
    def create(nom, horaire_debut=None, horaire_fin=None, adresse=None, image=None, geo_position=None):
        """Crée un nouveau restaurant."""
        query = """
            INSERT INTO restaurants (nom, horaire_debut, horaire_fin, adresse, image, geo_position)
            VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
            RETURNING id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
        """
        position_wkt = f'POINT({geo_position[0]} {geo_position[1]})' if geo_position else None
        result = fetch_one(query, (nom, horaire_debut, horaire_fin, adresse, image, position_wkt))
        return result

    @staticmethod
    def get_by_id(restaurant_id):
        """Récupère un restaurant par son ID."""
        query = """
            SELECT id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
            FROM restaurants
            WHERE id = %s
        """
        return fetch_one(query, (restaurant_id,))

    @staticmethod
    def update(restaurant_id, nom=None, horaire_debut=None, horaire_fin=None, adresse=None, image=None, geo_position=None):
        """Met à jour les informations d'un restaurant."""
        query = """
            UPDATE restaurants
            SET nom = COALESCE(%s, nom),
                horaire_debut = COALESCE(%s, horaire_debut),
                horaire_fin = COALESCE(%s, horaire_fin),
                adresse = COALESCE(%s, adresse),
                image = COALESCE(%s, image),
                geo_position = COALESCE(ST_GeomFromText(%s, 4326), geo_position)
            WHERE id = %s
            RETURNING id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
        """
        position_wkt = f'POINT({geo_position[0]} {geo_position[1]})' if geo_position else None
        result = fetch_one(query, (nom, horaire_debut, horaire_fin, adresse, image, position_wkt, restaurant_id))
        return result

    @staticmethod
    def delete(restaurant_id):
        """Supprime un restaurant."""
        query = "DELETE FROM restaurants WHERE id = %s"
        return execute_query(query, (restaurant_id,))