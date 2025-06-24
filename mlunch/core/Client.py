import psycopg2.errors
from database.db import execute_query, fetch_query, fetch_one

class Client:
    """Classe représentant un client dans le système."""

    @staticmethod
    def create(email, mot_de_passe, contact=None, prenom=None, nom=None):
        """Crée un client. Retourne les données du client ou une erreur."""
        if not email or not mot_de_passe:
            return {"error": "Email et mot de passe requis"}

        query = """
            INSERT INTO clients (email, mot_de_passe, contact, prenom, nom)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, email, contact, prenom, nom
        """
        result, error = fetch_one(query, (email, mot_de_passe, contact, prenom, nom))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": "Email déjà utilisé"}
            return {"error": str(error)}
        if not result:
            return {"error": "Échec de la création"}
        return dict(result)

    @staticmethod
    def get_by_id(client_id):
        """Récupère un client par son ID. Retourne None si non trouvé."""
        if not client_id or client_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT id, email, contact, prenom, nom
            FROM clients
            WHERE id = %s
        """
        result, error = fetch_one(query, (client_id,))
        if error:
            return {"error": str(error)}
        return dict(result) if result else None

    @staticmethod
    def get_by_email(email):
        """Récupère un client par son email. Retourne None si non trouvé."""
        if not email:
            return {"error": "Email invalide"}

        query = """
            SELECT id, email, contact, prenom, nom
            FROM clients
            WHERE email = %s
        """
        result, error = fetch_one(query, (email,))
        if error:
            return {"error": str(error)}
        return dict(result) if result else None

    @staticmethod
    def get_all():
        """Récupère tous les clients."""
        query = """
            SELECT id, email, contact, prenom, nom
            FROM clients
            ORDER BY nom, prenom
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": str(error)}]
        return [dict(row) for row in results]

    @staticmethod
    def update(client_id, email=None, mot_de_passe=None, contact=None, prenom=None, nom=None):
        """Met à jour un client. Retourne les données mises à jour ou None si non trouvé."""
        if not client_id or client_id <= 0:
            return {"error": "ID invalide"}

        query = """
            UPDATE clients
            SET email = COALESCE(%s, email),
                mot_de_passe = COALESCE(%s, mot_de_passe),
                contact = COALESCE(%s, contact),
                prenom = COALESCE(%s, prenom),
                nom = COALESCE(%s, nom)
            WHERE id = %s
            RETURNING id, email, contact, prenom, nom
        """
        result, error = fetch_one(query, (email, mot_de_passe, contact, prenom, nom, client_id))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": "Email déjà utilisé"}
            return {"error": str(error)}
        return dict(result) if result else None

    @staticmethod
    def delete(client_id):
        """Supprime un client. Retourne le statut de l'opération."""
        if not client_id or client_id <= 0:
            return {"error": "ID invalide"}

        query = """
            DELETE FROM clients
            WHERE id = %s
            RETURNING id
        """
        result, error = fetch_one(query, (client_id,))
        if error:
            return {"error": str(error)}
        return {"success": bool(result), "id": client_id}
