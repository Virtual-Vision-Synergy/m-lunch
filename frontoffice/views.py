from django.shortcuts import render, redirect
from mlunch.core.Inscription import Inscription
from mlunch.core.RechercheResto import RechercheResto
from database.db import fetch_query
from django.http import JsonResponse
from mlunch.core.Commande import Commande
from django.contrib import messages
import json
from mlunch.core.Panier import Panier
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

def index(request):
    return render(request, 'frontoffice/index.html')

def inscription_page(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        mot_de_passe = request.POST.get('mot_de_passe')
        telephone = request.POST.get('telephone')
        secteur_nom = request.POST.get('secteur')

        # Vérifier que le secteur est fourni
        if not secteur_nom:
            return render(request, 'frontoffice/inscription.html', {
                'erreur': "Veuillez sélectionner un secteur en cliquant sur la carte.",
                'zones': fetch_query("SELECT id, nom, ST_AsGeoJSON(zone) as geojson FROM zones")
            })

        # 1. Insérer client
        success = Inscription.inscrire(nom, prenom, email, mot_de_passe, telephone)
        if not success:
            return render(request, 'frontoffice/inscription.html', {
                'erreur': "Inscription échouée. Email peut-être déjà utilisé.",
                'zones': fetch_query("SELECT id, nom, ST_AsGeoJSON(zone) as geojson FROM zones")
            })

        # 2. Récupérer l'ID du client
        client_id = Inscription.getClientId(email)
        if not client_id:
            return render(request, 'frontoffice/inscription.html', {
                'erreur': "Erreur lors de la récupération de l'ID client.",
                'zones': fetch_query("SELECT id, nom, ST_AsGeoJSON(zone) as geojson FROM zones")
            })

        # 3. Vérifier que la zone existe et récupérer son ID
        zone_id = Inscription.getZoneId(secteur_nom)
        if not zone_id:
            return render(request, 'frontoffice/inscription.html', {
                'erreur': f"Secteur '{secteur_nom}' introuvable.",
                'zones': fetch_query("SELECT id, nom, ST_AsGeoJSON(zone) as geojson FROM zones")
            })

        # Affichage debug dans le terminal
        print(f"client_id = {client_id}")
        print(f"zone_id = {zone_id}")
        
        # 4. Lier client/zone dans zones_clients
        insertZone = Inscription.insertZoneClient(client_id, zone_id)
        if not insertZone:
            return render(request, 'frontoffice/inscription.html', {
                'erreur': "Erreur lors de l'insertion dans zones_clients.",
                'zones': fetch_query("SELECT id, nom, ST_AsGeoJSON(zone) as geojson FROM zones")
            })

        # Si tout s'est bien passé, rediriger vers la page d'accueil
        return redirect('frontoffice_index')

    # GET: afficher carte et zones
    zones = fetch_query("SELECT id, nom, ST_AsGeoJSON(zone) as geojson FROM zones")
    return render(request, 'frontoffice/inscription.html', {'zones': zones})

def api_zone_from_coord(request):
    try:
        lat = float(request.GET.get('lat'))
        lon = float(request.GET.get('lon'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Coordonnées invalides'})

    zone = Inscription.getZone(lat, lon)
    if zone:
        return JsonResponse({'success': True, 'nom': zone['nom'], 'zone_id': zone['id']})
    else:
        return JsonResponse({'success': False})



def barre_recherche(request):
    """
    Vue pour la recherche de restaurants par secteur, nom ou adresse
    """
    restaurants = []
    secteur = ""
    nom = ""
    adresse = ""
    
    # Récupérer la zone de l'utilisateur connecté depuis la session ou la base de données
    user_zone = None

    # cliet a besoin de ce connecte
    if client:
        # Récupérer la zone du client depuis zones_clients
        user_zone_query = fetch_query("""
            SELECT z.nom 
            FROM zones z
            JOIN zones_clients zc ON z.id = zc.zone_id
            JOIN clients c ON c.id = zc.client_id
            WHERE c.email = %s
        """, [client.email])
        
        if user_zone_query:
            user_zone = user_zone_query[0]['nom']
    
    if request.method == 'POST':
        secteur = request.POST.get('secteur', '').strip()
        nom = request.POST.get('nom', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        
        # Rechercher les restaurants
        if secteur or nom or adresse:
            if adresse:
                restaurants = RechercheResto.getRestaurantByAddress(adresse)
            else:
                restaurants = RechercheResto.getRestaurantBySecteurOuNom(
                    secteur=secteur if secteur else None,
                    nom=nom if nom else None
                )
        else:
            # Si aucun critère, afficher tous les restaurants
            restaurants = RechercheResto.getRestaurantBySecteurOuNom()
    
    elif request.method == 'GET':
        # Pour les requêtes AJAX ou paramètres GET
        secteur = request.GET.get('secteur', '').strip()
        nom = request.GET.get('nom', '').strip()
        adresse = request.GET.get('adresse', '').strip()
        
        if secteur or nom or adresse:
            if adresse:
                restaurants = RechercheResto.getRestaurantByAddress(adresse)
            else:
                restaurants = RechercheResto.getRestaurantBySecteurOuNom(
                    secteur=secteur if secteur else None,
                    nom=nom if nom else None
                )
        
        # Si c'est une requête AJAX, retourner du JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Ajouter l'information de disponibilité dans la zone utilisateur
            restaurants_with_availability = []
            for resto in restaurants:
                resto_dict = dict(resto) if hasattr(resto, 'keys') else resto._asdict() if hasattr(resto, '_asdict') else dict(zip(['id', 'nom', 'adresse', 'image', 'longitude', 'latitude', 'note_moyenne', 'zone_nom'], resto))
                resto_dict['available_in_user_zone'] = (
                    resto_dict.get('zone_nom') == user_zone if user_zone else True
                )
                restaurants_with_availability.append(resto_dict)
            
            return JsonResponse({
                'success': True,
                'restaurants': restaurants_with_availability,
                'count': len(restaurants) if restaurants else 0,
                'user_zone': user_zone
            })
    
    # Ajouter l'information de disponibilité pour l'affichage
    if restaurants:
        restaurants_with_availability = []
        for resto in restaurants:
            resto_dict = dict(resto) if hasattr(resto, 'keys') else resto._asdict() if hasattr(resto, '_asdict') else dict(zip(['id', 'nom', 'adresse', 'image', 'longitude', 'latitude', 'note_moyenne', 'zone_nom'], resto))
            resto_dict['available_in_user_zone'] = (
                resto_dict.get('zone_nom') == user_zone if user_zone else True
            )
            restaurants_with_availability.append(resto_dict)
        restaurants = restaurants_with_availability
    
    # Récupérer toutes les zones pour le dropdown
    zones = fetch_query("SELECT nom FROM zones ORDER BY nom")
    
    context = {
        'restaurants': restaurants,
        'zones': zones,
        'secteur_recherche': secteur,
        'nom_recherche': nom,
        'adresse_recherche': adresse,
        'nb_resultats': len(restaurants) if restaurants else 0,
        'user_zone': user_zone
    }
    
    return render(request, 'frontoffice/barre_recherche.html', context)

def deconnexion(request):
    request.session.flush()  # Supprimer toutes les données de session
    return redirect('frontoffice_index') 



def historique_commandes(request):
    return render(request, 'frontoffice/historique_commandes.html')


def commandes_en_cours(request):
    """
    Vue pour afficher les commandes en cours du client connecté
    """
    # Récupérer l'ID du client s'il se connecte
    #client_id = Commande.getClientIdFromEmail(client.email)
    client_id = 16 # test fotsiny ilay id = 16
    #if not client_id:
        #messages.error(request, "Impossible de récupérer vos informations client.")
        #return redirect('frontoffice_index')
    
    # Récupérer les commandes en cours
    commandes = Commande.getCommandesEnCours(client_id)
    
    # Ajouter le statut et les informations supplémentaires pour chaque commande
    commandes_enrichies = []
    for commande in commandes:
        commande_dict = dict(commande)
        commande_dict['statut'] = Commande.getStatutCommande(commande['id'])
        commande_dict['peut_annuler'] = Commande.peutAnnulerCommande(commande['id'])
        commande_dict['temps_estime'] = Commande.getTempsEstimeLivraison(commande['id'])
        commandes_enrichies.append(commande_dict)
    
    context = {
        'commandes': commandes_enrichies,
        'nb_commandes': len(commandes_enrichies)
    }
    
    return render(request, 'frontoffice/commandes_en_cours.html', context)
def detail_commande(request, commande_id):
    """
    Vue pour afficher le détail d'une commande spécifique
    """
    # Récupérer l'ID du client
    client_id = Commande.getClientIdFromEmail(client.email)
    
    if not client_id:
        messages.error(request, "Impossible de récupérer vos informations client.")
        return redirect('frontoffice_index')
    
    # Récupérer les détails de la commande
    detail = Commande.getDetailCommande(commande_id, client_id)
    
    if not detail:
        messages.error(request, "Commande introuvable.")
        return redirect('commandes_en_cours')
    
    # Enrichir avec les informations supplémentaires
    detail['commande']['statut'] = Commande.getStatutCommande(commande_id)
    detail['commande']['peut_annuler'] = Commande.peutAnnulerCommande(commande_id)
    detail['commande']['temps_estime'] = Commande.getTempsEstimeLivraison(commande_id)
    
    return render(request, 'frontoffice/detail_commande.html', detail)
def annuler_commande(request, commande_id):
    """
    Vue pour annuler une commande
    """
    if request.method == 'POST':
        # Récupérer l'ID du client
        client_id = Commande.getClientIdFromEmail(client.email)
        
        if not client_id:
            return JsonResponse({
                'success': False, 
                'message': "Impossible de récupérer vos informations client."
            })
        
        # Tenter l'annulation
        success, message = Commande.annulerCommande(commande_id, client_id)
        
        return JsonResponse({
            'success': success,
            'message': message
        })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})


def panier_view(request):
    """
    Vue principale du panier
    """
    
    #client_id = client.id #recuperer s'il est connecte
    client_id = 1 # test fotsiny ilay id = 1
    # Récupérer les articles du panier
    items = Panier.get_panier_items(client_id)
    
    # Calculer les totaux
    totals = Panier.calculate_totals(client_id)
    
    # Récupérer les points de récupération
    points_recuperation = Panier.get_points_recuperation()
    
    context = {
        'items': items,
        'totals': totals,
        'points_recuperation': points_recuperation,
    }
    print("PANIER:", items)

    
    return render(request, 'frontoffice/panier.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def add_to_panier(request):
    """
    Ajouter un article au panier via AJAX
    """
    try:
        data = json.loads(request.body)
        repas_id = data.get('repas_id')
        quantite = data.get('quantite', 1)
        client_id = client.id
        
        # Vérifier la disponibilité
        if not Panier.check_disponibilite_repas(repas_id):
            return JsonResponse({
                'success': False, 
                'message': 'Ce repas n\'est plus disponible'
            })
        
        # Ajouter au panier
        success = Panier.add_to_panier(client_id, repas_id, quantite)
        
        if success:
            # Récalculer les totaux
            totals = Panier.calculate_totals(client_id)
            return JsonResponse({
                'success': True,
                'message': 'Article ajouté au panier',
                'totals': totals
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de l\'ajout au panier'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def update_quantity(request):
    """
    Mettre à jour la quantité d'un article
    """
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        nouvelle_quantite = data.get('quantite')
        
        success = Panier.update_quantity(item_id, nouvelle_quantite)
        
        if success:
            client_id = client.id
            totals = Panier.calculate_totals(client_id)
            return JsonResponse({
                'success': True,
                'message': 'Quantité mise à jour',
                'totals': totals
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la mise à jour'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def remove_from_panier(request):
    """
    Supprimer un article du panier
    """
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        success = Panier.remove_from_panier(item_id)
        
        if success:
            client_id = client.id
            totals = Panier.calculate_totals(client_id)
            return JsonResponse({
                'success': True,
                'message': 'Article supprimé',
                'totals': totals
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la suppression'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def clear_panier(request):
    """
    Vider complètement le panier
    """
    try:
        client_id = client.id
        success = Panier.clear_panier(client_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Panier vidé avec succès'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors du vidage du panier'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def validate_commande(request):
    """
    Valider la commande et procéder au paiement
    """
    try:
        data = json.loads(request.body)
        point_recup_id = data.get('point_recup_id')
        mode_paiement = data.get('mode_paiement')
        client_id = client.id
        
        # Vérifier que le panier n'est pas vide
        totals = Panier.calculate_totals(client_id)
        if totals['nombre_articles'] == 0:
            return JsonResponse({
                'success': False,
                'message': 'Votre panier est vide'
            })
        
        # Valider la commande
        success, message = Panier.validate_commande(client_id, point_recup_id, mode_paiement)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': message,
                'redirect_url': '/commandes/confirmation/'  # Page de confirmation
            })
        else:
            return JsonResponse({
                'success': False,
                'message': message
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

def get_panier_count(request):
    """
    Récupérer le nombre d'articles dans le panier (pour le badge)
    """
    try:
        client_id = client.id
        totals = Panier.calculate_totals(client_id)
        
        return JsonResponse({
            'count': totals['quantite_totale']
        })
        
    except Exception as e:
        return JsonResponse({
            'count': 0
        })

# Vue pour les invités (optionnel)
def panier_guest_view(request):
    """
    Vue panier pour les invités (utilise les sessions)
    """
    # Implémenter la logique de session pour les invités
    # Pour l'instant, rediriger vers la connexion
    return redirect('login')

def checkout_view(request):
    """
    Page de checkout/validation
    """
    client_id = client.id
    items = Panier.get_panier_items(client_id=client_id)
    totals = Panier.calculate_totals(client_id)
    points_recuperation = Panier.get_points_recuperation()
    
    if totals['nombre_articles'] == 0:
        return redirect('panier')
    
    context = {
        'items': items,
        'totals': totals,
        'points_recuperation': points_recuperation,
    }
    
    return render(request, 'panier/checkout.html', context)
