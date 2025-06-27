import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import fetch_query, fetch_one

class Entite:
    def __init__(self, id=None, nom=None):
        self.id = id
        self.nom = nom

    @staticmethod
    def Create(nom):
        if nom is not None and (not isinstance(nom, str) or len(nom) > 100):
            return {"error": "Nom invalide : doit être une chaîne de 100 caractères maximum"}

        statut_id = 1

        queryCheckStatut = "SELECT id FROM statut_entite WHERE id = %s"
        resultStatut, error = fetch_one(queryCheckStatut, (statut_id,))
        if error or not resultStatut:
            return {"error": "Statut d'entité non trouvé"}

        queryInsertEntite = """
            INSERT INTO entites (nom)
            VALUES (%s)
            RETURNING id, nom
        """
        resultEntite, error = fetch_one(queryInsertEntite, (nom,))
        if error:
            return {"error": f"Erreur lors de la création de l'entité : {str(error)}"}
        if not resultEntite:
            return {"error": "Échec de la création de l'entité"}

        queryInsertHistorique = """
            INSERT INTO historique_statut_entite (entite_id, statut_id)
            VALUES (%s, %s)
            RETURNING id, entite_id, statut_id, mis_a_jour_le
        """
        resultHistorique, error = fetch_one(queryInsertHistorique, (resultEntite["id"], statut_id))
        if error:
            return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}

        entite = Entite(**resultEntite)
        return {"entite": entite, "historique": resultHistorique}

    @staticmethod
    def GetById(entiteId):
        if not isinstance(entiteId, int) or entiteId <= 0:
            return {"error": "ID invalide"}

        query = """
            SELECT 
                e.id AS entite_id, e.nom AS entite_nom,
                h.id AS historique_id, h.statut_id, h.mis_a_jour_le,
                s.appellation AS statut_appellation
            FROM entites e
            LEFT JOIN historique_statut_entite h ON e.id = h.entite_id
            LEFT JOIN statut_entite s ON h.statut_id = s.id
            WHERE e.id = %s
            ORDER BY h.mis_a_jour_le DESC
        """
        rows, error = fetch_query(query, (entiteId,), as_dict=True)
        if error:
            return {"error": f"Erreur lors de la récupération : {str(error)}"}
        if not rows:
            return {"error": "Aucune entité trouvée"}
        return {"data": rows}

    @staticmethod
    def GetAll():
        query = "SELECT id, nom FROM entites ORDER BY nom"
        results, error = fetch_query(query)
        if error:
            return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
        return [Entite(**row) for row in results]

    @staticmethod
    def Update(entiteId, statutId, nom=None):
        if not isinstance(entiteId, int) or entiteId <= 0 or not isinstance(statutId, int) or statutId <= 0:
            return {"error": "ID invalide"}
        if nom is not None and (not isinstance(nom, str) or len(nom) > 100):
            return {"error": "Nom invalide"}

        checkEntiteQuery = "SELECT id FROM entites WHERE id = %s"
        foundEntite, error = fetch_one(checkEntiteQuery, (entiteId,))
        if error or not foundEntite:
            return {"error": "Entité non trouvée"}

        checkStatutQuery = "SELECT id FROM statut_entite WHERE id = %s"
        foundStatut, error = fetch_one(checkStatutQuery, (statutId,))
        if error or not foundStatut:
            return {"error": "Statut d'entité non trouvé"}

        queryUpdate = """
            UPDATE entites
            SET nom = COALESCE(%s, nom)
            WHERE id = %s
            RETURNING id, nom
        """
        resultEntite, error = fetch_one(queryUpdate, (nom, entiteId))
        if error:
            return {"error": f"Erreur lors de la mise à jour de l'entité : {str(error)}"}
        if not resultEntite:
            return {"error": "Échec de la mise à jour"}

        queryHistorique = """
            INSERT INTO historique_statut_entite (entite_id, statut_id)
            VALUES (%s, %s)
            RETURNING id, entite_id, statut_id, mis_a_jour_le
        """
        resultHistorique, error = fetch_one(queryHistorique, (entiteId, statutId))
        if error:
            return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}

        return {"entite": Entite(**resultEntite), "historique": resultHistorique}

    @staticmethod
    def Delete(entiteId):
        if not isinstance(entiteId, int) or entiteId <= 0:
            return {"error": "ID invalide"}

        queryCheck = "SELECT id FROM entites WHERE id = %s"
        found, error = fetch_one(queryCheck, (entiteId,))
        if error or not found:
            return {"error": "Entité non trouvée"}

        statutId = 2

        checkStatutQuery = "SELECT id FROM statut_entite WHERE id = %s"
        foundStatut, error = fetch_one(checkStatutQuery, (statutId,))
        if error or not foundStatut:
            return {"error": "Statut d'entité non trouvé"}

        queryHistorique = """
            INSERT INTO historique_statut_entite (entite_id, statut_id)
            VALUES (%s, %s)
            RETURNING id, entite_id, statut_id, mis_a_jour_le
        """
        resultHistorique, error = fetch_one(queryHistorique, (entiteId, statutId))
        if error:
            return {"error": f"Erreur lors de l'enregistrement dans l'historique : {str(error)}"}

        return {"success": True, "historique": resultHistorique}
