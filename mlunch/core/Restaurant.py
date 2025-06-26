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
                SELECT 
                    h.id, h.statut_id, h.mis_a_jour_le,
                    sr.appellation as statut_nom
                FROM historique_statut_restaurant h
                JOIN statut_restaurant sr ON h.statut_id = sr.id
                WHERE h.restaurant_id = %s
                ORDER BY h.mis_a_jour_le DESC
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
        base_query = """
            SELECT r.*,
                   c.valeur as commission,
                   z.nom as secteur,
                   s.statut as statut
            FROM restaurants r
            LEFT JOIN commissions c ON c.restaurant_id = r.id
            LEFT JOIN zones_restaurant zr ON zr.restaurant_id = r.id
            LEFT JOIN zones z ON z.id = zr.zone_id
            LEFT JOIN (
                SELECT hsr.restaurant_id, sr.appellation as statut
                FROM (
                    SELECT DISTINCT ON (restaurant_id) *
                    FROM historique_statut_restaurant
                    ORDER BY restaurant_id, mis_a_jour_le DESC, id DESC
                ) hsr
                JOIN statut_restaurant sr ON hsr.statut_id = sr.id
            ) s ON s.restaurant_id = r.id
            WHERE (s.statut != 'Ferme' OR s.statut IS NULL)
        """
        if secteur:
            base_query += " AND z.nom = %s"
            params.append(secteur)
        if horaire:
            base_query += " AND r.horaire_debut <= %s AND r.horaire_fin >= %s"
            params.extend([horaire, horaire])
        base_query += " GROUP BY r.id, c.valeur, z.nom, s.statut ORDER BY r.id"
        return db.fetch_query(base_query, params)

    @staticmethod
    def detail(restaurant_id):
        query = """
            SELECT r.*,
                c.valeur as commission,
                s.appellation as statut,
                z.nom as secteur
            FROM restaurants r
            LEFT JOIN commissions c ON c.restaurant_id = r.id
            LEFT JOIN (
                SELECT DISTINCT ON (restaurant_id) restaurant_id, statut_id
                FROM historique_statut_restaurant
                WHERE restaurant_id = %s
                ORDER BY restaurant_id, mis_a_jour_le DESC
            ) hsr ON hsr.restaurant_id = r.id
            LEFT JOIN statut_restaurant s ON s.id = hsr.statut_id
            LEFT JOIN zones_restaurant zr ON zr.restaurant_id = r.id
            LEFT JOIN zones z ON z.id = zr.zone_id
            WHERE r.id = %s
            GROUP BY r.id, c.valeur, s.appellation, z.nom
        """
        return db.fetch_one(query, (restaurant_id, restaurant_id))

    @staticmethod
    def add(data):
        db.execute_query(
            "INSERT INTO restaurants (nom, horaire_debut, horaire_fin, image) VALUES (%s, %s, %s, %s) RETURNING id",
            (data['nom'], data['horaire_debut'], data['horaire_fin'], data['image'])
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
            "UPDATE restaurants SET nom=%s, horaire_debut=%s, horaire_fin=%s, image=%s WHERE id=%s",
            (data['nom'], data['horaire_debut'], data['horaire_fin'], data['image'], restaurant_id)
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
        en_cours = db.fetch_one("""
            SELECT COUNT(*) as nb
            FROM commandes c
            JOIN commande_repas cr ON cr.commande_id = c.id
            JOIN repas r ON r.id = cr.repas_id
            JOIN repas_restaurant rr ON rr.repas_id = r.id
            WHERE rr.restaurant_id = %s
            AND c.id IN (
                SELECT hsc.commande_id
                FROM historique_statut_commande hsc
                JOIN statut_commande sc ON sc.id = hsc.statut_id
                WHERE sc.appellation IN ('En attente', 'En cours')
            )
        """, (restaurant_id,))
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
        return db.fetch_query("""
            SELECT c.id, c.cree_le, cl.nom as client_nom
            FROM commandes c
            JOIN clients cl ON cl.id = c.client_id
            JOIN commande_repas cr ON cr.commande_id = c.id
            JOIN repas r ON r.id = cr.repas_id
            JOIN repas_restaurant rr ON rr.repas_id = r.id
            WHERE rr.restaurant_id = %s
            GROUP BY c.id, cl.nom
            ORDER BY c.cree_le DESC
        """, (restaurant_id,))

    @staticmethod
    def financial(restaurant_id, date_from, date_to):
        restaurant = db.fetch_one("""
            SELECT r.nom, r.image, z.nom as secteur, c.valeur as commission
            FROM restaurants r
            LEFT JOIN zones_restaurant zr ON zr.restaurant_id = r.id
            LEFT JOIN zones z ON z.id = zr.zone_id
            LEFT JOIN commissions c ON c.restaurant_id = r.id
            WHERE r.id = %s
            GROUP BY r.nom, r.image, z.nom, c.valeur
        """, (restaurant_id,))
        query = """
            SELECT 
                COALESCE(SUM(cr.quantite * r.prix), 0) as total_brut
            FROM commandes co
            JOIN commande_repas cr ON cr.commande_id = co.id
            JOIN repas r ON r.id = cr.repas_id
            JOIN repas_restaurant rr ON rr.repas_id = r.id
            JOIN historique_statut_commande hsc ON hsc.commande_id = co.id
            WHERE rr.restaurant_id = %s
            AND hsc.statut_id = (
                SELECT id FROM statut_commande WHERE appellation = 'Livrée' LIMIT 1
            )
            AND co.cree_le >= %s AND co.cree_le < %s
        """
        total_brut = db.fetch_one(query, (restaurant_id, date_from, date_to))['total_brut']
        commission = restaurant['commission'] if restaurant and restaurant['commission'] is not None else 0
        montant_commission = round(total_brut * commission / 100, 2)
        frais = db.fetch_one("""
            SELECT COALESCE(SUM(montant), 0) as total_frais
            FROM frais_restaurant
            WHERE restaurant_id = %s AND date >= %s AND date < %s
        """, (restaurant_id, date_from, date_to))
        total_frais = frais['total_frais'] if frais else 0
        benefice_net = total_brut - montant_commission - total_frais
        return {
            'restaurant': restaurant,
            'total_brut': total_brut,
            'commission': commission,
            'montant_commission': montant_commission,
            'total_frais': total_frais,
            'benefice_net': benefice_net,
        }

    @staticmethod
    def financial_graph(restaurant_id, date_from, date_to, periode):
        graph_labels = []
        graph_values = []
        db_graph = db
        if periode in ['today', 'custom'] and isinstance(date_from, datetime) and isinstance(date_to, datetime) and (date_to - date_from).days < 31:
            query_graph = """
                SELECT DATE(co.cree_le) as jour, COALESCE(SUM(cr.quantite * r.prix), 0) as total
                FROM commandes co
                JOIN commande_repas cr ON cr.commande_id = co.id
                JOIN repas r ON r.id = cr.repas_id
                JOIN repas_restaurant rr ON rr.repas_id = r.id
                JOIN historique_statut_commande hsc ON hsc.commande_id = co.id
                WHERE rr.restaurant_id = %s
                AND hsc.statut_id = (
                    SELECT id FROM statut_commande WHERE appellation = 'Livrée' LIMIT 1
                )
                AND co.cree_le >= %s AND co.cree_le < %s
                GROUP BY DATE(co.cree_le)
                ORDER BY jour
            """
            rows = db_graph.fetch_query(query_graph, (restaurant_id, date_from, date_to))
            for row in rows:
                graph_labels.append(row['jour'].strftime('%d/%m'))
                graph_values.append(float(row['total']))
        else:
            query_graph = """
                SELECT TO_CHAR(DATE_TRUNC('month', co.cree_le), 'MM/YYYY') as mois, COALESCE(SUM(cr.quantite * r.prix), 0) as total
                FROM commandes co
                JOIN commande_repas cr ON cr.commande_id = co.id
                JOIN repas r ON r.id = cr.repas_id
                JOIN repas_restaurant rr ON rr.repas_id = r.id
                JOIN historique_statut_commande hsc ON hsc.commande_id = co.id
                WHERE rr.restaurant_id = %s
                AND hsc.statut_id = (
                    SELECT id FROM statut_commande WHERE appellation = 'Livrée' LIMIT 1
                )
                AND co.cree_le >= %s AND co.cree_le < %s
                GROUP BY DATE_TRUNC('month', co.cree_le)
                ORDER BY DATE_TRUNC('month', co.cree_le)
            """
            rows = db_graph.fetch_query(query_graph, (restaurant_id, date_from, date_to))
            for row in rows:
                graph_labels.append(row['mois'])
                graph_values.append(float(row['total']))
        return graph_labels, graph_values

