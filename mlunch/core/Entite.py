import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Entite:
    """Classe représentant une entité dans le système."""

    @staticmethod
    def create(nom: str) -> Dict[str, Any]:
        """Crée une nouvelle entité."""
        if not nom:
            return {"error": "Le nom est requis"}

        query = """
            INSERT INTO entites (nom)
            VALUES (%s)
            RETURNING id, nom
        """
        result, error = fetch_one(query, (nom,))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": f"Le nom {nom} est déjà utilisé"}
            return {"error": f"Erreur lors de la création : {str(error)}"}
        if not result:
            return {"error": "Échec de la création de l'entité"}
        return dict(result)

    @staticmethod
    def get_by_id(entite_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une entité par son ID."""
        if not isinstance(entite_id, int) or entite_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT id, nom
            FROM entites
            WHERE id = %s
        """
        result, error = fetch_one(query, (entite_id,))
        if error:
            return {"error": f"Erreur lors de la récupération : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Récupère toutes les entités."""
        query = """
            SELECT id, nom
            FROM entites
            ORDER BY nom
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    def update(entite_id: int, nom: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Met à jour une entité."""
        if not isinstance(entite_id, int) or entite_id <= 0:
            return {"error": "ID invalide"}

        query = """
            UPDATE entites
            SET nom = COALESCE(%s, nom)
            WHERE id = %s
            RETURNING id, nom
        """
        result, error = fetch_one(query, (nom, entite_id))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": f"Le nom {nom} est déjà utilisé"}
            return {"error": f"Erreur lors de la mise à jour : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def delete(entite_id: int) -> Dict[str, Any]:
        """Supprime une entité."""
        if not isinstance(entite_id, int) or entite_id <= 0:
            return {"error": "ID invalide"}

        query = """
            DELETE FROM entites
            WHERE id = %s
            RETURNING id
        """
        result, error = fetch_one(query, (entite_id,))
        if error:
            return {"error": f"Erreur lors de la suppression : {str(error)}"}
        return {"success": bool(result), "id": entite_id}
