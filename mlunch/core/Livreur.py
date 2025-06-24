import psycopg2.errors
from typing import Optional, Dict, List, Any, Tuple
from database.db import execute_query, fetch_query, fetch_one

class Livreur:
    """Classe représentant un livreur dans le système."""

    @staticmethod
    def create(nom: str, contact: Optional[str] = None, position: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
        """Crée un nouveau livreur."""
        if not nom:
            return {"error": "Le nom est requis"}

        position_wkt = f'POINT({position[0]} {position[1]})' if position else None
        query = """
            INSERT INTO livreurs (nom, contact, position)
            VALUES (%s, %s, ST_GeomFromText(%s, 4326))
            RETURNING id, nom, contact, ST_AsText(position) as position
        """
        result, error = fetch_one(query, (nom, contact, position_wkt))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": f"Le nom {nom} est déjà utilisé"}
            return {"error": f"Erreur lors de la création : {str(error)}"}
        if not result:
            return {"error": "Échec de la création du livreur"}
        return dict(result)

    @staticmethod
    def get_by_id(livreur_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un livreur par son ID."""
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT id, nom, contact, ST_AsText(position) as position
            FROM livreurs
            WHERE id = %s
        """
        result, error = fetch_one(query, (livreur_id,))
        if error:
            return {"error": f"Erreur lors de la récupération : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Récupère tous les livreurs."""
        query = """
            SELECT id, nom, contact, ST_AsText(position) as position
            FROM livreurs
            ORDER BY nom
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    def update(livreur_id: int, nom: Optional[str] = None, contact: Optional[str] = None, 
               position: Optional[Tuple[float, float]] = None) -> Optional[Dict[str, Any]]:
        """Met à jour un livreur."""
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "ID invalide"}

        position_wkt = f'POINT({position[0]} {position[1]})' if position else None
        query = """
            UPDATE livreurs
            SET nom = COALESCE(%s, nom),
                contact = COALESCE(%s, contact),
                position = COALESCE(ST_GeomFromText(%s, 4326), position)
            WHERE id = %s
            RETURNING id, nom, contact, ST_AsText(position) as position
        """
        result, error = fetch_one(query, (nom, contact, position_wkt, livreur_id))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": f"Le nom {nom} est déjà utilisé"}
            return {"error": f"Erreur lors de la mise à jour : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def delete(livreur_id: int) -> Dict[str, Any]:
        """Supprime un livreur."""
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "ID invalide"}

        query = """
            DELETE FROM livreurs
            WHERE id = %s
            RETURNING id
        """
        result, error = fetch_one(query, (livreur_id,))
        if error:
            return {"error": f"Erreur lors de la suppression : {str(error)}"}
        return {"success": bool(result), "id": livreur_id}
