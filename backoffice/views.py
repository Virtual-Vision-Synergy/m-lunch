from django.shortcuts import render
from django.contrib import messages
from mlunch.core.Client import Client
from mlunch.core.Commande import Commande
from mlunch.core.Livraison import Livraison
from mlunch.core.Livreur import Livreur
from mlunch.core.Repas import Repas
from mlunch.core.Restaurant import Restaurant
from mlunch.core.Zone import Zone

from django.http import JsonResponse
from django.db import connection
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def test_create_client(request):

        # Créer le client
        result = Zone.delete(1,2)
               
        if 'error' in result:
            messages.error(request, result['error'])
        else:
            #messages.success(request, f"Client créé avec succès : {result['email']}")
            print(result)
        return render(request, 'backoffice/index.html')

def PageAcceuil(request):
    return render(request, 'backoffice/PageAcceuil.html')


def get_restaurants(request):
    """Fetch all restaurants."""
    restaurants = Restaurant.get_all()
    return JsonResponse({"restaurants": restaurants})

def get_zones(request):
    """Fetch all zones."""
    zones = Zone.get_all()
    return JsonResponse({"zones": zones})

def get_stats(request):
    """Fetch stats based on filters: base (restaurant/zone), temporal (day/month/year), content (revenue/orders)."""
    base_filter = request.GET.get("base", "restaurant")  # restaurant, zone, or general
    temporal_filter = request.GET.get("temporal", "day")  # day, month, year
    content_filter = request.GET.get("content", "revenue")  # revenue or orders
    selected_id = request.GET.get("selected_id", None)  # Specific restaurant or zone ID
    general = request.GET.get("general", "false") == "true"  # General overview

    # Determine time range
    end_date = datetime.now()
    if temporal_filter == "day":
        start_date = end_date - timedelta(days=1)
    elif temporal_filter == "month":
        start_date = end_date - relativedelta(months=1)
    else:  # year
        start_date = end_date - relativedelta(years=1)

    # Base query components
    if content_filter == "revenue":
        # Calculate revenue (price * quantity) from commande_repas and repas
        select_clause = """
            SUM(cr.quantite * r.prix) as value,
            TO_CHAR(c.cree_le, %s) as label
        """
        group_by_format = "YYYY-MM-DD" if temporal_filter == "day" else "YYYY-MM" if temporal_filter == "month" else "YYYY"
    else:  # orders by meal type
        select_clause = """
            tr.nom as label,
            COUNT(DISTINCT cr.commande_id) as value
        """
        group_by_format = None

    # Join tables
    from_clause = """
        FROM commandes c
        JOIN commande_repas cr ON c.id = cr.commande_id
        JOIN repas r ON cr.repas_id = r.id
        JOIN types_repas tr ON r.type_id = tr.id
    """
    where_clause = "WHERE c.cree_le BETWEEN %s AND %s"
    params = [start_date, end_date]

    # Apply base filter (restaurant or zone)
    if not general and selected_id:
        if base_filter == "restaurant":
            from_clause += " JOIN repas_restaurant rr ON r.id = rr.repas_id"
            where_clause += " AND rr.restaurant_id = %s"
            params.append(selected_id)
        elif base_filter == "zone":
            from_clause += """
                JOIN repas_restaurant rr ON r.id = rr.repas_id
                JOIN zones_restaurant zr ON rr.restaurant_id = zr.restaurant_id
            """
            where_clause += " AND zr.zone_id = %s"
            params.append(selected_id)

    # Group by
    group_by_clause = ""
    if content_filter == "revenue":
        group_by_clause = f"GROUP BY TO_CHAR(c.cree_le, %s)"
        params.insert(0, group_by_format)
    else:
        group_by_clause = "GROUP BY tr.nom"

    # Construct final query
    query = f"SELECT {select_clause} {from_clause} {where_clause} {group_by_clause}"
    
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Format data for Chart.js
        labels = []
        values = []
        for row in results:
            labels.append(row[1])
            values.append(float(row[0]) if content_filter == "revenue" else int(row[0]))

    return JsonResponse({
        "labels": labels,
        "values": values,
        "content_type": content_filter
    })