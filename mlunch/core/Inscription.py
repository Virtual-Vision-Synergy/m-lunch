import psycopg2.errors
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime

class Inscription:

    @staticmethod
    def inscrire( nom, prenom, email, mot_de_passe, telephone):
        """
        Inscrit un client dans la base de données.
        """
        try:

            query = """
                INSERT INTO clients (email, mot_de_passe, contact, prenom, nom)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (email, mot_de_passe, telephone, prenom, nom)
            
            success = execute_query(query, params)

            if success:
                print(f"[Succès] {email} inscrit avec succès.")
                return True
            else:
                print(f"[Erreur] Insertion échouée pour {email}.")
                return False

        except psycopg2.errors.UniqueViolation:
            print(f"[Erreur] L'email {email} est déjà utilisé.")
            return False

        except Exception as e:
            print(f"[Exception] {e}")
            return False


    @staticmethod
    def getClientId(email):
        query = "SELECT id FROM clients WHERE email = %s"
        result = fetch_one(query, (email,))
        return result['id'] if result else None


    @staticmethod
    def getZone( lat, lon):
        """
        Retourne la zone contenant ou la plus proche (à < 5km) d'un point.
        """
        query = """
            SELECT id, nom,
                   ST_Distance(zone, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) AS distance
            FROM zones
            WHERE ST_DWithin(zone, ST_SetSRID(ST_MakePoint(%s, %s), 4326), 5000)
            ORDER BY distance ASC
            LIMIT 1
        """
        result = fetch_one(query, (lon, lat, lon, lat))  # longitude d'abord
        return result


    @staticmethod
    def insertZoneClient( client_id, zone_id):
        query = "INSERT INTO zones_clients (client_id, zone_id) VALUES (%s, %s)"
        return execute_query(query, (client_id, zone_id))
    

    @staticmethod
    def getZoneId(nom):
        query = "SELECT id FROM zones WHERE nom = %s"
        result = fetch_one(query, (nom,))
        return result['id'] if result else None

    @staticmethod
    def getZoneByName(nom):
        query = "SELECT * FROM zones WHERE nom = %s"
        return fetch_one(query, (nom,))
