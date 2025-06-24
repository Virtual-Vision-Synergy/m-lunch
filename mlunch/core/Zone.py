import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Zone:
    """Classe représentant une zone de livraison dans le système."""

    @staticmethod
    def create(nom: str, description: Optional[str] = None, polygon: Optional[str] = None) -> Dict[str, Any]:
        """Crée une nouvelle zone de livraison."""
        if not nom:
            return {"error": "Le nom est requis"}

        query = """
            INSERT INTO zones (nom, description, zone)
            VALUES (%s, %s, ST_GeomFromText(%s, 4326))
            RETURNING id, nom, description, ST_AsText(zone) as zone
        """
        result, error = fetch_one(query, (nom, description, polygon))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": f"Le nom {nom} est déjà utilisé"}
            return {"error": f"Erreur lors de la création : {str(error)}"}
        if not result:
            return {"error": "Échec de la création de la zone"}
        return dict(result)

    @staticmethod
    def get_by_id(zone_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une zone par son ID."""
        if not isinstance(zone_id, int) or zone_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT id, nom, description, ST_AsText(zone) as zone
            FROM zones
            WHERE id = %s
        """
        result, error = fetch_one(query, (zone_id,))
        if error:
            return {"error": f"Erreur lors de la récupération : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Récupère toutes les zones."""
        query = """
            SELECT id, nom, description, ST_AsText(zone) as zone
            FROM zones
            ORDER BY nom
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    def update(zone_id: int, nom: Optional[str] = None, description: Optional[str] = None, 
               polygon: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Met à jour une zone."""
        if not isinstance(zone_id, int) or zone_id <= 0:
            return {"error": "ID invalide"}

        query = """
            UPDATE zones
            SET nom = COALESCE(%s, nom),
                description = COALESCE(%s, description),
                zone = COALESCE(ST_GeomFromText(%s, 4326), zone)
            WHERE id = %s
            RETURNING id, nom, description, ST_AsText(zone) as zone
        """
        result, error = fetch_one(query, (nom, description, polygon, zone_id))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": f"Le nom {nom} est déjà utilisé"}
            return {"error": f"Erreur lors de la mise à jour : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def delete(zone_id: int) -> Dict[str, Any]:
        """Supprime une zone."""
        if not isinstance(zone_id, int) or zone_id <= 0:
            return {"error": "ID invalide"}

        query = """
            DELETE FROM zones
            WHERE id = %s
            RETURNING id
        """
        result, error = fetch_one(query, (zone_id,))
        if error:
            return {"error": f"Erreur lors de la suppression : {str(error)}"}
        return {"success": bool(result), "id": zone_id}
