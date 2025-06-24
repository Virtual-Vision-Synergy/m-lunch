from ...database.db import execute_query, fetch_query, fetch_one

class Client:
    """Classe représentant un client dans le système."""
    
    @staticmethod
    def create(email, mot_de_passe, contact=None, prenom=None, nom=None):
        """Crée un nouveau client."""
        query = """
            INSERT INTO clients (email, mot_de_passe, contact, prenom, nom)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, email, contact, prenom, nom
        """
        result = fetch_one(query, (email, mot_de_passe, contact, prenom, nom))
        return result

    @staticmethod
    def get_by_id(client_id):
        """Récupère un client par son ID."""
        query = """
            SELECT id, email, contact, prenom, nom
            FROM clients
            WHERE id = %s
        """
        return fetch_one(query, (client_id,))

    @staticmethod
    def get_by_email(email):
        """Récupère un client par son email."""
        query = """
            SELECT id, email, contact, prenom, nom
            FROM clients
            WHERE email = %s
        """
        return fetch_one(query, (email,))

    @staticmethod
    def update(client_id, email=None, mot_de_passe=None, contact=None, prenom=None, nom=None):
        """Met à jour les informations d'un client."""
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
        result = fetch_one(query, (email, mot_de_passe, contact, prenom, nom, client_id))
        return result

    @staticmethod
    def delete(client_id):
        """Supprime un client."""
        query = "DELETE FROM clients WHERE id = %s"
        return execute_query(query, (client_id,))