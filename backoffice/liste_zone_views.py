from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mlunch.core.Zone import Zone
import json
from database.db import fetch_query, execute_query,fetch_one
from django.shortcuts import render

def zones_management(request):
    """Rend la page de gestion des zones."""
    return render(request, 'backoffice/zones_management.html')

@csrf_exempt
def get_zones(request):
    """API pour récupérer la liste des zones avec leurs entités associées."""
    results = Zone.get_zones_with_entities()
    if isinstance(results, list) and results and 'error' in results[0]:
        print(f"Erreur SQL: {results[0]['error']}")  # Log dans le terminal
        return JsonResponse({"error": results[0]['error']}, status=500)
    
    zones = [{
        'id': zone['id'],
        'nom': zone['nom'],
        'description': zone['description'],
        'entites': zone['entites']  # Assurez-vous que 'entites' est inclus
    } for zone in results]
    print(f"Zones récupérées: {zones}")  # Log dans le terminal
    return JsonResponse({'zones': zones})
@csrf_exempt
def get_zone_detail(request, zone_id):
    """API pour récupérer les détails d'une zone avec ses entités."""
    result = Zone.GetZoneFromId(zone_id)
    if 'error' in result:
        print(f"Erreur: {result['error']}")  # Log dans le terminal
        return JsonResponse({"error": result['error']}, status=500 if 'inattendue' in result['error'] else 404)
    
    # Récupérer les entités associées
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
    entites, error = fetch_query(query_entites, (zone_id,))
    if error:
        print(f"Erreur lors de la récupération des entités: {error}")  # Log dans le terminal
        return JsonResponse({"error": f"Erreur lors de la récupération des entités : {str(error)}"}, status=500)
    
    result['entites'] = [dict(e) for e in entites]
    print(f"Détails de la zone {zone_id}: {result}")  # Log dans le terminal
    return JsonResponse(result)


@csrf_exempt
def create_zone(request):
    """API pour créer une nouvelle zone avec ses entités."""
    if request.method != 'POST':
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)
    
    try:
        data = json.loads(request.body)
        print(f"Données reçues: {data}")  # Log des données reçues
        nom = data.get('nom')
        description = data.get('description')
        coordinates = data.get('coordinates')
        initial_statut_id = data.get('statut_id', 1)  # Statut "Active" par défaut
        entite_ids = data.get('entite_ids', [])
        
        # Validations supplémentaires
        if not nom or not isinstance(nom, str) or len(nom.strip()) == 0:
            print("Erreur: Nom de zone manquant ou invalide")  # Log
            return JsonResponse({"error": "Nom de zone manquant ou invalide"}, status=400)
        if description is not None and (not isinstance(description, str) or len(description) > 100):
            print("Erreur: Description invalide (max 100 caractères)")  # Log
            return JsonResponse({"error": "Description invalide (max 100 caractères)"}, status=400)
        if not coordinates or not isinstance(coordinates, list) or len(coordinates) < 3:
            print("Erreur: Coordonnées invalides (minimum 3 points)")  # Log
            return JsonResponse({"error": "Coordonnées invalides (minimum 3 points)"}, status=400)
        if not all(isinstance(coord, list) and len(coord) == 2 and all(isinstance(n, (int, float)) for n in coord) for coord in coordinates):
            print("Erreur: Format des coordonnées invalide, attendu [[lon, lat], ...]")  # Log
            return JsonResponse({"error": "Format des coordonnées invalide, attendu [[lon, lat], ...]"}, status=400)
        if not all(isinstance(id, int) for id in entite_ids):
            print("Erreur: entite_ids doit contenir uniquement des entiers")  # Log
            return JsonResponse({"error": "entite_ids doit contenir uniquement des entiers"}, status=400)
        
        # Créer la zone
        result = Zone.CreateZone(nom, description, coordinates, initial_statut_id)
        if 'error' in result:
            print(f"Erreur lors de la création: {result['error']}")  # Log dans le terminal
            return JsonResponse({"error": result['error']}, status=400)
        
        zone_id = result['zone']['id']
        
        # Associer les entités
        for entite_id in entite_ids:
            query_check_entite = "SELECT id FROM entites WHERE id = %s"
            result_entite, error = fetch_one(query_check_entite, (entite_id,))
            if error or not result_entite:
                print(f"Entité ID {entite_id} non trouvée")  # Log dans le terminal
                return JsonResponse({"error": f"Entité ID {entite_id} non trouvée"}, status=400)
            
            query_reference = """
                INSERT INTO reference_zone_entite (zone_id, entite_id)
                VALUES (%s, %s)
            """
            _, error = execute_query(query_reference, (zone_id, entite_id))
            if error:
                print(f"Erreur lors de l'association de l'entité {entite_id}: {error}")  # Log dans le terminal
                return JsonResponse({"error": f"Erreur lors de l'association de l'entité : {str(error)}"}, status=400)
        
        result['entite_ids'] = entite_ids
        print(f"Zone créée: {result}")  # Log dans le terminal
        return JsonResponse(result, status=201)
    except json.JSONDecodeError:
        print("Erreur: Corps de la requête JSON invalide")  # Log
        return JsonResponse({"error": "Corps de la requête JSON invalide"}, status=400)
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")  # Log dans le terminal
        return JsonResponse({"error": f"Erreur inattendue : {str(e)}"}, status=500)


@csrf_exempt
def update_zone(request, zone_id):
    """API pour mettre à jour une zone et ses entités."""
    if request.method != 'POST':
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)
    
    try:
        data = json.loads(request.body)
        nom = data.get('nom')
        description = data.get('description')
        coordinates = data.get('coordinates')
        entite_ids = data.get('entite_ids')
        statut_id = data.get('statut_id')
        
        # Mettre à jour la zone
        result = Zone.UpdateZone(zone_id, statut_id, nom, description, coordinates)
        if 'error' in result:
            print(f"Erreur lors de la mise à jour: {result['error']}")  # Log dans le terminal
            return JsonResponse({"error": result['error']}, status=400)
        
        # Mettre à jour les entités associées si fournies
        if entite_ids is not None:
            # Supprimer les anciennes associations
            query_delete_references = "DELETE FROM reference_zone_entite WHERE zone_id = %s"
            _, error = execute_query(query_delete_references, (zone_id,))
            if error:
                print(f"Erreur lors de la suppression des associations: {error}")  # Log dans le terminal
                return JsonResponse({"error": f"Erreur lors de la suppression des associations : {str(error)}"}, status=400)
            
            # Ajouter les nouvelles associations
            for entite_id in entite_ids:
                query_check_entite = "SELECT id FROM entites WHERE id = %s"
                result_entite, error = fetch_one(query_check_entite, (entite_id,))
                if error or not result_entite:
                    print(f"Entité ID {entite_id} non trouvée")  # Log dans le terminal
                    return JsonResponse({"error": f"Entité ID {entite_id} non trouvée"}, status=400)
                
                query_reference = """
                    INSERT INTO reference_zone_entite (zone_id, entite_id)
                    VALUES (%s, %s)
                """
                _, error = execute_query(query_reference, (zone_id, entite_id))
                if error:
                    print(f"Erreur lors de l'association de l'entité {entite_id}: {error}")  # Log dans le terminal
                    return JsonResponse({"error": f"Erreur lors de l'association de l'entité : {str(error)}"}, status=400)
        
        result['entite_ids'] = entite_ids if entite_ids is not None else []
        print(f"Zone mise à jour: {result}")  # Log dans le terminal
        return JsonResponse(result)
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")  # Log dans le terminal
        return JsonResponse({"error": f"Erreur inattendue : {str(e)}"}, status=500)

@csrf_exempt
def delete_zone(request, zone_id):
    """API pour marquer une zone comme supprimée."""
    if request.method != 'POST':
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)
    
    try:
        statut_id = 3  # Supposons que 3 est l'ID pour "Supprimée"
        result = Zone.DeleteZone(zone_id, statut_id)
        if 'error' in result:
            print(f"Erreur lors de la suppression: {result['error']}")  # Log dans le terminal
            return JsonResponse({"error": result['error']}, status=400)
        
        print(f"Zone supprimée: {result}")  # Log dans le terminal
        return JsonResponse({"message": "Zone marquée comme supprimée"}, status=200)
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")  # Log dans le terminal
        return JsonResponse({"error": f"Erreur inattendue : {str(e)}"}, status=500)

@csrf_exempt
def get_entites(request):
    """API pour récupérer la liste des entités avec leur statut actuel."""
    query = """
       SELECT 
    e.id, e.nom, se.appellation as statut_actuel
FROM entites e
LEFT JOIN (
    SELECT DISTINCT ON (entite_id) entite_id, statut_id
    FROM historique_statut_entite
    ORDER BY entite_id, id DESC
) latest ON e.id = latest.entite_id
LEFT JOIN statut_entite se ON latest.statut_id = se.id
ORDER BY e.nom
    """
    results, error = fetch_query(query)
    if error:
        print(f"Erreur SQL: {error}")  # Log dans le terminal
        return JsonResponse({"error": f"Erreur lors de la récupération des entités : {str(error)}"}, status=500)
    
    entites = [{'id': row['id'], 'nom': row['nom'], 'statut': row['statut_actuel'] or 'Inconnu'} for row in results]
    print(f"Entités récupérées: {entites}")  # Log dans le terminal
    return JsonResponse({'entites': entites})