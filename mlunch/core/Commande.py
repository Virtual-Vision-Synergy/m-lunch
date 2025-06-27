import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Commande:
    """Classe représentant une commande dans le système."""

    @staticmethod
    def CreateCommande(client_id, point_recup_id, initial_statut_id):
        """Crée une nouvelle commande avec son historique et statut initial. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(client_id, int) or client_id <= 0:
            return {"error": "L'ID du client doit être un entier positif"}
        if not isinstance(point_recup_id, int) or point_recup_id <= 0:
            return {"error": "L'ID du point de récupération doit être un entier positif"}
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "L'ID du statut doit être un entier positif"}

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
                    return {"error": "Client ou point de récupération non trouvé"}
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

            return {
                "commande": dict(result_commande),
                "historique": dict(result_historique)
            }

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetCommandeFromId(commande_id):
        """Récupère une commande par son ID avec son historique de statuts. Retourne un dictionnaire ou une erreur."""
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "L'ID de la commande doit être un entier positif"}

        query = """
            SELECT c.id, c.client_id, c.point_recup_id, c.cree_le, h.statut_id, h.mis_a_jour_le, s.appellation
            FROM commandes c
            JOIN historique_statut_commande h ON c.id = h.commande_id
            JOIN statut_commande s ON h.statut_id = s.id
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
    def GetAllCommandes():
        """Récupère toutes les commandes. Retourne une liste de dictionnaires ou une erreur."""
        query = """
            SELECT id, client_id, point_recup_id, cree_le
            FROM commandes 
            ORDER BY cree_le DESC
        """
        results, error = fetch_query(query)
        if error:
            return {"error": f"Erreur lors de la récupération : {str(error)}"}
        if not results:
            return {"error": "Aucune commande trouvée"}
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
    def UpdateCommande(commande_id, statut_id):
        """Met à jour le statut d'une commande en ajoutant une entrée dans l'historique. Retourne les données ou une erreur."""
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "L'ID de la commande doit être un entier positif"}
        if not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "L'ID du statut doit être un entier positif"}

        try:
            # Vérifier si la commande existe
            query_commande = """
                SELECT id FROM commandes WHERE id = %s
            """
            result_commande, error = fetch_one(query_commande, (commande_id,))
            if error or not result_commande:
                return {"error": "Commande non trouvée"}

            # Vérifier si le statut existe
            query_statut = """
                SELECT id FROM statut_commande WHERE id = %s
            """
            result_statut, error = fetch_one(query_statut, (statut_id,))
            if error or not result_statut:
                return {"error": "Statut non trouvé"}

            # Insérer dans l'historique
            query_historique = """
                INSERT INTO historique_statut_commande (commande_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, commande_id, statut_id, mis_a_jour_le
            """
            result, error = fetch_one(query_historique, (commande_id, statut_id))
            if error:
                return {"error": f"Erreur lors de la mise à jour du statut : {str(error)}"}
            if not result:
                return {"error": "Échec de la mise à jour du statut"}
            
            return dict(result)
        
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
    
    @staticmethod
    def DeleteCommande(commande_id, statut_id):
        """Marque une commande comme supprimée en ajoutant un statut dans l'historique. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "L'ID de la commande doit être un entier positif"}
        if not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "L'ID du statut doit être un entier positif"}

        try:
            # Vérifier si la commande existe
            query_commande = """
                SELECT id FROM commandes WHERE id = %s
            """
            result_commande, error = fetch_one(query_commande, (commande_id,))
            if error or not result_commande:
                return {"error": "Commande non trouvée"}

            # Vérifier si le statut existe
            query_statut = """
                SELECT id FROM statut_commande WHERE id = %s
            """
            result_statut, error = fetch_one(query_statut, (statut_id,))
            if error or not result_statut:
                return {"error": "Statut non trouvé"}

            # Insérer dans l'historique pour marquer la suppression
            query_historique = """
                INSERT INTO historique_statut_commande (commande_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, commande_id, statut_id, mis_a_jour_le
            """
            result, error = fetch_one(query_historique, (commande_id, statut_id))
            if error:
                return {"error": f"Erreur lors de l'ajout du statut : {str(error)}"}
            if not result:
                return {"error": "Échec de l'ajout du statut"}
            
            return dict(result)
        
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

