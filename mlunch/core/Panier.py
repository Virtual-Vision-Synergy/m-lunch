import psycopg2.errors
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime

class Panier:
    
    @staticmethod
    def get_panier_items( client_id):
        """
        Récupérer les articles du panier pour un utilisateur
        """
        try:
            if client_id:
                # Pour utilisateurs connectés - récupérer les commandes en cours
                query = """
                    SELECT 
                        cr.id as item_id,
                        cr.commande_id,
                        r.id as repas_id,
                        r.nom as nom_plat,
                        r.image,
                        r.prix as prix_unitaire,
                        cr.quantite,
                        (r.prix * cr.quantite) as prix_total,
                        rest.nom as restaurant_nom
                    FROM commande_repas cr
                    JOIN repas r ON cr.repas_id = r.id
                    JOIN commandes c ON cr.commande_id = c.id
                    LEFT JOIN repas_restaurant rr ON r.id = rr.repas_id
                    LEFT JOIN restaurants rest ON rr.restaurant_id = rest.id
                    WHERE c.client_id = %s 
                    AND c.id NOT IN (
                        SELECT DISTINCT commande_id 
                        FROM historique_statut_commande 
                        WHERE statut_id IN (SELECT id FROM statut_commande WHERE appellation IN ('validée', 'payée', 'livrée'))
                    )
                    ORDER BY cr.ajoute_le DESC
                """
                return fetch_query(query, (client_id,))
                
        except psycopg2.errors.Error as e:
            print(f"Erreur lors de la récupération du panier: {e}")
            return []
    
    @staticmethod
    def add_to_panier(client_id, repas_id, quantite=1):
        """
        Ajouter un article au panier
        """
        try:
            # Vérifier si une commande en cours existe pour ce client
            commande_query = """
                SELECT id FROM commandes 
                WHERE client_id = %s 
                AND id NOT IN (
                    SELECT DISTINCT commande_id 
                    FROM historique_statut_commande 
                    WHERE statut_id IN (SELECT id FROM statut_commande WHERE appellation IN ('validée', 'payée', 'livrée'))
                )
                ORDER BY cree_le DESC 
                LIMIT 1
            """
            commande = fetch_one(commande_query, (client_id,))
            
            if not commande:
                # Créer une nouvelle commande
                create_commande_query = """
                    INSERT INTO commandes (client_id, cree_le) 
                    VALUES (%s, %s) 
                    RETURNING id
                """
                commande_id = execute_query(create_commande_query, (client_id, datetime.now()), return_id=True)
            else:
                commande_id = commande['id']
            
            # Vérifier si le repas existe déjà dans la commande
            existing_item_query = """
                SELECT id, quantite FROM commande_repas 
                WHERE commande_id = %s AND repas_id = %s
            """
            existing_item = fetch_one(existing_item_query, (commande_id, repas_id))
            
            if existing_item:
                # Mettre à jour la quantité
                update_query = """
                    UPDATE commande_repas 
                    SET quantite = quantite + %s 
                    WHERE id = %s
                """
                execute_query(update_query, (quantite, existing_item['id']))
            else:
                # Ajouter nouveau repas
                insert_query = """
                    INSERT INTO commande_repas (commande_id, repas_id, quantite) 
                    VALUES (%s, %s, %s)
                """
                execute_query(insert_query, (commande_id, repas_id, quantite))
            
            return True
            
        except psycopg2.errors.Error as e:
            print(f"Erreur lors de l'ajout au panier: {e}")
            return False
    
    @staticmethod
    def update_quantity(item_id, nouvelle_quantite):
        """
        Mettre à jour la quantité d'un article dans le panier
        """
        try:
            if nouvelle_quantite <= 0:
                return Panier.remove_from_panier(item_id)
            
            query = """
                UPDATE commande_repas 
                SET quantite = %s 
                WHERE id = %s
            """
            execute_query(query, (nouvelle_quantite, item_id))
            return True
            
        except psycopg2.errors.Error as e:
            print(f"Erreur lors de la mise à jour de la quantité: {e}")
            return False
    
    @staticmethod
    def remove_from_panier(item_id):
        """
        Supprimer un article du panier
        """
        try:
            query = "DELETE FROM commande_repas WHERE id = %s"
            execute_query(query, (item_id,))
            return True
            
        except psycopg2.errors.Error as e:
            print(f"Erreur lors de la suppression: {e}")
            return False
    
    @staticmethod
    def clear_panier(client_id):
        """
        Vider complètement le panier
        """
        try:
            # Supprimer tous les repas de la commande en cours
            query = """
                DELETE FROM commande_repas 
                WHERE commande_id IN (
                    SELECT id FROM commandes 
                    WHERE client_id = %s 
                    AND id NOT IN (
                        SELECT DISTINCT commande_id 
                        FROM historique_statut_commande 
                        WHERE statut_id IN (SELECT id FROM statut_commande WHERE appellation IN ('validée', 'payée', 'livrée'))
                    )
                )
            """
            execute_query(query, (client_id,))
            return True
            
        except psycopg2.errors.Error as e:
            print(f"Erreur lors du vidage du panier: {e}")
            return False
    
    @staticmethod
    def calculate_totals(client_id):
        """
        Calculer les totaux du panier
        """
        try:
            query = """
                SELECT 
                    COALESCE(SUM(r.prix * cr.quantite), 0) as sous_total,
                    COUNT(cr.id) as nombre_articles,
                    COALESCE(SUM(cr.quantite), 0) as quantite_totale
                FROM commande_repas cr
                JOIN repas r ON cr.repas_id = r.id
                JOIN commandes c ON cr.commande_id = c.id
                WHERE c.client_id = %s 
                AND c.id NOT IN (
                    SELECT DISTINCT commande_id 
                    FROM historique_statut_commande 
                    WHERE statut_id IN (SELECT id FROM statut_commande WHERE appellation IN ('validée', 'payée', 'livrée'))
                )
            """
            result = fetch_one(query, (client_id,))
            
            if result:
                sous_total = result['sous_total']
                # Calculer frais de livraison (exemple: 500 si commande < 5000, sinon gratuit)
                frais_livraison = 500 if sous_total < 5000 and sous_total > 0 else 0
                total = sous_total + frais_livraison
                
                return {
                    'sous_total': sous_total,
                    'frais_livraison': frais_livraison,
                    'total': total,
                    'nombre_articles': result['nombre_articles'],
                    'quantite_totale': result['quantite_totale']
                }
            
            return {
                'sous_total': 0,
                'frais_livraison': 0,
                'total': 0,
                'nombre_articles': 0,
                'quantite_totale': 0
            }
            
        except psycopg2.errors.Error as e:
            print(f"Erreur lors du calcul des totaux: {e}")
            return None
    
    @staticmethod
    def get_points_recuperation():
        """
        Récupérer la liste des points de récupération
        """
        try:
            query = """
                SELECT 
                    id, 
                    nom,
                    ST_X(geo_position::geometry) as longitude,
                    ST_Y(geo_position::geometry) as latitude
                FROM point_de_recuperation
                ORDER BY nom
            """
            return fetch_query(query)
            
        except psycopg2.errors.Error as e:
            print(f"Erreur lors de la récupération des points: {e}")
            return []
    
    @staticmethod
    def validate_commande(client_id, point_recup_id, mode_paiement):
        """
        Valider la commande et créer l'historique de statut
        """
        try:
            # Récupérer la commande en cours
            commande_query = """
                SELECT id FROM commandes 
                WHERE client_id = %s 
                AND id NOT IN (
                    SELECT DISTINCT commande_id 
                    FROM historique_statut_commande 
                    WHERE statut_id IN (SELECT id FROM statut_commande WHERE appellation IN ('validée', 'payée', 'livrée'))
                )
                ORDER BY cree_le DESC 
                LIMIT 1
            """
            commande = fetch_one(commande_query, (client_id,))
            
            if not commande:
                return False, "Aucune commande en cours trouvée"
            
            commande_id = commande['id']
            
            # Mettre à jour le point de récupération
            update_commande_query = """
                UPDATE commandes 
                SET point_recup_id = %s 
                WHERE id = %s
            """
            execute_query(update_commande_query, (point_recup_id, commande_id))
            
            # Ajouter le statut "validée" à l'historique
            statut_query = "SELECT id FROM statut_commande WHERE appellation = 'validée'"
            statut = fetch_one(statut_query)
            
            if statut:
                historique_query = """
                    INSERT INTO historique_statut_commande (commande_id, statut_id) 
                    VALUES (%s, %s)
                """
                execute_query(historique_query, (commande_id, statut['id']))
            
            # Ici vous pourriez ajouter la logique de paiement selon le mode choisi
            # Pour l'instant, on considère que c'est validé
            
            return True, "Commande validée avec succès"
            
        except psycopg2.errors.Error as e:
            print(f"Erreur lors de la validation: {e}")
            return False, f"Erreur lors de la validation: {e}"
    
    @staticmethod
    def check_disponibilite_repas(repas_id):
        """
        Vérifier si un repas est disponible
        """
        try:
            query = """
                SELECT est_dispo 
                FROM disponibilite_repas 
                WHERE repas_id = %s 
                ORDER BY mis_a_jour_le DESC 
                LIMIT 1
            """
            result = fetch_one(query, (repas_id,))
            return result['est_dispo'] if result else True  # Par défaut disponible
            
        except psycopg2.errors.Error as e:
            print(f"Erreur lors de la vérification de disponibilité: {e}")
            return True
    
    @staticmethod
    def get_promotions_actives(repas_id):
        """
        Récupérer les promotions actives pour un repas
        """
        try:
            query = """
                SELECT pourcentage_reduction 
                FROM promotions 
                WHERE repas_id = %s 
                AND date_concerne = CURRENT_DATE
            """
            result = fetch_one(query, (repas_id,))
            return result['pourcentage_reduction'] if result else 0
            
        except psycopg2.errors.Error as e:
            print(f"Erreur lors de la récupération des promotions: {e}")
            return 0
