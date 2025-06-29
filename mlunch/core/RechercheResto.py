import psycopg2.errors
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime

class RechercheResto:

    @staticmethod
    def getRestaurantBySecteurOuNom(secteur=None, nom=None):
        """
        Recherche les restaurants par secteur (zone) ou par nom.
        - secteur: nom de la zone pour filtrer les restaurants dans cette zone
        - nom: nom du restaurant (recherche partielle)
        """
        conditions = []
        params = []
        
        # Construire la requête de base SANS evaluations
        query = """
            SELECT r.id, r.nom, r.adresse, r.image, 
                ST_X(r.geo_position::geometry) as longitude,
                ST_Y(r.geo_position::geometry) as latitude,
                0 as note_moyenne,
                z.nom as zone_nom
            FROM restaurants r
            LEFT JOIN zones z ON ST_DWithin(r.geo_position, z.zone,0)
        """
        
        # Si recherche par secteur
        if secteur:
            conditions.append("z.nom = %s")
            params.append(secteur)
        
        # Si recherche par nom ou adresse
        if nom:
            conditions.append("(r.nom ILIKE %s OR r.adresse ILIKE %s)")
            params.extend([f"%{nom}%", f"%{nom}%"])  # Recherche dans nom ET adresse
        
        # Ajouter les conditions WHERE
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY r.nom"
        
        return fetch_query(query, params)

    @staticmethod
    def getRestaurantByAddress(adresse):
        """
        Recherche de restaurants par adresse spécifique
        """
        query = """
            SELECT r.id, r.nom, r.adresse, r.image, 
                ST_X(r.geo_position::geometry) as longitude,
                ST_Y(r.geo_position::geometry) as latitude,
                0 as note_moyenne,
                z.nom as zone_nom
            FROM restaurants r
            LEFT JOIN zones z ON ST_DWithin(r.geo_position, z.zone,0)
            WHERE r.adresse ILIKE %s
            ORDER BY r.nom
        """
        return fetch_query(query, [f"%{adresse}%"])

    @staticmethod
    def checkRestaurantInUserZone(restaurant_id, user_zone):
        """
        Vérifie si un restaurant dessert la zone de l'utilisateur
        """
        query = """
            SELECT COUNT(*) as count
            FROM restaurants r
            JOIN zones z ON ST_DWithin(r.geo_position, z.zone,0)
            WHERE r.id = %s AND z.nom = %s
        """
        result = fetch_one(query, [restaurant_id, user_zone])
        return result['count'] > 0 if result else False

    @staticmethod
    def getRestaurantDetails(restaurant_id):
        """
        Récupère les détails complets d'un restaurant
        """
        query = """
            SELECT r.id, r.nom, r.adresse, r.image, 
                ST_X(r.geo_position::geometry) as longitude,
                ST_Y(r.geo_position::geometry) as latitude,
                0 as note_moyenne,
                0 as nb_evaluations,
                z.nom as zone_nom
            FROM restaurants r
            LEFT JOIN zones z ON ST_DWithin(r.geo_position, z.zone,0)
            WHERE r.id = %s
        """
        return fetch_one(query, [restaurant_id])

    # MÉTHODES OPTIONNELLES POUR PLUS TARD QUAND VOUS AUREZ LA TABLE EVALUATIONS
    @staticmethod
    def getRestaurantBySecteurOuNomAvecNotes(secteur=None, nom=None):
        """
        Version avec notes - à utiliser quand la table evaluations existera
        """
        conditions = []
        params = []
        
        query = """
            SELECT r.id, r.nom, r.adresse, r.image, 
                ST_X(r.geo_position::geometry) as longitude,
                ST_Y(r.geo_position::geometry) as latitude,
                COALESCE(AVG(ev.note), 0) as note_moyenne,
                z.nom as zone_nom
            FROM restaurants r
            LEFT JOIN evaluations ev ON r.id = ev.restaurant_id
            LEFT JOIN zones z ON ST_DWithin(r.geo_position, z.zone,0)
        """
        
        if secteur:
            conditions.append("z.nom = %s")
            params.append(secteur)
        
        if nom:
            conditions.append("(r.nom ILIKE %s OR r.adresse ILIKE %s)")
            params.extend([f"%{nom}%", f"%{nom}%"])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " GROUP BY r.id, r.nom, r.adresse, r.image, r.geo_position, z.nom ORDER BY r.nom"
        
        return fetch_query(query, params)
