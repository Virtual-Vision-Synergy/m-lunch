from django.shortcuts import render
from django.db import connection
from django.http import Http404

def GetRestaurant(restaurant_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                r.id, 
                r.nom, 
                r.image, 
                STRING_AGG(z.nom, ', ') AS secteurs
            FROM restaurants r
            LEFT JOIN zones_restaurant zr ON r.id = zr.restaurant_id
            LEFT JOIN zones z ON zr.zone_id = z.id
            WHERE r.id = %s
            GROUP BY r.id, r.nom, r.image
        """, [restaurant_id])
        restaurant_row = cursor.fetchone()
        if not restaurant_row:
            raise Http404("Restaurant introuvable")
        
        return {
            'id': restaurant_row[0],
            'nom': restaurant_row[1],
            'image': restaurant_row[2] or '',
            'secteurs': restaurant_row[3] or 'N/A'
        }

def GetCommande(restaurant_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.id AS numero,
                c.cree_le AS date_heure,
                CONCAT(cl.prenom, ' ', cl.nom) AS client_name,
                cl.email AS client_email,
                COALESCE(SUM(cr.quantite), 0) AS nombre_repas,
                COALESCE(SUM(cr.quantite * r.prix), 0.00) AS prix_total,
                sc.appellation AS statut,
                STRING_AGG(CONCAT(r.nom, ': ', cr.quantite), ', ') AS repas_details,
                z.id AS secteur_id,
                mp.nom AS mode_paiement
            FROM commandes c
            JOIN clients cl ON c.client_id = cl.id
            LEFT JOIN zones_clients zc ON cl.id = zc.client_id
            LEFT JOIN zones z ON zc.zone_id = z.id
            JOIN historique_statut_commande hsc ON c.id = hsc.commande_id
            JOIN statut_commande sc ON hsc.statut_id = sc.id
            LEFT JOIN commande_repas cr ON c.id = cr.commande_id
            LEFT JOIN repas r ON cr.repas_id = r.id
            LEFT JOIN repas_restaurant rr ON r.id = rr.repas_id
            LEFT JOIN commande_paiement cp ON c.id = cp.paiement_id
            LEFT JOIN mode_de_paiement mp ON cp.paiement_id = mp.id
            WHERE rr.restaurant_id = %s
            GROUP BY c.id, c.cree_le, cl.prenom, cl.nom, cl.email, sc.appellation, z.id, mp.nom
            ORDER BY c.cree_le DESC
        """, [restaurant_id])
        rows = cursor.fetchall()

    return [
        {
            'numero': row[0],
            'date_heure': row[1],
            'client_name': row[2] or 'N/A',
            'client_email': row[3] or 'N/A',
            'nombre_repas': row[4],
            'prix_total': float(row[5]),
            'statut': row[6] or 'N/A',
            'repas_details': row[7] or 'Aucun plat',
            'secteur_id': row[8] or '',
            'mode_paiement': row[9] or 'N/A'
        }
        for row in rows
    ]

def GetStatues():
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT appellation FROM statut_commande")
        return [row[0] for row in cursor.fetchall()]

def GetHorraireRestaurant(restaurant_id):
    with connection.cursor() as cursor:
        # Verify restaurant exists
        cursor.execute("SELECT id FROM restaurants WHERE id = %s", [restaurant_id])
        if not cursor.fetchone():
            raise Http404("Restaurant introuvable")

        # Fetch regular hours
        cursor.execute("""
            SELECT 
                le_jour, 
                horaire_debut, 
                horaire_fin 
            FROM horaire 
            WHERE restaurant_id = %s 
            ORDER BY le_jour
        """, [restaurant_id])
        regular_hours = [
            {
                'day': row[0],  # 1-7 (Monday-Sunday)
                'start_time': row[1].strftime('%H:%M') if row[1] else None,
                'end_time': row[2].strftime('%H:%M') if row[2] else None
            }
            for row in cursor.fetchall()
        ]

        # Fetch special hours
        cursor.execute("""
            SELECT 
                date_concerne, 
                horaire_debut, 
                horaire_fin 
            FROM horaire_special 
            WHERE restaurant_id = %s 
            ORDER BY date_concerne
        """, [restaurant_id])
        special_hours = [
            {
                'date': row[0].strftime('%Y-%m-%d'),
                'start_time': row[1].strftime('%H:%M') if row[1] else None,
                'end_time': row[2].strftime('%H:%M') if row[2] else None
            }
            for row in cursor.fetchall()
        ]

    return {
        'regular_hours': regular_hours,
        'special_hours': special_hours
    }

def GetCommandeResto(request, restaurant_id):
    restaurant = GetRestaurant(restaurant_id)
    orders = GetCommande(restaurant_id)
    statuses = GetStatues()
    horaires = GetHorraireRestaurant(restaurant_id)

    context = {
        'restaurant': restaurant,
        'orders': orders,
        'statuses': statuses,
        'horaires' : horaires,
    }

    return render(request, 'backoffice/restaurant_commande.html', context)