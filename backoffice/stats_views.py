from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from database.db import fetch_query
from mlunch.core.Restaurant import Restaurant
from mlunch.core.Zone import Zone
from django.shortcuts import render

def testchart(request):
    return render(request, 'backoffice/stats_dashboard.html')

@csrf_exempt
def get_stats(request):
    """API pour récupérer les statistiques selon les filtres."""
    if request.method != 'POST':
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    try:
        data = json.loads(request.body)
        base_filter = data.get('base_filter')  # 'zone' ou 'restaurant'
        zone_id = data.get('zone_id')  # Optionnel si base_filter='zone'
        restaurant_id = data.get('restaurant_id')  # Optionnel si base_filter='restaurant'
        temporal_filter = data.get('temporal_filter')  # 'day', 'month', 'year'
        content_filter = data.get('content_filter')  # 'revenue' ou 'orders_by_type'

        # Validation des filtres
        if base_filter not in ['zone', 'restaurant']:
            return JsonResponse({"error": "Filtre de base invalide"}, status=400)
        if temporal_filter not in ['day', 'month', 'year']:
            return JsonResponse({"error": "Filtre temporel invalide"}, status=400)
        if content_filter not in ['revenue', 'orders_by_type']:
            return JsonResponse({"error": "Filtre de contenu invalide"}, status=400)
        if base_filter == 'zone' and (not zone_id or not isinstance(zone_id, int)):
            return JsonResponse({"error": "ID de zone invalide"}, status=400)
        if base_filter == 'restaurant' and (not restaurant_id or not isinstance(restaurant_id, int)):
            return JsonResponse({"error": "ID de restaurant invalide"}, status=400)

        # Déterminer le groupement temporel
        date_trunc = {
            'day': "date_trunc('day', c.cree_le)",
            'month': "date_trunc('month', c.cree_le)",
            'year': "date_trunc('year', c.cree_le)"
        }[temporal_filter]

        # Construire la requête SQL
        if content_filter == 'revenue':
            # Chiffre d'affaires
            query = """
                SELECT 
                    %s AS period,
                    COALESCE(SUM(cr.quantite * (r.prix * (1.0 - COALESCE(p.pourcentage_reduction, 0)/100.0))), 0) AS revenue
                FROM commandes c
                JOIN commande_repas cr ON c.id = cr.commande_id
                JOIN repas r ON cr.repas_id = r.id
                LEFT JOIN promotions p ON r.id = p.repas_id 
                    AND p.date_concerne = DATE(c.cree_le)
                JOIN restaurants rest ON r.id IN (
                    SELECT repas_id FROM repas_restaurant WHERE restaurant_id = rest.id
                )
            """ % date_trunc
            params = []

            if base_filter == 'zone':
                query += """
                    JOIN zones_restaurant zr ON rest.id = zr.restaurant_id
                    WHERE zr.zone_id = %s
                """
                params.append(zone_id)
            else:  # restaurant
                query += """
                    WHERE rest.id = %s
                """
                params.append(restaurant_id)

            query += """
                GROUP BY period
                ORDER BY period
            """

        else:  # orders_by_type
            # Nombre de commandes par type de repas
            query = """
                SELECT 
                    tr.nom AS type_repas,
                    COALESCE(SUM(cr.quantite), 0) AS order_count
                FROM commandes c
                JOIN commande_repas cr ON c.id = cr.commande_id
                JOIN repas r ON cr.repas_id = r.id
                JOIN types_repas tr ON r.type_id = tr.id
                JOIN restaurants rest ON r.id IN (
                    SELECT repas_id FROM repas_restaurant WHERE restaurant_id = rest.id
                )
            """
            params = []

            if base_filter == 'zone':
                query += """
                    JOIN zones_restaurant zr ON rest.id = zr.restaurant_id
                    WHERE zr.zone_id = %s
                """
                params.append(zone_id)
            else:  # restaurant
                query += """
                    WHERE rest.id = %s
                """
                params.append(restaurant_id)

            query += """
                GROUP BY tr.nom
            """

        # Exécuter la requête
        results, error = fetch_query(query, params)
        if error:
            print(f"Erreur SQL: {error}")  # Log dans le terminal
            return JsonResponse({"error": f"Erreur lors de la récupération des données : {str(error)}"}, status=500)

        # Formater les résultats
        if content_filter == 'revenue':
            chart_type = 'line'
            data = {
                'labels': [row['period'].strftime('%Y-%m-%d' if temporal_filter == 'day' else '%Y-%m' if temporal_filter == 'month' else '%Y') for row in results],
                'values': [float(row['revenue']) for row in results]
            }
        else:  # orders_by_type
            chart_type = 'pie'
            # Limiter à 5 tranches, regrouper les autres en "Autres"
            if len(results) > 5:
                sorted_results = sorted(results, key=lambda x: x['order_count'], reverse=True)
                top_5 = sorted_results[:5]
                other_sum = sum(row['order_count'] for row in sorted_results[5:])
                results = top_5 + [{'type_repas': 'Autres', 'order_count': other_sum}] if other_sum > 0 else top_5
            data = {
                'labels': [row['type_repas'] for row in results],
                'values': [int(row['order_count']) for row in results]
            }

        print(f"Données récupérées: {data}")  # Log dans le terminal
        return JsonResponse({
            'chart_type': chart_type,
            'data': data
        })

    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")  # Log dans le terminal
        return JsonResponse({"error": f"Erreur inattendue : {str(e)}"}, status=500)

@csrf_exempt

def get_restaurants(request):
    restaurants = Restaurant.GetAllRestaurants()
    print(f"Restaurants récupérés: {restaurants}")  # Log dans le terminal
    return JsonResponse({'restaurants': restaurants})

def get_zones(request):
    
    zones = Zone.GetAllZone()
    print(f"Zones récupérées: {zones}")  # Log dans le terminal
    return JsonResponse({'zones': zones})