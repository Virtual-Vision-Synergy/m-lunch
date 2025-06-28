import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Livraison:
    """Classe représentant une livraison dans le système."""

    @staticmethod
    def CreateLivraison(livreur_id, commande_id):
        """Crée une nouvelle livraison avec un statut initial 'Attribué' (statut_id=1). Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "L'ID du livreur doit être un entier positif"}
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "L'ID de la commande doit être un entier positif"}

        statut_id = 1  # Statut "Attribué"
        try:
            # Vérifier si le livreur existe
            query_check_livreur = """
                SELECT id FROM livreurs WHERE id = %s
            """
            result_check_livreur, error = fetch_one(query_check_livreur, (livreur_id,))
            if error or not result_check_livreur:
                return {"error": "Livreur non trouvé"}

            # Vérifier si la commande existe
            query_check_commande = """
                SELECT id FROM commandes WHERE id = %s
            """
            result_check_commande, error = fetch_one(query_check_commande, (commande_id,))
            if error or not result_check_commande:
                return {"error": "Commande non trouvée"}

            # Vérifier si le statut existe
            query_check_statut = """
                SELECT id FROM statut_livraison WHERE id = %s
            """
            result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
            if error or not result_check_statut:
                return {"error": "Statut 'Attribué' non trouvé"}

            # Insérer dans livraisons
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

            # Insérer dans historique_statut_livraison
            query_historique = """
                INSERT INTO historique_statut_livraison (livraison_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, livraison_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (result_livraison['id'], statut_id))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de l'enregistrement dans l'historique"}

            return {"livraison": dict(result_livraison), "historique": dict(result_historique)}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetLivraisonFromId(livraison_id):
        """Récupère une livraison par son ID avec son historique de statuts. Retourne un dictionnaire ou une erreur."""
        if not isinstance(livraison_id, int) or livraison_id <= 0:
            return {"error": "L'ID de la livraison doit être un entier positif"}

        query = """
            SELECT 
                l.id AS livraison_id, l.livreur_id, l.commande_id, l.attribue_le,
                h.id AS historique_id, h.statut_id, h.mis_a_jour_le,
                s.appellation AS statut_appellation
            FROM livraisons l
            LEFT JOIN historique_statut_livraison h ON l.id = h.livraison_id
            LEFT JOIN statut_livraison s ON h.statut_id = s.id
            WHERE l.id = %s
            ORDER BY h.mis_a_jour_le DESC
        """
        try:
            rows, error = fetch_query(query, (livraison_id,), as_dict=True)
            if error:
                return {"error": f"Erreur lors de la récupération : {str(error)}"}
            if not rows:
                return {"error": "Aucune livraison trouvée"}
            return {"data": rows}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
    @staticmethod
    def GetAllLivraisons():
        """Récupère toutes les livraisons. Retourne une liste de dictionnaires ou une erreur."""
        query = """
            SELECT id, livreur_id, commande_id, attribue_le
            FROM livraisons
            ORDER BY attribue_le DESC
        """
        try:
            results, error = fetch_query(query)
            if error:
                return {"error": f"Erreur lors de la récupération : {str(error)}"}
            if not results:
                return {"error": "Aucune livraison trouvée"}
            return [dict(row) for row in results]
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def UpdateLivraison(livraison_id, statut_id, livreur_id=None, commande_id=None):
        """Met à jour une livraison et son historique de statut. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(livraison_id, int) or livraison_id <= 0:
            return {"error": "L'ID de la livraison doit être un entier positif"}
        if not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "L'ID du statut doit être un entier positif"}
        if livreur_id is not None and (not isinstance(livreur_id, int) or livreur_id <= 0):
            return {"error": "L'ID du livreur doit être un entier positif"}
        if commande_id is not None and (not isinstance(commande_id, int) or commande_id <= 0):
            return {"error": "L'ID de la commande doit être un entier positif"}

        try:
            # Vérifier si la livraison existe
            query_check_livraison = """
                SELECT id FROM livraisons WHERE id = %s
            """
            result_check_livraison, error = fetch_one(query_check_livraison, (livraison_id,))
            if error or not result_check_livraison:
                return {"error": "Livraison non trouvée"}

            # Vérifier si le statut existe
            query_check_statut = """
                SELECT id FROM statut_livraison WHERE id = %s
            """
            result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
            if error or not result_check_statut:
                return {"error": "Statut non trouvé"}

            # Vérifier si le livreur existe (si fourni)
            if livreur_id is not None:
                query_check_livreur = """
                    SELECT id FROM livreurs WHERE id = %s
                """
                result_check_livreur, error = fetch_one(query_check_livreur, (livreur_id,))
                if error or not result_check_livreur:
                    return {"error": "Livreur non trouvé"}

            # Vérifier si la commande existe (si fournie)
            if commande_id is not None:
                query_check_commande = """
                    SELECT id FROM commandes WHERE id = %s
                """
                result_check_commande, error = fetch_one(query_check_commande, (commande_id,))
                if error or not result_check_commande:
                    return {"error": "Commande non trouvée"}

            # Mettre à jour la table livraisons
            query_update_livraison = """
                UPDATE livraisons
                SET livreur_id = COALESCE(%s, livreur_id),
                    commande_id = COALESCE(%s, commande_id)
                WHERE id = %s
                RETURNING id, livreur_id, commande_id, attribue_le
            """
            result_livraison, error = fetch_one(query_update_livraison, (livreur_id, commande_id, livraison_id))
            if error:
                if isinstance(error, psycopg2.errors.ForeignKeyViolation):
                    return {"error": "Livreur ou commande non trouvé"}
                return {"error": f"Erreur lors de la mise à jour de la livraison : {str(error)}"}
            if not result_livraison:
                return {"error": "Échec de la mise à jour de la livraison"}

            # Insérer dans historique_statut_livraison
            query_historique = """
                INSERT INTO historique_statut_livraison (livraison_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, livraison_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (livraison_id, statut_id))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de l'enregistrement dans l'historique"}

            return {"livraison": dict(result_livraison), "historique": dict(result_historique)}
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def DeleteLivraison(livraison_id,statut_id):
        """Marque une livraison comme annulée (statut_id=2) dans l'historique. Retourne un dictionnaire avec les données ou une erreur."""
        if not isinstance(livraison_id, int) or livraison_id <= 0:
            return {"error": "L'ID de la livraison doit être un entier positif"}
        if not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "L'ID du statut  être un entier positif"}

        try:
            # Vérifier si la livraison existe
            query_check_livraison = """
                SELECT id FROM livraisons WHERE id = %s
            """
            result_check_livraison, error = fetch_one(query_check_livraison, (livraison_id,))
            if error or not result_check_livraison:
                return {"error": "Livraison non trouvée"}

            # Vérifier si le statut "Annulé" existe
            query_check_statut = """
                SELECT id FROM statut_livraison WHERE id = %s
            """
            result_check_statut, error = fetch_one(query_check_statut, (statut_id,))
            if error or not result_check_statut:
                return {"error": "Statut 'Annulé' non trouvé"}

            # Insérer dans historique_statut_livraison
            query_historique = """
                INSERT INTO historique_statut_livraison (livraison_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, livraison_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (livraison_id, statut_id))
            if error:
                return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de l'enregistrement dans l'historique"}

            return dict(result_historique)
        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}