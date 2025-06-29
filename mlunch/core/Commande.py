import psycopg2.errors
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime, timedelta

class Commande:
    
    @staticmethod
    def getCommandesEnCours(client_id):
        """
        Récupère toutes les commandes en cours pour un client donné
        """
        query = """
            SELECT 
                c.id,
                c.cree_le,
                r.nom AS restaurant_nom,
                pr.nom AS point_recup_nom,
                COUNT(cr.id) AS nb_articles,
                SUM(rep.prix * cr.quantite) AS total
            FROM commandes c
            JOIN point_de_recuperation pr ON c.point_recup_id = pr.id
            JOIN commande_repas cr ON c.id = cr.commande_id
            JOIN repas rep ON cr.repas_id = rep.id
            JOIN repas_restaurant rr ON rep.id = rr.repas_id
            JOIN restaurants r ON rr.restaurant_id = r.id
            WHERE c.client_id = %s
            GROUP BY c.id, c.cree_le, r.nom, pr.nom
            ORDER BY c.cree_le DESC
        """
        return fetch_query(query, [client_id])

    
    @staticmethod
    def getDetailCommande(commande_id, client_id):
        """
        Récupère les détails complets d'une commande spécifique
        """
        # Informations générales de la commande
        query_commande = """
            SELECT 
                c.id,
                c.cree_le,
                r.nom as restaurant_nom,
                r.adresse as restaurant_adresse,
                pr.nom as point_recup_nom,
                SUM(rep.prix * cr.quantite) as total
            FROM commandes c
            JOIN point_de_recuperation pr ON c.point_recup_id = pr.id
            JOIN commande_repas cr ON c.id = cr.commande_id
            JOIN repas rep ON cr.repas_id = rep.id
            JOIN restaurants r ON rep.restaurant_id = r.id
            WHERE c.id = %s AND c.client_id = %s
            GROUP BY c.id, c.cree_le, r.nom, r.adresse, pr.nom
        """
        
        commande_info = fetch_one(query_commande, [commande_id, client_id])
        
        if not commande_info:
            return None
        
        # Détails des repas commandés
        query_repas = """
            SELECT 
                rep.nom,
                rep.prix,
                cr.quantite,
                (rep.prix * cr.quantite) as sous_total
            FROM commande_repas cr
            JOIN repas rep ON cr.repas_id = rep.id
            WHERE cr.commande_id = %s
            ORDER BY rep.nom
        """
        
        repas_details = fetch_query(query_repas, [commande_id])
        
        return {
            'commande': commande_info,
            'repas': repas_details
        }
    
    @staticmethod
    def getStatutCommande(commande_id):
        """
        Détermine le statut d'une commande basé sur sa date de création
        Pour la démonstration, on simule différents statuts
        """
        commande = fetch_one("SELECT cree_le FROM commandes WHERE id = %s", [commande_id])
        if not commande:
            return "Commande introuvable"
        
        now = datetime.now()
        cree_le = commande['cree_le']
        
        # Calculer la différence en minutes
        diff_minutes = (now - cree_le).total_seconds() / 60
        
        if diff_minutes < 5:
            return "Commande reçue"
        elif diff_minutes < 15:
            return "En préparation"
        elif diff_minutes < 30:
            return "Prêt pour récupération"
        else:
            return "Disponible"
    
    @staticmethod
    def peutAnnulerCommande(commande_id):
        """
        Vérifie si une commande peut être annulée (moins de 5 minutes)
        """
        commande = fetch_one("SELECT cree_le FROM commandes WHERE id = %s", [commande_id])
        if not commande:
            return False
        
        now = datetime.now()
        cree_le = commande['cree_le']
        diff_minutes = (now - cree_le).total_seconds() / 60
        
        return diff_minutes < 5
    
    @staticmethod
    def annulerCommande(commande_id, client_id):
        """
        Annule une commande si les conditions le permettent
        """
        # Vérifier que la commande appartient au client et peut être annulée
        query_check = """
            SELECT id, cree_le 
            FROM commandes 
            WHERE id = %s AND client_id = %s
        """
        commande = fetch_one(query_check, [commande_id, client_id])
        
        if not commande:
            return False, "Commande introuvable"
        
        # Vérifier le délai de 5 minutes
        now = datetime.now()
        diff_minutes = (now - commande['cree_le']).total_seconds() / 60
        
        if diff_minutes >= 5:
            return False, "Délai d'annulation dépassé (5 minutes)"
        
        try:
            # Supprimer la commande (CASCADE supprimera automatiquement commande_repas)
            execute_query("DELETE FROM commandes WHERE id = %s", [commande_id])
            return True, "Commande annulée avec succès"
        except psycopg2.errors.Error as e:
            return False, f"Erreur lors de l'annulation: {str(e)}"
    
    @staticmethod
    def getClientIdFromEmail(email):
        """
        Récupère l'ID du client à partir de son email
        """
        result = fetch_one("SELECT id FROM clients WHERE email = %s", [email])
        return result['id'] if result else None
    
    @staticmethod
    def getTempsEstimeLivraison(commande_id):
        """
        Calcule le temps estimé de livraison/récupération
        """
        commande = fetch_one("SELECT cree_le FROM commandes WHERE id = %s", [commande_id])
        if not commande:
            return "Non disponible"
        
        now = datetime.now()
        cree_le = commande['cree_le']
        diff_minutes = (now - cree_le).total_seconds() / 60
        
        # Temps estimé total : 30 minutes
        temps_restant = max(0, 30 - diff_minutes)
        
        if temps_restant == 0:
            return "Prêt maintenant"
        elif temps_restant < 1:
            return "Moins d'1 minute"
        else:
            return f"{int(temps_restant)} minutes"
