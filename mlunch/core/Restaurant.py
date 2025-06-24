import psycopg2.errors
from typing import Optional, Dict, List, Any, Tuple
from database.db import execute_query, fetch_query, fetch_one

class Restaurant:
    """Classe représentant un restaurant dans le système."""

    @staticmethod
    def create(nom: str, horaire_debut: Optional[str] = None, horaire_fin: Optional[str] = None, 
               adresse: Optional[str] = None, image: Optional[str] = None, 
               geo_position: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
        """Crée un nouveau restaurant."""
        if not nom:
            return {"error": "Le nom est requis"}

        position_wkt = f'POINT({geo_position[0]} {geo_position[1]})' if geo_position else None
        query = """
            INSERT INTO restaurants (nom, horaire_debut, horaire_fin, adresse, image, geo_position)
            VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
            RETURNING id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
        """
        result, error = fetch_one(query, (nom, horaire_debut, horaire_fin, adresse, image, position_wkt))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": f"Le nom {nom} est déjà utilisé"}
            return {"error": f"Erreur lors de la création : {str(error)}"}
        if not result:
            return {"error": "Échec de la création du restaurant"}
        return dict(result)

    @staticmethod
    def get_by_id(restaurant_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un restaurant par son ID."""
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
            FROM restaurants
            WHERE id = %s
        """
        result, error = fetch_one(query, (restaurant_id,))
        if error:
            return {"error": f"Erreur lors de la récupération : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Récupère tous les restaurants."""
        query = """
            SELECT id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
            FROM restaurants
            ORDER BY nom
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    def update(restaurant_id: int, nom: Optional[str] = None, horaire_debut: Optional[str] = None, 
               horaire_fin: Optional[str] = None, adresse: Optional[str] = None, 
               image: Optional[str] = None, geo_position: Optional[Tuple[float, float]] = None) -> Optional[Dict[str, Any]]:
        """Met à jour un restaurant."""
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "ID invalide"}

        position_wkt = f'POINT({geo_position[0]} {geo_position[1]})' if geo_position else None
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
        result, error = fetch_one(query, (nom, horaire_debut, horaire_fin, adresse, image, position_wkt, restaurant_id))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": f"Le nom {nom} est déjà utilisé"}
            return {"error": f"Erreur lors de la mise à jour : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def delete(restaurant_id: int) -> Dict[str, Any]:
        """Supprime un restaurant."""
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "ID invalide"}

        query = """
            DELETE FROM restaurants
            WHERE id = %s
            RETURNING id
        """
        result, error = fetch_one(query, (restaurant_id,))
        if error:
            return {"error": f"Erreur lors de la suppression : {str(error)}"}
        return {"success": bool(result), "id": restaurant_id}
