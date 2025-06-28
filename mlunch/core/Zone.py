import psycopg2.errors
from typing import Optional, Dict, List, Any
from database.db import execute_query, fetch_query, fetch_one

class Zone:
    """Classe représentant une zone de livraison dans le système."""

    @staticmethod
    def CreateZone(nom, description, coordinates, initial_statut_id):
        """Crée une nouvelle zone avec son historique et statut initial."""
        # Validation des entrées
        if not isinstance(nom, str) or len(nom) > 100 or not nom.strip():
            return {"error": "Nom de zone invalide"}
        if not isinstance(description, str) or len(description) > 100:
            return {"error": "Description invalide"}
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "ID statut invalide"}
        if not isinstance(coordinates, list) or len(coordinates) < 3:
            return {"error": "Coordonnées du polygone invalides (minimum 3 points)"}

        # Démarrer une transaction
        try:
            # Convertir les coordonnées en format WKT pour PostgreSQL
            polygon_wkt = "POLYGON((" + ",".join([f"{lon} {lat}" for lon, lat in coordinates]) + "))"

            # Insérer la zone
            query_zone = """
                INSERT INTO zones (nom, description, zone)
                VALUES (%s, %s, ST_GeomFromText(%s, 4326))
                RETURNING id, nom, description, ST_AsText(zone) as zone
            """
            result_zone, error = fetch_one(query_zone, (nom, description, polygon_wkt))
            if error:
                return {"error": f"Erreur lors de la création de la zone : {str(error)}"}
            if not result_zone:
                return {"error": "Échec de la création de la zone"}

            zone_id = result_zone['id']

            # Vérifier si le statut existe
            query_statut = """
                SELECT id FROM statut_zone WHERE id = %s
            """
            result_statut, error = fetch_one(query_statut, (initial_statut_id,))
            if error or not result_statut:
                return {"error": "Statut zone non trouvé"}

            # Insérer dans l'historique
            query_historique = """
                INSERT INTO historique_statut_zone (zone_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, zone_id, statut_id, mis_a_jour_le
            """
            result_historique, error = fetch_one(query_historique, (zone_id, initial_statut_id))
            if error:
                return {"error": f"Erreur lors de la création de l'historique : {str(error)}"}
            if not result_historique:
                return {"error": "Échec de la création de l'historique"}

            # Retourner les informations complètes
            return {
                "zone": dict(result_zone),
                "historique": dict(result_historique)
            }

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetZoneFromId(zone_id):
        """
        Récupère une zone par son ID avec son historique complet des statuts.
        
        Args:
            zone_id (int): L'ID de la zone à récupérer.
        
        Returns:
            dict: Dictionnaire avec:
                - 'zone': les infos de la zone
                - 'statuts': liste des statuts historiques
                En cas d'erreur, retourne un dictionnaire avec une clé 'error'.
        """
        if not isinstance(zone_id, int) or zone_id <= 0:
            return {"error": "ID zone invalide"}

        try:
            # Requête pour les infos de la zone
            query_zone = """
                SELECT 
                    z.id, z.nom, z.description, ST_AsText(z.zone) as zone,
                    sz.appellation as statut_actuel
                FROM zones z
                LEFT JOIN (
                    SELECT zone_id, statut_id
                    FROM historique_statut_zone
                    WHERE id = (
                        SELECT MAX(id) 
                        FROM historique_statut_zone 
                        WHERE zone_id = %s
                    )
                ) latest ON z.id = latest.zone_id
                LEFT JOIN statut_zone sz ON latest.statut_id = sz.id
                WHERE z.id = %s
            """
            
            # Requête pour l'historique des statuts
            query_historique = """
                SELECT 
                    h.id, h.statut_id, h.mis_a_jour_le,
                    sz.appellation as statut_nom
                FROM historique_statut_zone h
                JOIN statut_zone sz ON h.statut_id = sz.id
                WHERE h.zone_id = %s
                ORDER BY h.mis_a_jour_le DESC
            """

            # Exécution des requêtes
            zone, error = fetch_one(query_zone, (zone_id, zone_id))
            if error or not zone:
                return {"error": "Zone non trouvée" if not error else f"Erreur : {str(error)}"}
            
            historiques, error = fetch_query(query_historique, (zone_id,))
            if error:
                return {"error": f"Erreur historique : {str(error)}"}

            # Formatage des résultats
            result = {
                "zone": dict(zone),
                "statuts": [dict(h) for h in historiques] if historiques else []
            }
            
            return result

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}

    @staticmethod
    def GetAllZone() -> List[Dict[str, Any]]:
            """Récupère toutes les zones."""
            query = """
                SELECT id, nom, description, ST_AsText(zone) as zone
                FROM zones
                ORDER BY nom
            """
            results, error = fetch_query(query)
            if error:
                return [{"error": f"Erreur lors de la récupération : {str(error)}"}]
            return [dict(row) for row in results]

    @staticmethod
    @staticmethod
    def UpdateZone(zone_id, statut_id, nom, description, coordinates):
        """Mettre à jour une zone existante."""
        if not isinstance(zone_id, int) or zone_id < 1:
            return {'error': 'ID de zone invalide'}
        if nom and (not isinstance(nom, str) or len(nom.strip()) > 100):
            return {'error': 'Nom de zone invalide'}
        if description and (not isinstance(description, str) or len(description) > 100):
            return {'error': 'Description invalide (max 100 caractères)'}
        if coordinates and (not isinstance(coordinates, list) or len(coordinates) < 3):
            return {'error': 'Coordonnées du polygone invalides (minimum 3 points)'}
        if coordinates and not all(isinstance(coord, list) and len(coord) == 2 and all(isinstance(n, (int, float)) for n in coord) for coord in coordinates):
            return {'error': 'Format des coordonnées invalide, attendu [[lon, lat], ...]'}
        
        # Vérifier si la zone existe
        query_check_zone = "SELECT id FROM zones WHERE id = %s"
        result_zone, error = fetch_one(query_check_zone, (zone_id,))
        if error or not result_zone:
            return {'error': f"Zone ID {zone_id} non trouvée"}
        
        params = []
        updates = []
        
        if nom:
            updates.append("nom = %s")
            params.append(nom.strip())
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if coordinates:
            try:
                wkt = f"POLYGON(({', '.join([f'{lon} {lat}' for lon, lat in coordinates])}))"
                print(f"Chaîne WKT générée pour mise à jour : {wkt}")  # Log pour débogage
                # Vérifier si la chaîne WKT est valide
                if not wkt.startswith('POLYGON((') or not wkt.endswith('))'):
                    return {'error': 'Format WKT invalide'}
                updates.append("zone = ST_GeomFromText(%s, 4326)")
                params.append(wkt)
            except Exception as e:
                return {'error': f"Erreur lors de la génération de la chaîne WKT : {str(e)}"}
        
        if not updates:
            return {'error': 'Aucune mise à jour fournie'}
        
        query = f"""
            UPDATE zones
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, nom, description, ST_AsText(zone) as zone
        """
        params.append(zone_id)
        result, error = fetch_one(query, tuple(params))
        if error:
            return {'error': f"Échec de la mise à jour : {str(error)}"}
        
        if statut_id:
            query_historique = """
                INSERT INTO historique_statut_zone (zone_id, statut_id, mis_a_jour_le)
                VALUES (%s, %s, NOW())
                RETURNING id, zone_id, statut_id, mis_a_jour_le
            """
            historique, error = fetch_one(query_historique, (zone_id, statut_id))
            if error:
                return {'error': f"Échec de l'insertion dans l'historique : {str(error)}"}
        else:
            historique = None
        
        return {
            'zone': {
                'id': result['id'],
                'nom': result['nom'],
                'description': result['description'],
                'zone': result['zone']
            },
            'historique': {
                'id': historique['id'],
                'zone_id': historique['zone_id'],
                'statut_id': historique['statut_id'],
                'mis_a_jour_le': historique['mis_a_jour_le'].isoformat()
            } if historique else None
        }

    @staticmethod
    def DeleteZone(zone_id, statut_id):
        """
        Marque une zone comme supprimée en mettant à jour son statut dans l'historique.
        
        Args:
            zone_id (int): ID de la zone à marquer comme supprimée
            statut_id (int): ID du statut "supprimé" ou "inactif"
        
        Returns:
            dict: Résultat de la mise à jour ou message d'erreur
        """
        # Validation des paramètres
        if not isinstance(zone_id, int) or zone_id <= 0:
            return {"error": "ID zone invalide"}
        if not isinstance(statut_id, int) or statut_id <= 0:
            return {"error": "ID statut invalide"}

        try:
            # Vérifier si la zone existe
            query_check_zone = "SELECT id FROM zones WHERE id = %s"
            zone_exists, error = fetch_one(query_check_zone, (zone_id,))
            if error or not zone_exists:
                return {"error": "Zone non trouvée"}

            # Vérifier si le statut existe
            query_check_statut = "SELECT id FROM statut_zone WHERE id = %s"
            statut_exists, error = fetch_one(query_check_statut, (statut_id,))
            if error or not statut_exists:
                return {"error": "Statut zone non trouvé"}

            # Mettre à jour l'historique avec le nouveau statut
            query = """
                INSERT INTO historique_statut_zone (zone_id, statut_id)
                VALUES (%s, %s)
                RETURNING id, zone_id, statut_id, mis_a_jour_le
            """
            result, error = fetch_one(query, (zone_id, statut_id))
            if error:
                return {"error": f"Erreur lors de la mise à jour du statut : {str(error)}"}
            
            return dict(result) if result else None

        except Exception as e:
            return {"error": f"Erreur inattendue : {str(e)}"}
        
    @staticmethod
    def get_zones_with_entities() -> List[Dict[str, Any]]:
        """
        Récupère toutes les zones avec leurs entités associées et statuts actuels.
        """
        try:
            # Récupérer toutes les zones via la fonction existante
            zones = Zone.get_all()
            if isinstance(zones, list) and zones and 'error' in zones[0]:
                return [{"error": zones[0]['error']}]

            # Pour chaque zone, récupérer les entités associées
            results = []
            for zone in zones:
                query_entites = """
                    SELECT 
                        e.id, e.nom, se.appellation as statut_actuel
                    FROM reference_zone_entite rze
                    JOIN entites e ON rze.entite_id = e.id
                    LEFT JOIN (
                        SELECT DISTINCT ON (entite_id) entite_id, statut_id
                        FROM historique_statut_entite
                        ORDER BY entite_id, id DESC
                    ) latest ON e.id = latest.entite_id
                    LEFT JOIN statut_entite se ON latest.statut_id = se.id
                    WHERE rze.zone_id = %s
                """
                entites, error = fetch_query(query_entites, (zone['id'],))
                if error:
                    return [{"error": f"Erreur lors de la récupération des entités : {str(error)}"}]
                
                formatted_zone = {
                    "id": zone["id"],
                    "nom": zone["nom"],
                    "description": zone["description"],
                    "zone": zone["zone"],
                    "entites": [
                        {"id": e["id"], "nom": e["nom"], "statut": e["statut_actuel"] or "Inconnu"}
                        for e in entites
                    ]
                }
                results.append(formatted_zone)

            return results

        except Exception as e:
            return [{"error": f"Erreur inattendue : {str(e)}"}]