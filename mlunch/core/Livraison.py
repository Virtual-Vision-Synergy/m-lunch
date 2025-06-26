import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one
from database import db

class Livraison:
    """Classe représentant une livraison dans le système."""

    @staticmethod
    def create(livreur_id, commande_id, initial_statut_id):
        """Crée une nouvelle livraison avec son historique et statut initial."""
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "ID livreur invalide"}
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "ID commande invalide"}
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "ID statut invalide"}

        # Démarrer une transaction
        try:
            # Insérer la livraison
            query_livraison = """
                INSERT INTO livraisons (livreur_id, commande_id)
                VALUES (%s, %s)
                RETURNING id, livreur_id, commande_id, attribue_le
            """
            result_livraison, error = fetch_one(query_livraison, (livreur_id, commande_id))
            if error:
                if isinstance(error, psycopg2.errors.ForeignKeyViolation):
                    return {"error": "Livreur ou commande non trouvé"}
                return {"error": f"Erreur lors de la création de la livraison : {str(error)}"}
            if not result_livraison:
                return {"error": "Échec de la création de la livraison"}

            livraison_id = result_livraison['id']

            # Vérifier si le statut existe
            query_statut = """
                SELECT id FROM statut_livraison WHERE id = %s
            """
            result_statut, error = fetch_one(query_statut, (initial_statut_id,))
            if error or not result_statut:
                return {"error": "Statut non trouvé"}

            # Insérer dans l'historique
            query_historique = """
                INSERT INTO historique_statut_livraison (livraison_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, livraison_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (livraison_id, initial_statut_id))
            if error:
                return {"error": f"Erreur lors de la création de l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de la création de l'historique"}

            # Retourner les informations complètes
            return {
                "livraison": dict(result_livraison),
                "historique": dict(result_historique)
            }

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
            
    @staticmethod
    def get_by_id(livraison_id):
        """Récupère une livraison par son ID, incluant son historique de statuts."""
        if not isinstance(livraison_id, int) or livraison_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT l.id, l.livreur_id, l.commande_id, l.attribue_le,
                h.statut_id, h.mis_a_jour_le
            FROM livraisons l
            LEFT JOIN historique_statut_livraison h ON l.id = h.livraison_id
            WHERE l.id = %s
            ORDER BY h.mis_a_jour_le DESC
        """
        try:
            results, error = fetch_query(query, (livraison_id,), as_dict=True)
            if error:
                return {"error": f"Erreur lors de la récupération : {str(error)}"}
            if not results:
                return {"message": "Aucune livraison trouvée"}
            return {"data": results}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def get_all():
            """Récupère toutes les livraisons."""
            query = """
                SELECT id, livreur_id, commande_id, attribue_le
                FROM livraisons
                ORDER BY attribue_le DESC
            """
            results, error = fetch_query(query)
            if error:
                return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
            return [dict(row) for row in results]

    @staticmethod
    def update(livreur_id, statut_id):
        """Met à jour le statut d'un livreur. Retourne les données mises à jour ou None si non trouvé."""
        if not isinstance(livreur_id, int) or livreur_id <= 0 or not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "ID invalide"}

        query = """
            INSERT INTO historique_statut_livraison (livraison_id, statut_id)
            VALUES (%s, %s)
            RETURNING id, livraison_id, statut_id, mis_a_jour_le
        """
        result, error = fetch_one(query, (livreur_id, statut_id))
        if error:
            return {"error": str(error)}
        return result if result else None

    @staticmethod
    def delete(livraison_id):
        """Marque une livraison comme annulée en mettant à jour son statut. Retourne les données mises à jour ou None si non trouvé."""
        if not isinstance(livraison_id, int) or livraison_id <= 0:
            return {"error": "ID invalide"}

        statut_id = 3  # Statut "Annulé"
        query = """
            INSERT INTO historique_statut_livraison (livraison_id, statut_id)
            VALUES (%s, %s)
            RETURNING id, livraison_id, statut_id, mis_a_jour_le
        """
        result, error = fetch_one(query, (livraison_id, statut_id))
        if error:
            return {"error": str(error)}
        return result if result else None

    @staticmethod
    def list(secteur=None, statut=None, adresse=None, livreur_id=None):
        """Récupère la liste des livraisons avec filtres."""
        params = []
        query = """
            SELECT l.id, l.livreur_id, l.commande_id, l.attribue_le,
                   lr.nom as livreur_nom,
                   r.nom as restaurant_nom,
                   c.id as commande_id,
                   z.nom as secteur,
                   sl.appellation as statut,
                   SUM(cr.quantite * rp.prix) as total_commande
            FROM livraisons l
            JOIN livreurs lr ON l.livreur_id = lr.id
            JOIN commandes c ON l.commande_id = c.id
            JOIN commande_repas cr ON c.id = cr.commande_id
            JOIN repas rp ON cr.repas_id = rp.id
            JOIN repas_restaurant rr ON rp.id = rr.repas_id
            JOIN restaurants r ON rr.restaurant_id = r.id
            JOIN zones_restaurant zr ON r.id = zr.restaurant_id
            JOIN zones z ON zr.zone_id = z.id
            JOIN (
                SELECT hsl.livraison_id, sl.appellation
                FROM historique_statut_livraison hsl
                JOIN statut_livraison sl ON hsl.statut_id = sl.id
                WHERE hsl.id = (
                    SELECT id FROM historique_statut_livraison
                    WHERE livraison_id = hsl.livraison_id
                    ORDER BY mis_a_jour_le DESC, id DESC
                    LIMIT 1
                )
            ) sl ON sl.livraison_id = l.id
            WHERE 1=1
        """
        
        if secteur:
            query += " AND z.nom = %s"
            params.append(secteur)
            
        if statut:
            query += " AND sl.appellation = %s"
            params.append(statut)
            
        if adresse and False:  # Désactivé car cette colonne n'existe pas
            query += " AND c.adresse_livraison ILIKE %s"
            params.append(f"%{adresse}%")
            
        if livreur_id:
            query += " AND l.livreur_id = %s"
            params.append(livreur_id)
            
        query += " GROUP BY l.id, l.livreur_id, l.commande_id, l.attribue_le, lr.nom, r.nom, c.id, z.nom, sl.appellation ORDER BY l.attribue_le DESC"
        
        return db.fetch_query(query, params)
    
    @staticmethod
    def detail(livraison_id):
        """Récupère les détails d'une livraison."""
        query = """
            SELECT l.id, l.livreur_id, l.commande_id, l.attribue_le,
                   lr.nom as livreur_nom,
                   r.nom as restaurant_nom,
                   c.id as commande_id,
                   z.nom as secteur,
                   sl.appellation as statut,
                   SUM(cr.quantite * rp.prix) as total_commande
            FROM livraisons l
            JOIN livreurs lr ON l.livreur_id = lr.id
            JOIN commandes c ON l.commande_id = c.id
            JOIN commande_repas cr ON c.id = cr.commande_id
            JOIN repas rp ON cr.repas_id = rp.id
            JOIN repas_restaurant rr ON rp.id = rr.repas_id
            JOIN restaurants r ON rr.restaurant_id = r.id
            JOIN zones_restaurant zr ON r.id = zr.restaurant_id
            JOIN zones z ON zr.zone_id = z.id
            JOIN (
                SELECT hsl.livraison_id, sl.appellation
                FROM historique_statut_livraison hsl
                JOIN statut_livraison sl ON hsl.statut_id = sl.id
                WHERE hsl.id = (
                    SELECT id FROM historique_statut_livraison
                    WHERE livraison_id = hsl.livraison_id
                    ORDER BY mis_a_jour_le DESC, id DESC
                    LIMIT 1
                )
            ) sl ON sl.livraison_id = l.id
            WHERE l.id = %s
            GROUP BY l.id, l.livreur_id, l.commande_id, l.attribue_le, lr.nom, r.nom, c.id, z.nom, sl.appellation
        """
        
        return db.fetch_one(query, (livraison_id,))
    
    @staticmethod
    def update_status(livraison_id, statut_id):
        """Met à jour le statut d'une livraison."""
        query = """
            INSERT INTO historique_statut_livraison (livraison_id, statut_id, mis_a_jour_le)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
        """
        db.execute_query(query, (livraison_id, statut_id))
        return True
    
    @staticmethod
    def update_livreur(livraison_id, livreur_id):
        """Met à jour le livreur assigné à une livraison."""
        query = """
            UPDATE livraisons
            SET livreur_id = %s
            WHERE id = %s
        """
        db.execute_query(query, (livreur_id, livraison_id))
        return True
