import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Commande:
    """Classe représentant une commande dans le système."""

    @staticmethod
    def create(client_id, initial_statut_id):
        """Crée une nouvelle commande avec son historique et statut initial."""
        if not isinstance(client_id, int) or client_id <= 0:
            return {"error": "ID client invalide"}
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "ID statut invalide"}

        # Démarrer une transaction
        try:
            # Insérer la commande
            query_commande = """
                INSERT INTO commandes (client_id)
                VALUES (%s)
                RETURNING id, client_id, cree_le
            """
            result_commande, error = fetch_one(query_commande, (client_id,))
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
        """Récupère une commande par son ID."""
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT c.id, c.client_id, c.cree_le,h.statut_id,mis_a_jour_le
            FROM commandes c JOIN historique_statut_commande h 
            on c.id = h.commande_id
            WHERE c.id = %s
        """
        result, error = fetch_one(query, (commande_id,))
        if error:
            return {"error": f"Erreur lors de la récupération : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def get_all():
        """Récupère toutes les commandes."""
        query = """
            SELECT c.id, c.client_id, c.cree_le
            FROM commandes c JOIN historique_statut_commande h
             on c.id = h.commande_id
            ORDER BY cree_le DESC
        """
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    # def add_repas(commande_id: int, repas_id: int, quantite: int) -> Dict[str, Any]:
    #     """Ajoute un repas à une commande."""
    #     if not isinstance(commande_id, int) or commande_id <= 0:
    #         return {"error": "ID commande invalide"}
    #     if not isinstance(repas_id, int) or repas_id <= 0:
    #         return {"error": "ID repas invalide"}
    #     if not isinstance(quantite, int) or quantite <= 0:
    #         return {"error": "Quantité invalide"}

    #     query = """
    #         INSERT INTO commande_repas (commande_id, repas_id, quantite)
    #         VALUES (%s, %s, %s)
    #         RETURNING id, commande_id, repas_id, quantite, ajoute_le
    #     """
    #     result, error = fetch_one(query, (commande_id, repas_id, quantite))
    #     if error:
    #         if isinstance(error, psycopg2.errors.ForeignKeyViolation):
    #             return {"error": "Commande ou repas non trouvé"}
    #         return {"error": f"Erreur lors de l'ajout du repas : {str(error)}"}
    #     if not result:
    #         return {"error": "Échec de l'ajout du repas"}
    #     return dict(result)

    
    @staticmethod
    def update(commande_id,statut_id):
        """Met à jour un Commane. Retourne les données mises à jour ou None si non trouvé."""
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
