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

@csrf_exempt
def get_zone_financials(request, zone_id):
    """API pour récupérer les restaurants et les données financières d'une zone."""
    try:
        # Vérifier si la zone existe
        query_check_zone = "SELECT id FROM zones WHERE id = %s"
        result_zone, error = fetch_one(query_check_zone, (zone_id,))
        if error or not result_zone:
            print(f"Erreur: Zone ID {zone_id} non trouvée")  # Log
            return JsonResponse({"error": f"Zone ID {zone_id} non trouvée"}, status=404)

        # Récupérer les restaurants associés à la zone
        query_restaurants = """
            SELECT 
                r.id, r.nom, r.adresse, sr.appellation as statut_actuel
            FROM zones_restaurant zr
            JOIN restaurants r ON zr.restaurant_id = r.id
            LEFT JOIN (
                SELECT DISTINCT ON (restaurant_id) restaurant_id, statut_id
                FROM historique_statut_restaurant
                ORDER BY restaurant_id, id DESC
            ) latest ON r.id = latest.restaurant_id
            LEFT JOIN statut_restaurant sr ON latest.statut_id = sr.id
            WHERE zr.zone_id = %s
            ORDER BY r.nom
        """
        restaurants, error = fetch_query(query_restaurants, (zone_id,))
        if error:
            print(f"Erreur lors de la récupération des restaurants: {error}")  # Log
            return JsonResponse({"error": f"Erreur lors de la récupération des restaurants : {str(error)}"}, status=500)

        # Récupérer les paramètres de filtrage temporel
        period = request.GET.get('period', 'all')  # 'day', 'month', 'year', 'custom'
        date = request.GET.get('date')  # Format: YYYY-MM-DD
        month = request.GET.get('month')  # Format: YYYY-MM
        year = request.GET.get('year')  # Format: YYYY
        start_date = request.GET.get('start_date')  # Format: YYYY-MM-DD
        end_date = request.GET.get('end_date')  # Format: YYYY-MM-DD

        # Construire la condition temporelle
        time_condition = ""
        time_params = []
        if period == 'day' and date:
            time_condition = "AND DATE(c.cree_le) = %s"
            time_params.append(date)
        elif period == 'month' and month:
            time_condition = "AND TO_CHAR(c.cree_le, 'YYYY-MM') = %s"
            time_params.append(month)
        elif period == 'year' and year:
            time_condition = "AND EXTRACT(YEAR FROM c.cree_le) = %s"
            time_params.append(year)
        elif period == 'custom' and start_date and end_date:
            time_condition = "AND c.cree_le BETWEEN %s AND %s"
            time_params.extend([start_date, end_date])

        # Récupérer le chiffre d'affaires par restaurant et total
        query_financials = f"""
            SELECT 
                r.id, r.nom,
                COALESCE(SUM(cr.quantite * m.prix), 0) as chiffre_affaires,
                COALESCE(cms.valeur, 0) as commission
            FROM zones_restaurant zr
            JOIN restaurants r ON zr.restaurant_id = r.id
            LEFT JOIN point_de_recuperation pr ON pr.id IN (
                SELECT point_recup_id
                FROM commandes
                WHERE EXISTS (
                    SELECT 1
                    FROM commande_repas
                    WHERE commande_id = commandes.id
                )
            )
            LEFT JOIN commandes c ON c.point_recup_id = pr.id
            LEFT JOIN commande_repas cr ON cr.commande_id = c.id
            LEFT JOIN repas m ON cr.repas_id = m.id
            LEFT JOIN commissions cms ON cms.restaurant_id = r.id
            WHERE zr.zone_id = %s
            {time_condition}
            GROUP BY r.id, r.nom, cms.valeur
        """
        params = [zone_id] + time_params
        financials, error = fetch_query(query_financials, tuple(params))
        if error:
            print(f"Erreur lors de la récupération des données financières: {error}")  # Log
            return JsonResponse({"error": f"Erreur lors de la récupération des données financières : {str(error)}"}, status=500)

        # Calculer le chiffre d'affaires total et le bénéfice net
        total_chiffre_affaires = 0
        total_frais = 0
        for f in financials:
            ca = f['chiffre_affaires'] or 0
            commission = f['commission'] or 0
            total_chiffre_affaires += ca
            total_frais += ca * (commission / 100.0)
        
        benefice_net = total_chiffre_affaires - total_frais

        response = {
            'zone_id': zone_id,
            'restaurants': [dict(r) for r in restaurants],
            'financials': {
                'restaurants': [{
                    'id': f['id'],
                    'nom': f['nom'],
                    'chiffre_affaires': float(f['chiffre_affaires'] or 0),
                    'commission': float(f['commission'] or 0)
                } for f in financials],
                'total_chiffre_affaires': float(total_chiffre_affaires),
                'total_frais': float(total_frais),
                'benefice_net': float(benefice_net)
            }
        }
        print(f"Données financières pour la zone {zone_id}: {response}")  # Log
        return JsonResponse(response, status=200)
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")  # Log
        return JsonResponse({"error": f"Erreur inattendue : {str(e)}"}, status=500)

@csrf_exempt
def get_restaurant_detail(request, restaurant_id):
    """API pour récupérer les détails d'un restaurant."""
    try:
        # Vérifier si le restaurant existe
        query_check_restaurant = """
            SELECT id, nom, adresse, ST_AsText(geo_position) as geo_position
            FROM restaurants
            WHERE id = %s
        """
        restaurant, error = fetch_one(query_check_restaurant, (restaurant_id,))
        if error or not restaurant:
            print(f"Erreur: Restaurant ID {restaurant_id} non trouvé")  # Log
            return JsonResponse({"error": f"Restaurant ID {restaurant_id} non trouvé"}, status=404)

        # Récupérer le statut actuel
        query_statut = """
            SELECT sr.appellation as statut_actuel
            FROM historique_statut_restaurant hsr
            LEFT JOIN statut_restaurant sr ON hsr.statut_id = sr.id
            WHERE hsr.restaurant_id = %s
            ORDER BY hsr.mis_a_jour_le DESC
            LIMIT 1
        """
        statut, error = fetch_one(query_statut, (restaurant_id,))
        if error:
            print(f"Erreur lors de la récupération du statut: {error}")  # Log
            return JsonResponse({"error": f"Erreur lors de la récupération du statut : {str(error)}"}, status=500)

        # Récupérer les repas proposés
        query_repas = """
            SELECT r.id, r.nom, r.description, r.prix, tr.nom as type_repas
            FROM repas_restaurant mr
            JOIN repas r ON mr.repas_id = r.id
            JOIN types_repas tr ON r.type_id = tr.id
            WHERE mr.restaurant_id = %s
            ORDER BY r.nom
        """
        repas, error = fetch_query(query_repas, (restaurant_id,))
        if error:
            print(f"Erreur lors de la récupération des repas: {error}")  # Log
            return JsonResponse({"error": f"Erreur lors de la récupération des repas : {str(error)}"}, status=500)

        # Récupérer les horaires réguliers
        query_horaires = """
            SELECT le_jour, horaire_debut, horaire_fin
            FROM horaire
            WHERE restaurant_id = %s
            ORDER BY le_jour
        """
        horaires, error = fetch_query(query_horaires, (restaurant_id,))
        if error:
            print(f"Erreur lors de la récupération des horaires: {error}")  # Log
            return JsonResponse({"error": f"Erreur lors de la récupération des horaires : {str(error)}"}, status=500)

        # Récupérer les horaires exceptionnels
        query_horaires_special = """
            SELECT date_concerne, horaire_debut, horaire_fin
            FROM horaire_special
            WHERE restaurant_id = %s
            ORDER BY date_concerne
        """
        horaires_special, error = fetch_query(query_horaires_special, (restaurant_id,))
        if error:
            print(f"Erreur lors de la récupération des horaires spéciaux: {error}")  # Log
            return JsonResponse({"error": f"Erreur lors de la récupération des horaires spéciaux : {str(error)}"}, status=500)

        response = {
            'restaurant': {
                'id': restaurant['id'],
                'nom': restaurant['nom'],
                'adresse': restaurant['adresse'],
                'geo_position': restaurant['geo_position'],
                'statut_actuel': statut['statut_actuel'] if statut else 'Inconnu'
            },
            'repas': [dict(r) for r in repas],
            'horaires': [dict(h) for h in horaires],
            'horaires_special': [dict(h) for h in horaires_special]
        }
        print(f"Détails du restaurant {restaurant_id}: {response}")  # Log
        return JsonResponse(response, status=200)
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")  # Log
        return JsonResponse({"error": f"Erreur inattendue : {str(e)}"}, status=500)
