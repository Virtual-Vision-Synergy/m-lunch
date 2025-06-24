import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Repas:
    """Classe représentant un repas dans le système."""

    @staticmethod
    def create(nom: str, description: Optional[str] = None, image: Optional[str] = None, 
               type_id: Optional[int] = None, prix: Optional[float] = None) -> Dict[str, Any]:
        """Crée un nouveau repas."""
        if not nom:
            return {"error": "Le nom est requis"}

        query = """
            INSERT INTO repas (nom, description, image, type_id, prix)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, nom, description, image, type_id, prix
        """
        result, error = fetch_one(query, (nom, description, image, type_id, prix))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": f"Le nom {nom} est déjà utilisé"}
            if isinstance(error, psycopg2.errors.ForeignKeyViolation):
                return {"error": "Type de repas non trouvé"}
            return {"error": f"Erreur lors de la création : {str(error)}"}
        if not result:
            return {"error": "Échec de la création du repas"}
        return dict(result)

    @staticmethod
    def get_by_id(repas_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un repas par son ID."""
        if not isinstance(repas_id, int) or repas_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT id, nom, description, image, type_id, prix
            FROM repas
            WHERE id = %s
        """
        result, error = fetch_one(query, (repas_id,))
        if error:
            return {"error": f"Erreur lors de la récupération : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Récupère tous les repas."""
        query = """
            SELECT id, nom, description, image, type_id, prix
            FROM repas
            ORDER BY nom
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    def update(repas_id: int, nom: Optional[str] = None, description: Optional[str] = None, 
               image: Optional[str] = None, type_id: Optional[int] = None, 
               prix: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Met à jour un repas."""
        if not isinstance(repas_id, int) or repas_id <= 0:
            return {"error": "ID invalide"}

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
        result, error = fetch_one(query, (nom, description, image, type_id, prix, repas_id))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": f"Le nom {nom} est déjà utilisé"}
            if isinstance(error, psycopg2.errors.ForeignKeyViolation):
                return {"error": "Type de repas non trouvé"}
            return {"error": f"Erreur lors de la mise à jour : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def delete(repas_id: int) -> Dict[str, Any]:
        """Supprime un repas."""
        if not isinstance(repas_id, int) or repas_id <= 0:
            return {"error": "ID invalide"}

        query = """
            DELETE FROM repas
            WHERE id = %s
            RETURNING id
        """
        result, error = fetch_one(query, (repas_id,))
        if error:
            return {"error": f"Erreur lors de la suppression : {str(error)}"}
        return {"success": bool(result), "id": repas_id}
