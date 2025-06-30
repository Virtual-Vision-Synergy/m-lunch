import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Commande:
    """Classe représentant une commande dans le système."""

    @staticmethod
    def create(client_id, point_recup_id, initial_statut_id):
        """Crée une nouvelle commande avec son historique et statut initial."""
        if not isinstance(client_id, int) or client_id <= 0:
            return {"error": "ID client invalide"}
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "ID statut invalide"}

        # Démarrer une transaction
        try:
            # Insérer la commande
            query_commande = """
                INSERT INTO commandes (client_id, point_recup_id)
                VALUES (%s, %s)
                RETURNING id, client_id, point_recup_id, cree_le
            """
            result_commande, error = fetch_one(query_commande, (client_id, point_recup_id))
            if error:
                if isinstance(error, psycopg2.errors.ForeignKeyViolation):
                    return {"error": "Client non trouvé"}
                return {"error": f"Erreur lors de la création de la commande : {str(error)}"}
            if not result_commande:
                return {"error": "Échec de la création de la commande"}

            commande_id = result_commande['id']

            # Vérifier si le statut existe
            query_statut = """
                SELECT id FROM statut_commande WHERE id = %s
            """
            result_statut, error = fetch_one(query_statut, (initial_statut_id,))
            if error or not result_statut:
                return {"error": "Statut non trouvé"}

            # Insérer dans l'historique
            query_historique = """
                INSERT INTO historique_statut_commande (commande_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, commande_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (commande_id, initial_statut_id))
            if error:
                return {"error": f"Erreur lors de la création de l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de la création de l'historique"}

            # Retourner les informations complètes
            return {
                "commande": dict(result_commande),
                "historique": dict(result_historique)
            }

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def get_by_id(commande_id):
        """
        Récupère toutes les lignes d'une commande par son ID, incluant l'historique des statuts.
        
        Args:
            commande_id (int): L'ID de la commande à récupérer.
        
        Returns:
            dict: Dictionnaire avec une clé 'data' contenant une liste de dictionnaires (chaque dictionnaire représente une ligne).
                En cas d'erreur ou si aucune commande n'est trouvée, retourne un dictionnaire avec une clé 'error'.
        """
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT c.id, c.client_id, c.cree_le, h.statut_id, h.mis_a_jour_le
            FROM commandes c
            JOIN historique_statut_commande h ON c.id = h.commande_id
            WHERE c.id = %s
            ORDER BY h.mis_a_jour_le DESC
        """
        try:
            rows, error = fetch_query(query, (commande_id,), as_dict=True)
            if error:
                return {"error": f"Erreur lors de la récupération : {str(error)}"}
            if not rows:
                return {"error": "Aucune commande trouvée"}
            return {"data": rows}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def get_all():
        """Récupère toutes les commandes."""
        query = """
            SELECT id, client_id, cree_le
            FROM commandes 
            ORDER BY cree_le DESC
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    def get_commande_en_cours(user_id):
        query = """
            SELECT id FROM commandes
            WHERE client_id = %s
            ORDER BY cree_le DESC
            LIMIT 1
        """
        result = fetch_one(query, (user_id,))
        return result['id'] if result else None

    @staticmethod
    def choisir_livreur(zone_id):
        query = """
            SELECT livreur_id FROM zones_livreurs
            WHERE zone_id = %s
            ORDER BY mis_a_jour_le DESC
            LIMIT 1
        """
        result = fetch_one(query, (zone_id,))
        return result['livreur_id'] if result else None

    @staticmethod
    def vider_panier(commande_id):
        query = "DELETE FROM commande_repas WHERE commande_id = %s"
        execute_query(query, (commande_id,))

    @staticmethod
    def update(commande_id, statut_id):
        """Met à jour un Commane. Retourne les données mises à jour ou None si non trouvé."""
        if not commande_id or statut_id <= 0:
            return {"error": "ID invalide"}

        query = """
            INSERT INTO historique_statut_commande (commande_id, statut_id)
            VALUES (%s, %s)
            RETURNING id, commande_id, statut_id
        """
        result, error = fetch_one(query, (commande_id, statut_id))
        if error:
            return {"error": str(error)}
        return result if result else None
    
    @staticmethod
    def delete(commande_id, statut_id):
        """Met à jour un Commande Retourne les données mises à jour ou None si non trouvé."""
        if not commande_id or statut_id <= 0:
            return {"error": "ID invalide"}

        query = """
            insert into historique_statut_commande (commande_id,statut_id)
            values(%s,%s) 
            RETURNING id, commande_id, statut_id
        """
        result, error = fetch_one(query, (commande_id,statut_id))
        if error:
            return {"error": str(error)}
        return result if result else None