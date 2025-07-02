from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
import re

# ========== FONCTIONS UTILITAIRES ==========

def GetZones():
    """Récupère toutes les zones disponibles."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nom FROM zones")
        return [{'id': row[0], 'nom': row[1]} for row in cursor.fetchall()]

def GetStatuses():
    """Récupère tous les statuts de livreur disponibles."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, appellation FROM statut_livreur")
        return [{'id': row[0], 'appellation': row[1]} for row in cursor.fetchall()]

def ValiderPosition(position):
    """Valide et formate une position géographique."""
    if not position:
        return None
    if not re.match(r'^-?\d+\.?\d*,-?\d+\.?\d*$', position):
        return False
    lat, lon = position.split(',')
    return f"POINT({lon.strip()} {lat.strip()})"

def FormatPositionToWKT(position_wkt):
    """Formate une position WKT pour l'affichage."""
    if not position_wkt:
        return ''
    return position_wkt.replace('POINT(', '').replace(')', '')

def FormatPositionToLatLon(position_wkt):
    """Formate une position WKT en latitude,longitude."""
    if not position_wkt:
        return 'N/A'
    position = position_wkt.replace('POINT(', '').replace(')', '')
    longitude, latitude = position.split()
    return f"{latitude},{longitude}"

# ========== FONCTIONS DE BASE DE DONNÉES POUR LIVREUR ==========

def InsertLivreur(nom, contact, position_wkt):
    """Insère un nouveau livreur dans la base de données."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO livreurs (nom, contact, position, date_inscri)
            VALUES (%s, %s, ST_GeomFromText(%s, 4326), NOW())
            RETURNING id
        """, [nom, contact, position_wkt])
        return cursor.fetchone()[0]

def InsertLivreurStatus(livreur_id, statut):
    """Insère un nouveau statut pour un livreur."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO historique_statut_livreur (livreur_id, statut_id, mis_a_jour_le)
            SELECT %s, id, NOW()
            FROM statut_livreur
            WHERE appellation = %s
        """, [livreur_id, statut])

def InsertLivreurZones(livreur_id, zones):
    """Insère les zones d'un livreur."""
    with connection.cursor() as cursor:
        for zone_id in zones:
            cursor.execute("""
                INSERT INTO zones_livreurs (livreur_id, zone_id, mis_a_jour_le)
                VALUES (%s, %s, NOW())
            """, [livreur_id, zone_id])

def GetLivreurDetails(livreur_id):
    """Récupère les détails d'un livreur."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nom, contact, ST_AsText(position) AS position
            FROM livreurs
            WHERE id = %s
        """, [livreur_id])
        return cursor.fetchone()

def GetLivreurZones(livreur_id):
    """Récupère les zones actuelles d'un livreur."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT zone_id
            FROM zones_livreurs
            WHERE livreur_id = %s
        """, [livreur_id])
        return [row[0] for row in cursor.fetchall()]

def GetLivreurStatus(livreur_id):
    """Récupère le statut actuel d'un livreur."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT sl.appellation
            FROM historique_statut_livreur hsl
            JOIN statut_livreur sl ON hsl.statut_id = sl.id
            WHERE hsl.livreur_id = %s
            ORDER BY hsl.mis_a_jour_le DESC
            LIMIT 1
        """, [livreur_id])
        result = cursor.fetchone()
        return result[0] if result else 'Disponible'

def UpdateLivreurDetails(livreur_id, nom, contact, position_wkt):
    """Met à jour les détails d'un livreur."""
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE livreurs
            SET nom = %s, contact = %s, position = ST_GeomFromText(%s, 4326)
            WHERE id = %s
        """, [nom, contact, position_wkt, livreur_id])

def DeleteLivreurZones(livreur_id):
    """Supprime toutes les zones d'un livreur."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM zones_livreurs WHERE livreur_id = %s", [livreur_id])

def CheckLivraison(livreur_id):
    """Vérifie si un livreur a des livraisons actives."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM livraisons l
            JOIN historique_statut_livraison hsl ON l.id = hsl.livraison_id
            JOIN statut_livraison sl ON hsl.statut_id = sl.id
            WHERE l.livreur_id = %s AND sl.appellation IN ('En cours', 'Attribué')
        """, [livreur_id])
        return cursor.fetchone()[0]

def GetHistoriqueLivraison(livreur_id):
    """Récupère l'historique des livraisons d'un livreur."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.id AS numero,
                c.cree_le AS date_heure,
                CONCAT(cl.prenom, ' ', cl.nom) AS client_name,
                COALESCE(SUM(cr.quantite), 0) AS nombre_repas,
                COALESCE(SUM(cr.quantite * r.prix), 0.00) AS prix_total,
                sl.appellation AS statut
            FROM livraisons l
            JOIN commandes c ON l.commande_id = c.id
            JOIN clients cl ON c.client_id = cl.id
            LEFT JOIN commande_repas cr ON c.id = cr.commande_id
            LEFT JOIN repas r ON cr.repas_id = r.id
            JOIN historique_statut_livraison hsl ON l.id = hsl.livraison_id
            JOIN statut_livraison sl ON hsl.statut_id = sl.id
            WHERE l.livreur_id = %s
            GROUP BY c.id, c.cree_le, cl.prenom, cl.nom, sl.appellation
            ORDER BY c.cree_le DESC
        """, [livreur_id])
        return [
            {
                'numero': row[0],
                'date_heure': row[1],
                'client_name': row[2],
                'nombre_repas': row[3],
                'prix_total': float(row[4]),
                'statut': row[5]
            }
            for row in cursor.fetchall()
        ]

def GetCommandeNonLivree():
    """Récupère les commandes non attribuées."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.id AS numero,
                CONCAT(cl.prenom, ' ', cl.nom) AS client_name,
                c.cree_le AS date_heure,
                COALESCE(SUM(cr.quantite), 0) AS nombre_repas
            FROM commandes c
            JOIN clients cl ON c.client_id = cl.id
            LEFT JOIN commande_repas cr ON c.id = cr.commande_id
            JOIN historique_statut_commande hsc ON c.id = hsc.commande_id
            JOIN statut_commande sc ON hsc.statut_id = sc.id
            LEFT JOIN livraisons l ON c.id = l.commande_id
            WHERE sc.appellation = 'En attente' AND l.id IS NULL
            GROUP BY c.id, cl.prenom, cl.nom, c.cree_le
            ORDER BY c.cree_le DESC
        """)
        return [
            {
                'numero': row[0],
                'client_name': row[1],
                'date_heure': row[2],
                'nombre_repas': row[3]
            }
            for row in cursor.fetchall()
        ]

def AttributionLivraison(livreur_id, commande_id):
    """Attribue une livraison à un livreur."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO livraisons (livreur_id, commande_id, attribue_le)
            VALUES (%s, %s, NOW())
            RETURNING id
        """, [livreur_id, commande_id])
        return cursor.fetchone()[0]

def ModificationStatusLivraison(livraison_id, statut):
    """Met à jour le statut d'une livraison."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO historique_statut_livraison (livraison_id, statut_id, mis_a_jour_le)
            SELECT %s, id, NOW()
            FROM statut_livraison
            WHERE appellation = %s
        """, [livraison_id, statut])

def GetAllLivreurs():
    """Récupère tous les livreurs avec leurs informations."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                l.id,
                l.nom,
                l.contact,
                COALESCE(sl.appellation, 'N/A') AS statut,
                COALESCE(z.nom, 'Aucune') AS zone_nom
            FROM livreurs l
            LEFT JOIN (
                SELECT hsl.livreur_id, hsl.statut_id
                FROM historique_statut_livreur hsl
                INNER JOIN (
                    SELECT livreur_id, MAX(mis_a_jour_le) AS max_date
                    FROM historique_statut_livreur
                    GROUP BY livreur_id
                ) latest ON hsl.livreur_id = latest.livreur_id AND hsl.mis_a_jour_le = latest.max_date
            ) hsl ON l.id = hsl.livreur_id
            LEFT JOIN statut_livreur sl ON hsl.statut_id = sl.id
            LEFT JOIN zones_livreurs zl ON l.id = zl.livreur_id
            LEFT JOIN zones z ON zl.zone_id = z.id
            GROUP BY l.id, l.nom, l.contact, sl.appellation, z.nom
            ORDER BY l.nom
        """)
        return [
            {
                'id': row[0],
                'nom': row[1],
                'contact': row[2],
                'statut': row[3] or 'N/A',
                'zone_count': row[4]
            }
            for row in cursor.fetchall()
        ]

# ========== FONCTIONS DE VALIDATION ==========

def ValiderLivreurInput(nom, contact):
    """Valide les données d'entrée d'un livreur."""
    return bool(nom and contact)

def ValiderLivreurPosition(position):
    """Valide la position d'un livreur."""
    if not position:
        return True, None
    
    if not re.match(r'^-?\d+\.?\d*,-?\d+\.?\d*$', position):
        return False, "Position invalide. Utilisez le format 'latitude,longitude' (ex: -18.8792,47.5079)."
    
    return True, None

# ========== VUES PRINCIPALES ==========

def create_livreur(request):
    """Create a new livreur and associated records."""
    if request.method == 'POST':
        return CreateLivreurPost(request)
    return CreateLivreurGet(request)

def CreateLivreurPost(request):
    """Traite la création d'un livreur (POST)."""
    nom = request.POST.get('nom')
    contact = request.POST.get('contact')
    position = request.POST.get('position')
    zones = request.POST.getlist('zones')
    statut = request.POST.get('statut', 'Disponible')

    # Validation
    if not ValiderLivreurInput(nom, contact):
        messages.error(request, "Nom et contact sont requis.")
        return redirect('create_livreur')

    # Parse position
    position_wkt = f"POINT({position.replace(',', ' ')})" if position else None

    # Insertion en base
    livreur_id = InsertLivreur(nom, contact, position_wkt)
    InsertLivreurStatus(livreur_id, statut)
    InsertLivreurZones(livreur_id, zones)

    messages.success(request, f"Livreur {nom} créé avec succès.")
    return redirect('livreur_list')

def CreateLivreurGet(request):
    """Traite l'affichage du formulaire de création (GET)."""
    zones = GetZones()
    statuses = GetStatuses()
    context = {'zones': zones, 'statuses': statuses}
    return render(request, 'backoffice/livreur_ajout.html', context)

def update_livreur(request, livreur_id):
    """Met à jour les détails d'un livreur avec validation et confirmation."""
    livreur = GetLivreurDetails(livreur_id)
    if not livreur:
        messages.error(request, "Livreur introuvable.")
        return redirect('livreur_list')

    if request.method == 'POST':
        return ModifierLivreurPost(request, livreur_id)
    return ModifierLivreurGet(request, livreur_id, livreur)

def ModifierLivreurPost(request, livreur_id):
    """Traite la mise à jour d'un livreur (POST)."""
    nom = request.POST.get('nom')
    contact = request.POST.get('contact')
    position = request.POST.get('position')
    zones = request.POST.getlist('zones')
    statut = request.POST.get('statut')

    # Validation
    if not ValiderLivreurInput(nom, contact):
        messages.error(request, "Nom et contact sont requis.")
        return redirect('update_livreur', livreur_id=livreur_id)

    # Validation de la position
    is_valid, error_msg = ValiderLivreurPosition(position)
    if not is_valid:
        messages.error(request, error_msg)
        return redirect('update_livreur', livreur_id=livreur_id)

    position_wkt = ValiderPosition(position)

    # Mise à jour en base
    UpdateLivreurDetails(livreur_id, nom, contact, position_wkt)
    InsertLivreurStatus(livreur_id, statut)
    DeleteLivreurZones(livreur_id)
    InsertLivreurZones(livreur_id, zones)

    messages.success(request, f"Livreur {nom} mis à jour avec succès.")
    return redirect('livreur_list')

def ModifierLivreurGet(request, livreur_id, livreur):
    """Traite l'affichage du formulaire de mise à jour (GET)."""
    current_zones = GetLivreurZones(livreur_id)
    current_statut = GetLivreurStatus(livreur_id)
    zones = GetZones()
    statuses = GetStatuses()

    context = {
        'livreur_id': livreur_id,
        'nom': livreur[0],
        'contact': livreur[1],
        'position': FormatPositionToWKT(livreur[2]),
        'current_zones': current_zones,
        'current_statut': current_statut,
        'zones': zones,
        'statuses': statuses
    }
    return render(request, 'backoffice/livreur_modifier.html', context)

def delete_livreur(request, livreur_id):
    """Change le statut du livreur à 'Indisponible' et enregistre dans l'historique."""
    # Vérifier les livraisons actives
    active_deliveries = CheckLivraison(livreur_id)
    if active_deliveries > 0:
        messages.error(request, "Impossible de rendre le livreur indisponible : il a des livraisons en cours.")
        return redirect('livreur_list')

    livreur = GetLivreurDetails(livreur_id)
    if not livreur:
        messages.error(request, "Livreur introuvable.")
        return redirect('livreur_list')

    if request.method == 'POST':
        return DeleteLivreurPost(request, livreur_id, livreur)
    
    context = {'livreur_id': livreur_id, 'nom': livreur[0]}
    return render(request, 'backoffice/livreur_supprimer.html', context)

def DeleteLivreurPost(request, livreur_id, livreur):
    """Traite la suppression d'un livreur (POST)."""
    InsertLivreurStatus(livreur_id, 'Indisponible')
    messages.success(request, f"Le livreur {livreur[0]} est maintenant indisponible.")
    return redirect('livreur_list')

def livreur_details(request, livreur_id):
    """Affiche les détails du livreur et son historique de livraisons avec filtres."""
    livreur = GetLivreurDetails(livreur_id)
    if not livreur:
        messages.error(request, "Livreur introuvable.")
        return redirect('livreur_list')

    deliveries = GetHistoriqueLivraison(livreur_id)
    position = FormatPositionToLatLon(livreur[2])

    context = {
        'livreur_id': livreur_id,
        'nom': livreur[0],
        'contact': livreur[1],
        'position': position,
        'deliveries': deliveries
    }
    return render(request, 'backoffice/livreur_details.html', context)

def assign_order(request, livreur_id):
    """Attribue une commande à un livreur s'il est disponible et met à jour son statut en 'En livraison'."""
    # Vérifier le statut du livreur
    status = GetLivreurStatus(livreur_id)
    if status != 'Disponible':
        messages.error(request, "Vous ne pouvez pas attribuer une commande : le livreur n'est pas disponible.")
        return redirect('livreur_list')

    livreur = GetLivreurDetails(livreur_id)
    if not livreur:
        messages.error(request, "Livreur introuvable.")
        return redirect('livreur_list')

    if request.method == 'POST':
        return AttributionCommandePost(request, livreur_id, livreur)
    
    orders = GetCommandeNonLivree()
    context = {
        'livreur_id': livreur_id,
        'nom': livreur[0],
        'orders': orders
    }
    return render(request, 'backoffice/livreur_attribution.html', context)

def AttributionCommandePost(request, livreur_id, livreur):
    """Traite l'attribution d'une commande (POST)."""
    commande_id = request.POST.get('commande_id')
    if not commande_id:
        messages.error(request, "Aucune commande sélectionnée.")
        return redirect('assign_order', livreur_id=livreur_id)

    # Attribution
    livraison_id = AttributionLivraison(livreur_id, commande_id)
    InsertLivreurStatus(livreur_id, 'En livraison')
    ModificationStatusLivraison(livraison_id, 'Attribué')

    messages.success(request, f"Commande attribuée au livreur {livreur[0]}.")
    return redirect('livreur_list')

def livreur_list(request):
    """List all livreurs with action links."""
    livreurs = GetAllLivreurs()
    context = {'livreurs': livreurs}
    return render(request, 'backoffice/livreur_list.html', context)