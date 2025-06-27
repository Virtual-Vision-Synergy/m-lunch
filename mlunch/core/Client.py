import psycopg2.errors
from database.db import execute_query, fetch_query, fetch_one

class Client:
    def __init__(self, id=None, email=None, mot_de_passe=None, contact=None, prenom=None, nom=None, date_inscri=None):
        self.id = id
        self.email = email
        self.mot_de_passe = mot_de_passe
        self.contact = contact
        self.prenom = prenom
        self.nom = nom
        self.date_inscri = date_inscri

    @staticmethod
    def Create(email, mot_de_passe, contact=None, prenom=None, nom=None):
        if not email or not mot_de_passe:
            return {"error": "Email et mot de passe requis"}

        query = """
            INSERT INTO clients (email, mot_de_passe, contact, prenom, nom)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, email, mot_de_passe, contact, prenom, nom, date_inscri
        """
        result, error = fetch_one(query, (email, mot_de_passe, contact, prenom, nom))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": "Email déjà utilisé"}
            return {"error": str(error)}
        if not result:
            return {"error": "Échec de la création"}
        return Client(**result)

    @staticmethod
    def GetById(client_id):
        if not client_id or client_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT id, email, mot_de_passe, contact, prenom, nom, date_inscri
            FROM clients
            WHERE id = %s
        """
        result, error = fetch_one(query, (client_id,))
        if error:
            return {"error": str(error)}
        return Client(**result) if result else None

    @staticmethod
    def GetByEmail(email):
        if not email:
            return {"error": "Email invalide"}

        query = """
            SELECT id, email, mot_de_passe, contact, prenom, nom, date_inscri
            FROM clients
            WHERE email = %s
        """
        result, error = fetch_one(query, (email,))
        if error:
            return {"error": str(error)}
        return Client(**result) if result else None

    @staticmethod
    def GetAll():
        query = """
            SELECT id, email, mot_de_passe, contact, prenom, nom, date_inscri
            FROM clients
            ORDER BY nom, prenom
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": str(error)}]
        return [Client(**row) for row in results]

    def Update(self):
        if not self.id or self.id <= 0:
            return {"error": "ID invalide"}

        query = """
            UPDATE clients
            SET email = COALESCE(%s, email),
                mot_de_passe = COALESCE(%s, mot_de_passe),
                contact = COALESCE(%s, contact),
                prenom = COALESCE(%s, prenom),
                nom = COALESCE(%s, nom)
            WHERE id = %s
            RETURNING id, email, mot_de_passe, contact, prenom, nom, date_inscri
        """
        result, error = fetch_one(query, (
            self.email,
            self.mot_de_passe,
            self.contact,
            self.prenom,
            self.nom,
            self.id
        ))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": "Email déjà utilisé"}
            return {"error": str(error)}
        if result:
            self.__init__(**result)
            return self
        return None

    def Delete(self):
        if not self.id or self.id <= 0:
            return {"error": "ID invalide"}

        query = """
            DELETE FROM clients
            WHERE id = %s
            RETURNING id
        """
        result, error = fetch_one(query, (self.id,))
        if error:
            return {"error": str(error)}
        return {"success": bool(result), "id": self.id}
