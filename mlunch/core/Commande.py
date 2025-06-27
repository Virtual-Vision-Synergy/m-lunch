import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Commande:
    def __init__(self, id=None, client_id=None, point_recup_id=None, cree_le=None):
        self.id = id
        self.client_id = client_id
        self.point_recup_id = point_recup_id
        self.cree_le = cree_le

    @staticmethod
    def Create(clientId: int, pointRecupId: int, statutId: int) -> Dict[str, Any]:
        if not isinstance(clientId, int) or clientId <= 0:
            return {"error": "ClientId invalide"}
        if not isinstance(pointRecupId, int) or pointRecupId <= 0:
            return {"error": "PointRecupId invalide"}
        if not isinstance(statutId, int) or statutId <= 0:
            return {"error": "StatutId invalide"}

        try:
            queryCommande = """
                INSERT INTO commandes (client_id, point_recup_id)
                VALUES (%s, %s)
                RETURNING id, client_id, point_recup_id, cree_le
            """
            resultCommande, error = fetch_one(queryCommande, (clientId, pointRecupId))
            if error:
                return {"error": f"Erreur insertion commande : {str(error)}"}
            if not resultCommande:
                return {"error": "Insertion commande échouée"}

            commandeId = resultCommande['id']

            queryCheckStatut = "SELECT id FROM statut_commande WHERE id = %s"
            resultStatut, error = fetch_one(queryCheckStatut, (statutId,))
            if error or not resultStatut:
                return {"error": "Statut non trouvé"}

            queryHistorique = """
                INSERT INTO historique_statut_commande (commande_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, commande_id, statut_id, mis_a_jour_le
            """
            resultHistorique, error = fetch_one(queryHistorique, (commandeId, statutId))
            if error:
                return {"error": f"Erreur historique : {str(error)}"}

            return {"commande": resultCommande, "historique": resultHistorique}

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetCommandeFromId(commandeId: int) -> Dict[str, Any]:
        if not isinstance(commandeId, int) or commandeId <= 0:
            return {"error": "CommandeId invalide"}

        query = """
            SELECT c.id, c.client_id, c.point_recup_id, c.cree_le,
                   h.statut_id, h.mis_a_jour_le
            FROM commandes c
            JOIN historique_statut_commande h ON c.id = h.commande_id
            WHERE c.id = %s
            ORDER BY h.mis_a_jour_le DESC
        """
        rows, error = fetch_query(query, (commandeId,), as_dict=True)
        if error:
            return {"error": f"Erreur récupération : {str(error)}"}
        if not rows:
            return {"error": "Commande non trouvée"}
        return {"data": rows}

    @staticmethod
    def GetAllCommandes() -> List[Dict[str, Any]]:
        query = "SELECT id, client_id, point_recup_id, cree_le FROM commandes ORDER BY cree_le DESC"
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur récupération : {str(error)}"}]
        return [dict(row) for row in results]

    @staticmethod
    def UpdateCommandeStatut(commandeId: int, statutId: int) -> Optional[Dict[str, Any]]:
        if not isinstance(commandeId, int) or not isinstance(statutId, int):
            return {"error": "Paramètres invalides"}

        queryCheckStatut = "SELECT id FROM statut_commande WHERE id = %s"
        resultStatut, error = fetch_one(queryCheckStatut, (statutId,))
        if error or not resultStatut:
            return {"error": "Statut non trouvé"}

        query = """
            INSERT INTO historique_statut_commande (commande_id, statut_id)
            VALUES (%s, %s)
            RETURNING id, commande_id, statut_id, mis_a_jour_le
        """
        result, error = fetch_one(query, (commandeId, statutId))
        if error:
            return {"error": f"Erreur mise à jour statut : {str(error)}"}
        return dict(result) if result else None

    @staticmethod
    def DeleteCommandeLogique(commandeId: int, statutId: int) -> Optional[Dict[str, Any]]:
        return Commande.UpdateCommandeStatut(commandeId, statutId)
