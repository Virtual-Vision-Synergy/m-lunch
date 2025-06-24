import psycopg2.errors
from typing import Optional, Dict, List, Any, Tuple
from database.db import execute_query, fetch_query, fetch_one
from database import db
from datetime import datetime, timedelta

class Restaurant:
    """Classe représentant un restaurant dans le système."""

    @staticmethod
    def create(nom: str, horaire_debut: Optional[str] = None, horaire_fin: Optional[str] = None, 
               adresse: Optional[str] = None, image: Optional[str] = None, 
               geo_position: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
        """Crée un nouveau restaurant."""
        if not nom:
            return {"error": "Le nom est requis"}

        position_wkt = f'POINT({geo_position[0]} {geo_position[1]})' if geo_position else None
        query = """
            INSERT INTO restaurants (nom, horaire_debut, horaire_fin, adresse, image, geo_position)
            VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
            RETURNING id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
        """
        result, error = fetch_one(query, (nom, horaire_debut, horaire_fin, adresse, image, position_wkt))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": f"Le nom {nom} est déjà utilisé"}
            return {"error": f"Erreur lors de la création : {str(error)}"}
        if not result:
            return {"error": "Échec de la création du restaurant"}
        return dict(result)

    @staticmethod
    def get_by_id(restaurant_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un restaurant par son ID."""
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
            FROM restaurants
            WHERE id = %s
        """
        result, error = fetch_one(query, (restaurant_id,))
        if error:
            return {"error": f"Erreur lors de la récupération : {str(error)}"}
        return dict(result) if result else None

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
    def update(restaurant_id: int, nom: Optional[str] = None, horaire_debut: Optional[str] = None, 
               horaire_fin: Optional[str] = None, adresse: Optional[str] = None, 
               image: Optional[str] = None, geo_position: Optional[Tuple[float, float]] = None) -> Optional[Dict[str, Any]]:
        """Met à jour un restaurant."""
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "ID invalide"}

        position_wkt = f'POINT({geo_position[0]} {geo_position[1]})' if geo_position else None
        query = """
            UPDATE restaurants
            SET nom = COALESCE(%s, nom),
                horaire_debut = COALESCE(%s, horaire_debut),
                horaire_fin = COALESCE(%s, horaire_fin),
                adresse = COALESCE(%s, adresse),
                image = COALESCE(%s, image),
                geo_position = COALESCE(ST_GeomFromText(%s, 4326), geo_position)
            WHERE id = %s
            RETURNING id, nom, horaire_debut, horaire_fin, adresse, image, ST_AsText(geo_position) as geo_position
        """
        result, error = fetch_one(query, (nom, horaire_debut, horaire_fin, adresse, image, position_wkt, restaurant_id))
        if error:
            if isinstance(error, psycopg2.errors.UniqueViolation):
                return {"error": f"Le nom {nom} est déjà utilisé"}
            return {"error": f"Erreur lors de la mise à jour : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def delete(restaurant_id: int) -> Dict[str, Any]:
        """Supprime un restaurant."""
        if not isinstance(restaurant_id, int) or restaurant_id <= 0:
            return {"error": "ID invalide"}

        query = """
            DELETE FROM restaurants
            WHERE id = %s
            RETURNING id
        """
        result, error = fetch_one(query, (restaurant_id,))
        if error:
            return {"error": f"Erreur lors de la suppression : {str(error)}"}
        return {"success": bool(result), "id": restaurant_id}

    @staticmethod
    def list(secteur=None, horaire=None):
        params = []
        base_query = """
            SELECT r.*,
                   c.valeur as commission,
                   z.nom as secteur,
                   s.appellation as statut
            FROM restaurants r
            LEFT JOIN commissions c ON c.restaurant_id = r.id
            LEFT JOIN zones_restaurant zr ON zr.restaurant_id = r.id
            LEFT JOIN zones z ON z.id = zr.zone_id
            LEFT JOIN (
                SELECT hsr.restaurant_id, sr.appellation
                FROM historique_statut_restaurant hsr
                JOIN statut_restaurant sr ON hsr.statut_id = sr.id
                WHERE hsr.id = (
                    SELECT id FROM historique_statut_restaurant
                    WHERE restaurant_id = hsr.restaurant_id
                    ORDER BY mis_a_jour_le DESC, id DESC
                    LIMIT 1
                )
            ) s ON s.restaurant_id = r.id
            WHERE (s.appellation IS NULL OR s.appellation != 'Fermé')
        """
        if secteur:
            base_query += " AND z.nom = %s"
            params.append(secteur)
        if horaire:
            base_query += " AND r.horaire_debut <= %s AND r.horaire_fin >= %s"
            params.extend([horaire, horaire])
        base_query += " GROUP BY r.id, c.valeur, z.nom, s.appellation ORDER BY r.id"
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
        return last_statut and last_statut['appellation'] == 'Fermé'

    @staticmethod
    def close(restaurant_id):
        last_statut = db.fetch_one("""
            SELECT s.appellation
            FROM historique_statut_restaurant hsr
            JOIN statut_restaurant s ON hsr.statut_id = s.id
            WHERE hsr.restaurant_id = %s
            ORDER BY hsr.mis_a_jour_le DESC, hsr.id DESC
            LIMIT 1
        """, (restaurant_id,))
        if last_statut and last_statut['appellation'] == 'Fermé':
            return False
        statut_ferme = db.fetch_one("SELECT id FROM statut_restaurant WHERE appellation='Fermé'")
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