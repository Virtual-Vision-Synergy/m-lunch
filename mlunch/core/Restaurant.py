import psycopg2.errors
from typing import Optional, Dict, List, Any, Tuple
from database.db import execute_query, fetch_query, fetch_one
from database import db
from datetime import datetime, timedelta

class Restaurant:
    """Classe représentant un restaurant dans le système."""

    @staticmethod
    def create(nom, horaire_debut, horaire_fin, adresse, image, geo_position, initial_statut_id):
        """Crée un nouveau restaurant avec son historique et statut initial."""
        # Validation des entrées
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "ID statut invalide"}
        if not nom or not isinstance(nom, str):
            return {"error": "Nom de restaurant invalide"}
        if not adresse or not isinstance(adresse, str):
            return {"error": "Adresse invalide"}

        # Démarrer une transaction
        try:
            # Insérer le restaurant
            query_restaurant = """
                INSERT INTO restaurants (nom, horaire_debut, horaire_fin, adresse, image, geo_position)
                VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
                RETURNING id, nom, horaire_debut, horaire_fin, adresse, image, geo_position
            """
            point_wkt = f"POINT({geo_position[0]} {geo_position[1]})" if geo_position else None
            
            result_restaurant, error = fetch_one(query_restaurant, 
                                            (nom, horaire_debut, horaire_fin, adresse, image, point_wkt))
            
            if error:
                return {"error": f"Erreur lors de la création du restaurant : {str(error)}"}
            if not result_restaurant:
                return {"error": "Échec de la création du restaurant"}

            restaurant_id = result_restaurant['id']

            # Vérifier si le statut existe
            query_statut = """
                SELECT id FROM statut_restaurant WHERE id = %s
            """
            result_statut, error = fetch_one(query_statut, (initial_statut_id,))
            if error or not result_statut:
                return {"error": "Statut restaurant non trouvé"}

            # Insérer dans l'historique
            query_historique = """
                INSERT INTO historique_statut_restaurant (restaurant_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, restaurant_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (restaurant_id, initial_statut_id))
            if error:
                return {"error": f"Erreur lors de la création de l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de la création de l'historique"}

            # Retourner les informations complètes
            return {
                "restaurant": dict(result_restaurant),
                "historique": dict(result_historique)
            }

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def get_by_id(restaurant_id):
        """
        Récupère un restaurant par son ID avec son historique complet des statuts.
        
        Args:
            restaurant_id (int): L'ID du restaurant à récupérer.
        
        Returns:
            dict: Dictionnaire avec:
                - 'restaurant': les infos du restaurant
                - 'statuts': liste des statuts historiques
                En cas d'erreur, retourne un dictionnaire avec une clé 'error'.
        """
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "ID restaurant invalide"}

        try:
            # Requête pour les infos du restaurant
            query_restaurant = """
                SELECT 
                    r.id, r.nom, r.horaire_debut, r.horaire_fin, 
                    r.adresse, r.image, ST_AsText(r.geo_position) as geo_position,
                    sr.appellation as statut_actuel
                FROM restaurants r
                LEFT JOIN (
                    SELECT restaurant_id, statut_id
                    FROM historique_statut_restaurant
                    WHERE id = (
                        SELECT MAX(id) 
                        FROM historique_statut_restaurant 
                        WHERE restaurant_id = %s
                    )
                ) latest ON r.id = latest.restaurant_id
                LEFT JOIN statut_restaurant sr ON latest.statut_id = sr.id
                WHERE r.id = %s
            """
            
            # Requête pour l'historique des statuts
            query_historique = """
                SELECT * FROM v_restaurant_status_history WHERE restaurant_id = %s ORDER BY mis_a_jour_le DESC
            """

            # Exécution des requêtes
            restaurant, error = fetch_one(query_restaurant, (restaurant_id, restaurant_id))
            if error or not restaurant:
                return {"error": "Restaurant non trouvé" if not error else f"Erreur : {str(error)}"}
            
            historiques, error = fetch_query(query_historique, (restaurant_id,))
            if error:
                return {"error": f"Erreur historique : {str(error)}"}

            # Formatage des résultats
            result = {
                "restaurant": dict(restaurant),
                "statuts": [dict(h) for h in historiques] if historiques else []
            }
            
            return result

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
            """Récupère tous les restaurants."""
            query = """
                SELECT id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
                FROM restaurants
                ORDER BY nom
            """
            results, error = fetch_query(query)
            if error:
                return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
            return [dict(row) for row in results]

    @staticmethod
    def update(restaurant_id, statut_id=None, nom=None, horaire_debut=None, horaire_fin=None, 
                     adresse=None, image=None, geo_position=None):
        """
        Met à jour un restaurant et son historique de statut.
        Retourne les données mises à jour ou un dictionnaire d'erreur.
        """
        # Validation des paramètres
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "ID restaurant invalide"}
        if statut_id is not None and (not isinstance(statut_id, int) or statut_id <= 0):
            return {"error": "ID statut invalide"}
        if nom is not None and (not isinstance(nom, str) or len(nom) > 150):
            return {"error": "Nom invalide : doit être une chaîne de 150 caractères maximum"}
        if adresse is not None and not isinstance(adresse, str):
            return {"error": "Adresse invalide : doit être une chaîne"}
        if image is not None and not isinstance(image, str):
            return {"error": "Image invalide : doit être une chaîne"}
        if geo_position is not None and (
            not isinstance(geo_position, (tuple, list)) or 
            len(geo_position) != 2 or 
            not all(isinstance(x, (int, float)) for x in geo_position)
        ):
            return {"error": "Position géographique invalide : doit être un tuple (longitude, latitude)"}

        try:
            # Vérifier si le restaurant existe
            query_check_restaurant = """
                SELECT id FROM restaurants WHERE id = %s
            """
            result_check, error = fetch_one(query_check_restaurant, (restaurant_id,))
            if error or not result_check:
                return {"error": "Restaurant non trouvé"}

            # Vérifier si le statut existe (si fourni)
            if statut_id is not None:
                query_check_statut = """
                    SELECT id FROM statut_restaurant WHERE id = %s
                """
                result_statut, error = fetch_one(query_check_statut, (statut_id,))
                if error or not result_statut:
                    return {"error": "Statut restaurant non trouvé"}

            # Préparation de la position géographique
            geo_wkt = None
            if geo_position is not None:
                geo_wkt = f"POINT({geo_position[0]} {geo_position[1]})"

            # Mettre à jour le restaurant
            query_update = """
                UPDATE restaurants
                SET 
                    nom = COALESCE(%s, nom),
                    horaire_debut = COALESCE(%s, horaire_debut),
                    horaire_fin = COALESCE(%s, horaire_fin),
                    adresse = COALESCE(%s, adresse),
                    image = COALESCE(%s, image),
                    geo_position = CASE WHEN %s IS NULL THEN geo_position ELSE ST_GeomFromText(%s, 4326) END
                WHERE id = %s
                RETURNING id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
            """
            result_restaurant, error = fetch_one(query_update, (
                nom, horaire_debut, horaire_fin, adresse, image, 
                geo_wkt, geo_wkt, restaurant_id
            ))
            if error:
                return {"error": f"Erreur lors de la mise à jour du restaurant : {str(error)}"}

            # Si statut fourni, mettre à jour l'historique
            result_historique = None
            if statut_id is not None:
                query_historique = """
                    INSERT INTO historique_statut_restaurant (restaurant_id, statut_id)
                    VALUES (%s, %s)
                    RETURNING id, restaurant_id, statut_id, mis_a_jour_le
                """
                result_historique, error = fetch_one(query_historique, (restaurant_id, statut_id))
                if error:
                    return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}

            # Préparation du résultat
            response = {
                "restaurant": dict(result_restaurant) if result_restaurant else None,
                "historique": dict(result_historique) if result_historique else None
            }

            return response

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def delete(restaurant_id,statut_id):
        """Met à jour un restaurant Retourne les données mises à jour ou None si non trouvé."""
        if not restaurant_id or statut_id <= 0:
            return {"error": "ID invalide"}

        query = """
            insert into historique_statut_restaurant (restaurant_id,statut_id)
            values(%s,%s) 
            RETURNING id, restaurant_id, statut_id
        """
        result, error = fetch_one(query, (restaurant_id,statut_id))
        if error:
            return {"error": f"Erreur lors de la suppression : {str(error)}"}
        return {"success": bool(result), "id": restaurant_id}
        return result if result else None

    @staticmethod
    def list(secteur=None, horaire=None):
        params = []
        query = "SELECT * FROM v_restaurants_list WHERE 1=1"
        if secteur:
            query += " AND secteur = %s"
            params.append(secteur)
        if horaire:
            query += " AND %s BETWEEN horaire_debut AND horaire_fin"
            params.append(horaire)
        return db.fetch_query(query, tuple(params))

    @staticmethod
    def detail(restaurant_id):
        query = "SELECT * FROM v_restaurants_detail WHERE id = %s"
        return db.fetch_one(query, (restaurant_id,))

    @staticmethod
    def add(data):
        db.execute_query(
            "INSERT INTO restaurants (nom, horaire_debut, horaire_fin, adresse, image, geo_position) VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326)) RETURNING id",
            (data['nom'], data['horaire_debut'], data['horaire_fin'], data['adresse'], data['image'], data['geo_position'])
        )
        restaurant = db.fetch_one("SELECT id FROM restaurants WHERE nom=%s ORDER BY id DESC LIMIT 1", (data['nom'],))
        restaurant_id = restaurant['id']
        zone = db.fetch_one("SELECT id FROM zones WHERE nom=%s", (data['secteur'],))
        if zone:
            db.execute_query("INSERT INTO zones_restaurant (restaurant_id, zone_id) VALUES (%s, %s)", (restaurant_id, zone['id']))
        db.execute_query("INSERT INTO commissions (restaurant_id, valeur) VALUES (%s, %s)", (restaurant_id, data['commission']))
        statut_obj = db.fetch_one("SELECT id FROM statut_restaurant WHERE appellation=%s", (data['statut'],))
        if statut_obj:
            db.execute_query("INSERT INTO historique_statut_restaurant (restaurant_id, statut_id) VALUES (%s, %s)", (restaurant_id, statut_obj['id']))
        return restaurant_id

    @staticmethod
    def edit(restaurant_id, data):
        db.execute_query(
            "UPDATE restaurants SET nom=%s, horaire_debut=%s, horaire_fin=%s, adresse=%s, image=%s, geo_position=ST_GeomFromText(%s, 4326) WHERE id=%s",
            (data['nom'], data['horaire_debut'], data['horaire_fin'], data['adresse'], data['image'], data['geo_position'], restaurant_id)
        )
        zone = db.fetch_one("SELECT id FROM zones WHERE nom=%s", (data['secteur'],))
        if zone:
            db.execute_query("UPDATE zones_restaurant SET zone_id=%s WHERE restaurant_id=%s", (zone['id'], restaurant_id))
        db.execute_query("UPDATE commissions SET valeur=%s WHERE restaurant_id=%s", (data['commission'], restaurant_id))
        statut_obj = db.fetch_one("SELECT id FROM statut_restaurant WHERE appellation=%s", (data['statut'],))
        if statut_obj:
            db.execute_query("INSERT INTO historique_statut_restaurant (restaurant_id, statut_id) VALUES (%s, %s)", (restaurant_id, statut_obj['id']))

    @staticmethod
    def can_delete(restaurant_id):
        en_cours = db.fetch_one(
            "SELECT nb FROM v_restaurant_commandes_en_cours WHERE restaurant_id = %s", (restaurant_id,)
        )
        return not (en_cours and en_cours['nb'] > 0)

    @staticmethod
    def is_closed(restaurant_id):
        last_statut = db.fetch_one("""
            SELECT s.appellation
            FROM historique_statut_restaurant hsr
            JOIN statut_restaurant s ON hsr.statut_id = s.id
            WHERE hsr.restaurant_id = %s
            ORDER BY hsr.mis_a_jour_le DESC, hsr.id DESC
            LIMIT 1
        """, (restaurant_id,))
        return last_statut and last_statut['appellation'] == 'Ferme'

    @staticmethod
    def close(restaurant_id):
        statut_ferme = db.fetch_one("SELECT id FROM statut_restaurant WHERE appellation='Ferme'")
        if statut_ferme:
            db.execute_query("""
                INSERT INTO historique_statut_restaurant 
                (restaurant_id, statut_id, mis_a_jour_le) 
                VALUES (%s, %s, CURRENT_TIMESTAMP)
            """, (restaurant_id, statut_ferme['id']))
            return True
        return False

    @staticmethod
    def orders(restaurant_id):
        query = "SELECT * FROM v_restaurant_orders WHERE restaurant_id = %s"
        return db.fetch_query(query, (restaurant_id,))

    @staticmethod
    def financial(restaurant_id, date_from, date_to):
        """Calcule les données financières pour un restaurant."""
        restaurant = db.fetch_one("""
            SELECT r.nom, r.image, r.adresse,
                   c.valeur as commission
            FROM restaurants r
            LEFT JOIN commissions c ON c.restaurant_id = r.id
            WHERE r.id = %s
        """, (restaurant_id,))

        # Utilisation de la vue pour le total brut et le nombre de commandes
        query = """
            SELECT COALESCE(SUM(total), 0) as total_brut,
                   COALESCE(SUM(nb_commandes), 0) as nb_commandes
            FROM v_restaurant_financial_daily
            WHERE restaurant_id = %s
              AND jour >= %s AND jour < %s
        """
        params = (restaurant_id, date_from, date_to)
        result = db.fetch_one(query, params)
        if result is not None:
            total_brut = result.get('total_brut', 0)
            nb_commandes = result.get('nb_commandes', 0)
        else:
            total_brut = 0
            nb_commandes = 0

        commission_percent = restaurant.get('commission', 0)
        commission_montant = (total_brut * commission_percent / 100) if total_brut else 0

        query_frais = """
            SELECT COALESCE(SUM(valeur), 0) as total_frais FROM commissions WHERE restaurant_id = %s
            AND mis_a_jour_le >= %s AND mis_a_jour_le < %s
        """
        frais = db.fetch_one(query_frais, (restaurant_id, date_from, date_to))
        total_frais = frais['total_frais'] if frais else 0

        benefice_net = total_brut - commission_montant - total_frais

        return {
            'restaurant': restaurant,
            'total_brut': total_brut,
            'commission_percent': commission_percent,
            'commission_montant': commission_montant,
            'total_frais': total_frais,
            'benefice_net': benefice_net,
            'nb_commandes': nb_commandes
        }

    @staticmethod
    def financial_graph(restaurant_id, date_from, date_to, periode):
        """Génère les données de graphique financier pour un restaurant."""
        graph_labels = []
        graph_values = []

        if periode in ['today', 'custom'] and isinstance(date_from, datetime) and isinstance(date_to, datetime) and (date_to - date_from).days < 31:
            # Utilisation de la vue jour par jour
            query_graph = """
                SELECT jour, total
                FROM v_restaurant_financial_daily
                WHERE restaurant_id = %s
                  AND jour >= %s AND jour < %s
                ORDER BY jour
            """
            rows = db.fetch_query(query_graph, (restaurant_id, date_from, date_to))
            for row in rows:
                graph_labels.append(row['jour'].strftime('%d/%m'))
                graph_values.append(float(row['total']))
        else:
            # Utilisation de la vue par mois
            query_graph = """
                SELECT mois, total
                FROM v_restaurant_financial_monthly
                WHERE restaurant_id = %s
                  AND TO_DATE(mois, 'MM/YYYY') >= %s AND TO_DATE(mois, 'MM/YYYY') < %s
                ORDER BY TO_DATE(mois, 'MM/YYYY')
            """
            rows = db.fetch_query(query_graph, (restaurant_id, date_from, date_to))
            for row in rows:
                graph_labels.append(row['mois'])
                graph_values.append(float(row['total']))

        return graph_labels, graph_values

