import psycopg2.errors
from database.db import execute_query, fetch_query, fetch_one
from django.shortcuts import render
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
class Client:
    """Classe représentant un client dans le système."""

    @staticmethod
    def CreateClient(email, mot_de_passe, contact=None, prenom=None, nom=None):
        """Crée un nouveau client avec les informations fournies."""
        if not isinstance(email, str) or not email:
            return {"error": "Email invalide"}
        if not isinstance(mot_de_passe, str) or not mot_de_passe:
            return {"error": "Mot de passe invalide"}
        if contact is not None and not isinstance(contact, str):
            return {"error": "Contact invalide"}
        if prenom is not None and not isinstance(prenom, str):
            return {"error": "Prénom invalide"}
        if nom is not None and not isinstance(nom, str):
            return {"error": "Nom invalide"}

        # Démarrer une transaction
        try:
            # Insérer le client
            query_client = """
                INSERT INTO clients (email, mot_de_passe, contact, prenom, nom)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, email, contact, prenom, nom, date_inscri
            """
            result_client, error = fetch_one(query_client, (email, mot_de_passe, contact, prenom, nom))
            if error:
                if isinstance(error, psycopg2.errors.UniqueViolation):
                    return {"error": "Email déjà utilisé"}
                return {"error": f"Erreur lors de la création du client : {str(error)}"}
            if not result_client:
                return {"error": "Échec de la création du client"}

            # Retourner les informations du client
            return {
                "client": dict(result_client)
            }

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetClientFromId(client_id):
        """Récupère un client par son ID. Retourne un dictionnaire avec les informations du client ou un dictionnaire d'erreur."""
        if not isinstance(client_id, int) or client_id <= 0:
            return {"error": "L'ID du client doit être un entier positif"}

        query = """
            SELECT id, email, contact, prenom, nom, date_inscri 
            FROM clients 
            WHERE id = %s
        """
        result, error = fetch_one(query, (client_id,))
        if error:
            return {"error": f"Erreur de base de données : {str(error)}"}
        return dict(result) if result else {"error": "Client non trouvé"}

    @staticmethod
    def GetClientFromEmail(email):
        """Récupère un client par son email. Retourne un dictionnaire avec les informations du client ou un dictionnaire d'erreur."""
        if not isinstance(email, str) or not email:
            return {"error": "L'email doit être une chaîne non vide"}
        
        try:
            validate_email(email)
        except ValidationError:
            return {"error": "Format d'email invalide"}

        query = """
            SELECT id, email, contact, prenom, nom, date_inscri 
            FROM clients 
            WHERE email = %s
        """
        result, error = fetch_one(query, (email,))
        if error:
            return {"error": f"Erreur de base de données : {str(error)}"}
        return dict(result) if result else {"error": "Client non trouvé"}

    @staticmethod
    def GetAllClients():
        """Récupère tous les clients triés par nom et prénom. Retourne une liste de dictionnaires ou un dictionnaire d'erreur."""
        query = """
            SELECT id, email, contact, prenom, nom, date_inscri
            FROM clients
            ORDER BY nom, prenom
        """
        results, error = fetch_query(query)
        if error:
            return {"error": f"Erreur de base de données : {str(error)}"}
        if not results:
            return {"error": "Aucun client trouvé"}
        return [dict(row) for row in results]

    @staticmethod
    def UpdateClient(client_id, email=None, mot_de_passe=None, contact=None, prenom=None, nom=None):
        """Met à jour les informations d'un client par son ID. Retourne un dictionnaire avec les données mises à jour ou un dictionnaire d'erreur."""
        if not isinstance(client_id, int) or client_id <= 0:
            return {"error": "L'ID du client doit être un entier positif"}

        # Validation des paramètres
        if email is not None:
            if not isinstance(email, str) or not email:
                return {"error": "L'email doit être une chaîne non vide"}
            try:
                validate_email(email)
            except ValidationError:
                return {"error": "Format d'email invalide"}
        
        if mot_de_passe is not None and (not isinstance(mot_de_passe, str) or not mot_de_passe):
            return {"error": "Le mot de passe doit être une chaîne non vide"}
        
        if contact is not None and not isinstance(contact, str):
            return {"error": "Le contact doit être une chaîne"}
        
        if prenom is not None and not isinstance(prenom, str):
            return {"error": "Le prénom doit être une chaîne"}
        
        if nom is not None and not isinstance(nom, str):
            return {"error": "Le nom doit être une chaîne"}

        query = """
            UPDATE clients
            SET email = COALESCE(%s, email),
                mot_de_passe = COALESCE(%s, mot_de_passe),
                contact = COALESCE(%s, contact),
                prenom = COALESCE(%s, prenom),
                nom = COALESCE(%s, nom)
            WHERE id = %s
            RETURNING id, email, contact, prenom, nom, date_inscri
        """
        result, error = fetch_one(query, (email, mot_de_passe, contact, prenom, nom, client_id))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": "Email déjà utilisé"}
            return {"error": f"Erreur de base de données : {str(error)}"}
        return dict(result) if result else {"error": "Client non trouvé"}

    @staticmethod
    def DeleteClient(client_id):
        """Supprime un client par son ID. Retourne un dictionnaire indiquant le succès ou une erreur."""
        if not isinstance(client_id, int) or client_id <= 0:
            return {"error": "L'ID du client doit être un entier positif"}

        query = """
            DELETE FROM clients
            WHERE id = %s
            RETURNING id
        """
        result, error = fetch_one(query, (client_id,))
        if error:
            return {"error": f"Erreur de base de données : {str(error)}"}
        if not result:
            return {"error": "Client non trouvé"}
        return {"success": True, "id": client_id}
