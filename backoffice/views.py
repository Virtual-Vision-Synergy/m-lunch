from django.shortcuts import render
from mlunch.core.services import CommandeService
from mlunch.core.services import RestaurantService  
from mlunch.core.services import ZoneService


def index(request):
    commandes_en_attente = CommandeService.get_commandes_en_attente()
    return render(request, 'backoffice/index.html', {'commandes_en_attente': commandes_en_attente})

def restaurant(request):
    zone_id = request.GET.get('zone')
    statut_id = request.GET.get('statut')
    if zone_id or statut_id:
        restaurants = RestaurantService.list_restaurant_filtrer(zone_id, statut_id)
    else:
        restaurants = RestaurantService.list_restaurants_all_details()
    zones = ZoneService.get_all_zones()
    statuts = RestaurantService.get_all_statuts()
    selected_zone = int(zone_id) if zone_id else None
    selected_statut = int(statut_id) if statut_id else None
    return render(request, 'backoffice/restaurant.html', {
        'restaurants': restaurants,
        'zones': zones,
        'statuts': statuts,
        'selected_zone': selected_zone,
        'selected_statut': selected_statut
    })

def livreur_detail(request, livreur_id):
    livreur = Livreur.detail(livreur_id)
    return render(request, 'backoffice/livreurs/livreur_detail.html', {'livreur': livreur})

def livreur_add(request):
    if request.method == 'POST':
        data = {
            'nom': request.POST.get('nom'),
            'contact': request.POST.get('contact'),
            'secteur': request.POST.get('secteur'),
            'statut': request.POST.get('statut'),
            # 'photo': request.POST.get('photo'),  # À SUPPRIMER
        }
        Livreur.add(data)
        return redirect('livreurs_list')
    secteurs = db.fetch_query("SELECT nom FROM zones")
    statuts = db.fetch_query("SELECT appellation FROM statut_livreur")
    return render(request, 'backoffice/livreurs/livreur_form.html', {
        'secteurs': secteurs,
        'statuts': statuts,
        'action': 'Ajouter'
    })

def livreur_edit(request, livreur_id):
    livreur = Livreur.detail(livreur_id)
    secteurs = db.fetch_query("SELECT nom FROM zones")
    statuts = db.fetch_query("SELECT appellation FROM statut_livreur")
    
    if request.method == 'POST':
        data = {
            'nom': request.POST.get('nom'),
            'contact': request.POST.get('contact'),
            'secteur': request.POST.get('secteur'),
            'statut': request.POST.get('statut'),
            # 'photo': request.POST.get('photo'),  # À SUPPRIMER
        }
        
        # Si c'est une requête AJAX, on renvoie les changements
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            changements = []
            
            # Verifier les changements de nom
            if livreur['nom'] != data['nom']:
                changements.append({
                    'champ': 'Nom',
                    'avant': livreur['nom'],
                    'apres': data['nom']
                })
                
            # Verifier les changements de contact
            if livreur['contact'] != data['contact']:
                changements.append({
                    'champ': 'Contact',
                    'avant': livreur['contact'] or 'Non defini',
                    'apres': data['contact'] or 'Non defini'
                })
                
            # Verifier les changements de secteur
            if livreur['secteur'] != data['secteur']:
                changements.append({
                    'champ': 'Secteur',
                    'avant': livreur['secteur'] or 'Non defini',
                    'apres': data['secteur']
                })
                
            # Verifier les changements de statut
            if livreur['statut'] != data['statut']:
                changements.append({
                    'champ': 'Statut',
                    'avant': livreur['statut'] or 'Non defini',
                    'apres': data['statut']
                })
                
            # Verifier les changements de photo
            before_photo = livreur.get('photo', None)
            if before_photo != data['photo']:
                changements.append({
                    'champ': 'Photo',
                    'avant': before_photo or 'Non definie',
                    'apres': data['photo'] or 'Non definie'
                })
                
            return JsonResponse({'changements': changements})
        
        # Si confirm=1, on effectue les modifications
        if request.POST.get('confirm') == '1':
            Livreur.edit(livreur_id, data)
            return redirect('livreurs_list')
            
    return render(request, 'backoffice/livreurs/livreur_form.html', {
        'livreur': livreur,
        'secteurs': secteurs,
        'statuts': statuts,
        'action': 'Modifier'
    })

def livreur_delete(request, livreur_id):
    if not Livreur.can_delete(livreur_id):
        return render(request, 'backoffice/livreurs/livreur_delete_error.html', {
            'reason': "Impossible de supprimer ce livreur : il a des livraisons en cours."
        })
    if Livreur.is_inactive(livreur_id):
        return redirect('livreurs_list')
    if request.method == 'POST':
        Livreur.deactivate(livreur_id)
        return redirect('livreurs_list')
    return render(request, 'backoffice/livreurs/livreur_delete_confirm.html', {
        'livreur_id': livreur_id
    })

def livraisons_list(request):
    # Recuperer les filtres
    secteur = request.GET.get('secteur')
    statut = request.GET.get('statut')
    adresse = request.GET.get('adresse')
    livreur_id = request.GET.get('livreur')
    
    # Recuperer les livraisons filtrees
    livraisons = Livraison.list(secteur=secteur, statut=statut, adresse=adresse, livreur_id=livreur_id)
    
    # Recuperer les donnees pour les filtres
    secteurs = db.fetch_query("SELECT nom FROM zones")
    statuts = db.fetch_query("SELECT appellation FROM statut_livraison")
    livreurs = db.fetch_query("SELECT id, nom FROM livreurs")
    
    return render(request, 'backoffice/livraisons/livraisons_list.html', {
        'livraisons': livraisons,
        'secteurs': secteurs,
        'statuts': statuts,
        'livreurs': livreurs,
        'selected_secteur': secteur,
        'selected_statut': statut,
        'selected_adresse': adresse,
        'selected_livreur': livreur_id,
    })

def livraison_detail(request, livraison_id):
    livraison = Livraison.detail(livraison_id)
    return render(request, 'backoffice/livraisons/livraison_detail.html', {'livraison': livraison})

def livraison_edit(request, livraison_id):
    livraison = Livraison.detail(livraison_id)
    statuts = db.fetch_query("SELECT id, appellation FROM statut_livraison")
    livreurs = db.fetch_query("SELECT id, nom FROM livreurs")
    
    if request.method == 'POST':
        data = {
            'livreur_id': request.POST.get('livreur_id'),
            'statut': request.POST.get('statut'),
        }
        
        # Si c'est une requête AJAX, on renvoie les changements
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            changements = []
            
            # Verifier les changements de livreur
            old_livreur = db.fetch_one("SELECT nom FROM livreurs WHERE id=%s", (livraison['livreur_id'],))
            new_livreur = db.fetch_one("SELECT nom FROM livreurs WHERE id=%s", (data['livreur_id'],))
            
            if livraison['livreur_id'] != int(data['livreur_id']):
                changements.append({
                    'champ': 'Livreur',
                    'avant': old_livreur['nom'] if old_livreur else 'Non defini',
                    'apres': new_livreur['nom'] if new_livreur else 'Non defini'
                })
                
            # Verifier les changements de statut
            if livraison['statut'] != data['statut']:
                changements.append({
                    'champ': 'Statut',
                    'avant': livraison['statut'] or 'Non defini',
                    'apres': data['statut']
                })
                
            return JsonResponse({'changements': changements})
        
        # Si confirm=1, on effectue les modifications
        if request.POST.get('confirm') == '1':
            statut_id = db.fetch_one("SELECT id FROM statut_livraison WHERE appellation=%s", (data['statut'],))
            if statut_id:
                Livraison.update_status(livraison_id, statut_id['id'])
            
            if livraison['livreur_id'] != int(data['livreur_id']):
                Livraison.update_livreur(livraison_id, int(data['livreur_id']))
                
            return redirect('livraisons_list')
            
    return render(request, 'backoffice/livraisons/livraison_form.html', {
        'livraison': livraison,
        'statuts': statuts,
        'livreurs': livreurs,
        'action': 'Modifier'
    })

def livraison_delete(request, livraison_id):
    from django.contrib import messages
    import traceback
    
    try:
        livraison_id = int(livraison_id)  # S'assurer que l'ID est bien un int
        
        livraison = Livraison.detail(livraison_id)
        if not livraison:
            messages.error(request, f"La livraison avec l'ID {livraison_id} n'existe pas.")
            return redirect('livraisons_list')
        
        # Verifier si la livraison peut être annulee
        if livraison['statut'] == 'Livree' or livraison['statut'] == 'Livree':
            return render(request, 'backoffice/livraisons/livraison_delete_error.html', {
                'reason': "Impossible d'annuler une livraison dejà effectuee."
            })
        
        if livraison['statut'] == 'Annulee' or livraison['statut'] == 'Annulee':
            messages.info(request, "Cette livraison est dejà annulee.")
            return redirect('livraisons_list')
        
        if request.method == 'POST':
            # Recuperer l'ID du statut 'Annulee'
            statut_annule = db.fetch_one("SELECT id FROM statut_livraison WHERE appellation = 'Annulee'")
            
            if not statut_annule:
                # Si le statut n'existe pas avec 'Annulee', essayer avec 'Annulee' (avec accent)
                statut_annule = db.fetch_one("SELECT id FROM statut_livraison WHERE appellation = 'Annulee'")
                
            if not statut_annule:
                # Si le statut n'existe toujours pas, le creer
                db.execute_query("INSERT INTO statut_livraison (appellation) VALUES ('Annulee')")
                statut_annule = db.fetch_one("SELECT id FROM statut_livraison WHERE appellation = 'Annulee'")
            
            if not statut_annule:
                messages.error(request, "Impossible de creer ou trouver le statut 'Annulee'.")
                return redirect('livraisons_list')
            
            print(f"Tentative d'annulation de la livraison {livraison_id} avec le statut ID {statut_annule['id']}")
            
            # Utiliser update_status pour changer le statut
            success = Livraison.update_status(livraison_id, statut_annule['id'])
            
            if success:
                # Verifier que le changement a bien ete applique
                updated_livraison = Livraison.detail(livraison_id)
                if updated_livraison and updated_livraison['statut'] in ['Annulee', 'Annulee']:
                    messages.success(request, "La livraison a ete annulee avec succès.")
                else:
                    messages.warning(request, "La fonction a indique un succès mais le statut pourrait ne pas être mis à jour. Verifiez la liste des livraisons.")
            else:
                messages.error(request, "Un problème est survenu lors de l'annulation de la livraison.")
            
            # Afficher tous les statuts disponibles pour le debogage
            all_statuses = db.fetch_query("SELECT id, appellation FROM statut_livraison")
            print(f"Statuts disponibles: {all_statuses}")
            
            return redirect('livraisons_list')
            
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        traceback.print_exc()
        return redirect('livraisons_list')
        
    return render(request, 'backoffice/livraisons/livraison_delete_confirm.html', {
        'livraison': livraison
    })

def test_create_client(request):

        # Créer le client
        result = Zone.delete(1,2)
               
                        
               
        if 'error' in result:
            messages.error(request, result['error'])
        else:
            #messages.success(request, f"Client créé avec succès : {result['email']}")
            print(result)
        return render(request, 'backoffice/index.html')

def zones_list(request):
    zones = db.fetch_query("SELECT id, nom, description FROM zones")
    return render(request, 'backoffice/zones/zones_list.html', {'zones': zones})

def zone_add(request):
    error = None
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        zone_geom = request.POST.get('zone_geom')  # WKT format: POLYGON((...))
        statut_id = db.fetch_one("SELECT id FROM statut_zone WHERE appellation='Active'")
        if not statut_id:
            db.execute_query("INSERT INTO statut_zone (appellation) VALUES ('Active')")
            statut_id = db.fetch_one("SELECT id FROM statut_zone WHERE appellation='Active'")
        if not (nom and zone_geom and statut_id):
            error = "Tous les champs sont obligatoires."
        else:
            db.execute_query(
                "INSERT INTO zones (nom, description, zone) VALUES (%s, %s, ST_GeomFromText(%s, 4326))",
                (nom, description, zone_geom)
            )
            zone = db.fetch_one("SELECT id FROM zones WHERE nom=%s ORDER BY id DESC LIMIT 1", (nom,))
            db.execute_query(
                "INSERT INTO historique_statut_zone (zone_id, statut_id) VALUES (%s, %s)",
                (zone['id'], statut_id['id'])
            )
            return redirect('zones_list')
    return render(request, 'backoffice/zones/zone_form.html', {'action': 'Ajouter', 'error': error})

def zone_edit(request, zone_id):
    zone = db.fetch_one("SELECT id, nom, description, ST_AsText(zone) as zone FROM zones WHERE id=%s", (zone_id,))
    if not zone:
        return redirect('zones_list')
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        zone_geom = request.POST.get('zone_geom')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            changements = []
            if nom != zone['nom']:
                changements.append({'champ': 'Nom', 'avant': zone['nom'], 'apres': nom})
            if description != zone['description']:
                changements.append({'champ': 'Description', 'avant': zone['description'], 'apres': description})
            if zone_geom != zone['zone']:
                changements.append({'champ': 'Zone', 'avant': zone['zone'], 'apres': zone_geom})
            return JsonResponse({'changements': changements})
        if request.POST.get('confirm') == '1':
            db.execute_query(
                "UPDATE zones SET nom=%s, description=%s, zone=ST_GeomFromText(%s, 4326) WHERE id=%s",
                (nom, description, zone_geom, zone_id)
            )
            return redirect('zones_list')
    return render(request, 'backoffice/zones/zone_form.html', {'action': 'Modifier', 'zone': zone})



def zone_delete(request, zone_id):
    zone = db.fetch_one("SELECT id, nom FROM zones WHERE id=%s", (zone_id,))
    if not zone:
        return redirect('zones_list')
    # Verifier dependances (restaurants actifs dans la zone)
    restaurants = db.fetch_query("""
        SELECT r.nom FROM restaurants r
        JOIN zones_restaurant zr ON zr.restaurant_id = r.id
        WHERE zr.zone_id = %s
        AND EXISTS (
            SELECT 1 FROM historique_statut_restaurant hsr
            JOIN statut_restaurant sr ON hsr.statut_id = sr.id
            WHERE hsr.restaurant_id = r.id AND sr.appellation = 'Ouvert'
        )
    """, (zone_id,))
    if restaurants:
        reason = "Suppression impossible : des restaurants actifs sont associes à cette zone (" + ", ".join([r['nom'] for r in restaurants]) + ")."
        return render(request, 'backoffice/zones/zone_delete_error.html', {'reason': reason})
    if request.method == 'POST':
        # Mettre le statut à "Supprimee"
        statut_suppr = db.fetch_one("SELECT id FROM statut_zone WHERE appellation='Supprimee'")
        if not statut_suppr:
            db.execute_query("INSERT INTO statut_zone (appellation) VALUES ('Supprimee')")
            statut_suppr = db.fetch_one("SELECT id FROM statut_zone WHERE appellation='Supprimee'")
        db.execute_query(
            "INSERT INTO historique_statut_zone (zone_id, statut_id) VALUES (%s, %s)",
            (zone_id, statut_suppr['id'])
        )
        return redirect('zones_list')
    return render(request, 'backoffice/zones/zone_delete_confirm.html', {'zone': zone})

# modif kely
def commande(request):
    commandes = CommandeService.get_all_commandes()
    return render(request, 'backoffice/commande.html', {'commandes': commandes})
