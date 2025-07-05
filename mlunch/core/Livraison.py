import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import fetch_one, execute_query
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
            results, error = db.fetch_query(query, (livraison_id,), as_dict=True)
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
            results, error = db.fetch_query(query)
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
    def list(secteur=None, statut=None, livreur_id=None):
        params = []
        query = "SELECT * FROM v_livraisons_list WHERE 1=1"
        if secteur:
            query += " AND secteur = %s"
            params.append(secteur)
        if statut:
            query += " AND statut = %s"
            params.append(statut)
        if livreur_id:
            query += " AND livreur_id = %s"
            params.append(livreur_id)
        return db.fetch_query(query, tuple(params))
    
    @staticmethod
    def detail(livraison_id):
        query = "SELECT * FROM v_livraisons_detail WHERE id = %s"
        return db.fetch_one(query, (livraison_id,))
    
    @staticmethod
    def update_status(livraison_id, statut_id):
        """Met à jour le statut d'une livraison."""
        try:
            # Vérification que les paramètres sont des entiers
            livraison_id = int(livraison_id)
            statut_id = int(statut_id)
            
            # Vérification de l'existence du statut
            statut = db.fetch_one("SELECT id, appellation FROM statut_livraison WHERE id = %s", (statut_id,))
            if not statut:
                print(f"Erreur: Le statut avec l'ID {statut_id} n'existe pas")
                return False
            
            # Vérification de l'existence de la livraison
            livraison = db.fetch_one("SELECT id FROM livraisons WHERE id = %s", (livraison_id,))
            if not livraison:
                print(f"Erreur: La livraison avec l'ID {livraison_id} n'existe pas")
                return False
            
            # Vérifier si le statut actuel est déjà celui qu'on veut mettre
            current_status = db.fetch_one("""
                SELECT sl.id, sl.appellation
                FROM historique_statut_livraison hsl
                JOIN statut_livraison sl ON hsl.statut_id = sl.id
                WHERE hsl.livraison_id = %s
                ORDER BY hsl.mis_a_jour_le DESC, hsl.id DESC
                LIMIT 1
            """, (livraison_id,))
            
            if current_status and current_status['id'] == statut_id:
                print(f"La livraison a déjà le statut {statut['appellation']}")
                return True  # On retourne True car c'est déjà le bon statut
            
            print(f"Mise à jour du statut: livraison_id={livraison_id}, statut_id={statut_id}, statut={statut['appellation']}")
            
            # Exécution de l'insertion avec une transaction explicite pour s'assurer qu'elle est bien exécutée
            db.execute_query("""
                BEGIN;
                INSERT INTO historique_statut_livraison (livraison_id, statut_id, mis_a_jour_le)
                VALUES (%s, %s, CURRENT_TIMESTAMP);
                COMMIT;
            """, (livraison_id, statut_id))
            
            # Vérification que l'insertion a bien été effectuée
            check_result = db.fetch_one("""
                SELECT COUNT(*) as count 
                FROM historique_statut_livraison 
                WHERE livraison_id = %s AND statut_id = %s
            """, (livraison_id, statut_id))
            
            if check_result and check_result['count'] > 0:
                print(f"Mise à jour réussie pour la livraison {livraison_id} avec le statut {statut['appellation']}")
                return True
            else:
                print(f"Échec de la mise à jour pour la livraison {livraison_id}")
                return False
    
        except Exception as e:
            print(f"Erreur lors de la mise à jour du statut: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
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

    @staticmethod
    def create(livreur_id, commande_id, statut_id):
        # Créer la livraison
        query = """
            INSERT INTO livraisons (livreur_id, commande_id)
            VALUES (%s, %s)
            RETURNING id
        """
        result, error = fetch_one(query, (livreur_id, commande_id))
        if error or not result:
            return {"error": str(error) if error else "Erreur lors de la création de la livraison"}
        livraison_id = result['id']
        # Historiser le statut
        query_statut = """
            INSERT INTO historique_statut_livraison (livraison_id, statut_id)
            VALUES (%s, %s)
        """
        execute_query(query_statut, (livraison_id, statut_id))
        return {"success": True, "livraison_id": livraison_id}
