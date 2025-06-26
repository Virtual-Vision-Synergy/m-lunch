from django.shortcuts import render, redirect
from mlunch.core.Restaurant import Restaurant
from mlunch.core.Livreur import Livreur
from mlunch.core.Livraison import Livraison
from database import db
from datetime import datetime, timedelta
import json
from django.contrib import messages
import traceback
from django.http import JsonResponse
from mlunch.core.Zone import Zone

def index(request):
    return render(request, 'backoffice/index.html')

def restaurants_list(request):
    secteur = request.GET.get('secteur')
    horaire = request.GET.get('horaire')
    restaurants = Restaurant.list(secteur, horaire)
    secteurs = db.fetch_query("SELECT nom FROM zones")
    return render(request, 'backoffice/restaurants/restaurants_list.html', {
        'restaurants': restaurants,
        'secteurs': secteurs,
        'selected_secteur': secteur,
        'selected_horaire': horaire,
    })

def restaurant_detail(request, restaurant_id):
    restaurant = Restaurant.detail(restaurant_id)
    return render(request, 'backoffice/restaurants/restaurant_detail.html', {'restaurant': restaurant})

def restaurant_add(request):
    if request.method == 'POST':
        data = {
            'nom': request.POST.get('nom'),
            'secteur': request.POST.get('secteur'),
            'commission': request.POST.get('commission'),
            'horaire_debut': request.POST.get('horaire_debut'),
            'horaire_fin': request.POST.get('horaire_fin'),
            'statut': request.POST.get('statut'),
            'image': request.POST.get('image'),
        }
        Restaurant.add(data)
        return redirect('restaurants_list')
    secteurs = db.fetch_query("SELECT nom FROM zones")
    statuts = db.fetch_query("SELECT appellation FROM statut_restaurant")
    return render(request, 'backoffice/restaurants/restaurant_form.html', {
        'secteurs': secteurs,
        'statuts': statuts,
        'action': 'Ajouter'
    })

def restaurant_edit(request, restaurant_id):
    restaurant = Restaurant.detail(restaurant_id)
    secteurs = db.fetch_query("SELECT nom FROM zones")
    statuts = db.fetch_query("SELECT appellation FROM statut_restaurant")
    if request.method == 'POST':
        data = {
            'nom': request.POST.get('nom'),
            'secteur': request.POST.get('secteur'),
            'commission': request.POST.get('commission'),
            'horaire_debut': request.POST.get('horaire_debut'),
            'horaire_fin': request.POST.get('horaire_fin'),
            'statut': request.POST.get('statut'),
            'image': request.POST.get('image'),
        }
        Restaurant.edit(restaurant_id, data)
        return redirect('restaurants_list')
    return render(request, 'backoffice/restaurants/restaurant_form.html', {
        'restaurant': restaurant,
        'secteurs': secteurs,
        'statuts': statuts,
        'action': 'Modifier'
    })

def restaurant_delete(request, restaurant_id):
    if not Restaurant.can_delete(restaurant_id):
        return render(request, 'backoffice/restaurants/restaurant_delete_error.html', {
            'reason': "Impossible de supprimer ce restaurant : il existe des commandes en cours."
        })
    if Restaurant.is_closed(restaurant_id):
        return redirect('restaurants_list')
    if request.method == 'POST':
        success = Restaurant.close(restaurant_id)
        if success:
            from django.contrib import messages
            messages.success(request, "Le restaurant a ete ferme avec succès.")
        return redirect('restaurants_list')
    return render(request, 'backoffice/restaurants/restaurant_delete_confirm.html', {
        'restaurant_id': restaurant_id
    })

def restaurant_orders(request, restaurant_id):
    commandes = Restaurant.orders(restaurant_id)
    return render(request, 'backoffice/restaurants/restaurant_orders.html', {
        'commandes': commandes
    })

def restaurant_financial(request, restaurant_id):
    periode = request.GET.get('periode', 'today')
    date_from = None
    date_to = None
    now = datetime.now()

    if periode == 'today':
        date_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
        date_to = now
    elif periode == 'month':
        date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        date_to = now
    elif periode == 'year':
        date_from = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        date_to = now
    elif periode == 'custom':
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        if date_from:
            date_from = datetime.strptime(date_from, "%Y-%m-%d")
        if date_to:
            date_to = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
        else:
            date_to = now
    else:
        date_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
        date_to = now

    result = Restaurant.financial(restaurant_id, date_from, date_to)
    graph_labels, graph_values = Restaurant.financial_graph(restaurant_id, date_from, date_to, periode)

    periode_label = {
        'today': "Aujourd'hui",
        'month': "Ce mois",
        'year': "Cette annee",
        'custom': "Periode personnalisee"
    }.get(periode, "Aujourd'hui")

    return render(request, 'backoffice/restaurants/restaurant_financial.html', {
        'restaurant': result['restaurant'],
        'total_brut': result['total_brut'],
        'commission_percent': result['commission_percent'],
        'commission_montant': result['commission_montant'],
        'total_frais': result['total_frais'],
        'benefice_net': result['benefice_net'],
        'nb_commandes': result['nb_commandes'],
        'periode': periode,
        'periode_label': periode_label,
        'date_from': date_from.strftime("%Y-%m-%d") if isinstance(date_from, datetime) else '',
        'date_to': (date_to - timedelta(days=1)).strftime("%Y-%m-%d") if isinstance(date_to, datetime) else '',
        'graph_labels': json.dumps(graph_labels),
        'graph_values': json.dumps(graph_values),
    })

def livreurs_list(request):
    secteur = request.GET.get('secteur')
    statut = request.GET.get('statut')
    livreurs = Livreur.list(secteur, statut)
    secteurs = db.fetch_query("SELECT nom FROM zones")
    statuts = db.fetch_query("SELECT appellation FROM statut_livreur")
    return render(request, 'backoffice/livreurs/livreurs_list.html', {
        'livreurs': livreurs,
        'secteurs': secteurs,
        'statuts': statuts,
        'selected_secteur': secteur,
        'selected_statut': statut,
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
            'photo': request.POST.get('photo'),
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
            'photo': request.POST.get('photo'),
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
