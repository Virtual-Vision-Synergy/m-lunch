from django.shortcuts import render
from django.db import connection

def GetAllCommandeAttente(zone_id=None, restaurant_id=None):
    query = """
        SELECT 
            c.id AS numero,
            CONCAT(cl.prenom, ' ', cl.nom) AS client_name,
            z.nom AS secteur,
            c.cree_le AS date_heure,
            COALESCE(SUM(cr.quantite), 0) AS nombre_repas,
            COALESCE(SUM(cr.quantite * r.prix), 0.00) AS prix_total
        FROM commandes c
        JOIN clients cl ON c.client_id = cl.id
        LEFT JOIN zones_clients zc ON cl.id = zc.client_id
        LEFT JOIN zones z ON zc.zone_id = z.id
        JOIN historique_statut_commande hsc ON c.id = hsc.commande_id
        JOIN statut_commande sc ON hsc.statut_id = sc.id
        LEFT JOIN commande_repas cr ON c.id = cr.commande_id
        LEFT JOIN repas r ON cr.repas_id = r.id
        WHERE sc.appellation = 'En attente'
    """
    
    params = []

    if zone_id:
        query += " AND zc.zone_id = %s"
        params.append(zone_id)
    if restaurant_id:
        query += """
            AND r.id IN (
                SELECT repas_id 
                FROM repas_restaurant 
                WHERE restaurant_id = %s
            )
        """
        params.append(restaurant_id)

    query += " GROUP BY c.id, cl.prenom, cl.nom, z.nom, c.cree_le ORDER BY c.cree_le DESC"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    return [
        {
            'numero': row[0],
            'client_name': row[1],
            'secteur': row[2] if row[2] else 'N/A',
            'date_heure': row[3],
            'nombre_repas': row[4],
            'prix_total': float(row[5]),
        }
        for row in rows
    ]

def GetZones():
    """
    Fetch all zones from the database.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nom FROM zones")
        return [{'id': row[0], 'nom': row[1]} for row in cursor.fetchall()]

def GetRestaurants():
    """
    Fetch all restaurants from the database.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nom FROM restaurants")
        return [{'id': row[0], 'nom': row[1]} for row in cursor.fetchall()]

def GetCommandeAttente(request):
    """
    Main view to render the pending orders page with filters for zone and restaurant.
    """
    zone_id = request.GET.get('zone')
    restaurant_id = request.GET.get('restaurant')

    orders = GetAllCommandeAttente(zone_id, restaurant_id)
    zones = GetZones()
    restaurants = GetRestaurants()

    context = {
        'orders': orders,
        'zones': zones,
        'restaurants': restaurants,
        'selected_zone': zone_id,
        'selected_restaurant': restaurant_id,
    }

    return render(request, 'backoffice/back_office_commande_attente.html', context)