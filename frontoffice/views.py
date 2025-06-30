from django.shortcuts import render, redirect
from mlunch.core.Commande import Commande
from mlunch.core.Livraison import Livraison
from database import db
from django.contrib.auth import logout
from django.contrib import messages

from django.shortcuts import render, redirect
from django.http import JsonResponse

import json
from django.views.decorators.csrf import csrf_exempt
from mlunch.core.services import ClientService, ZoneService
from mlunch.core.models import Zone, Client, ZoneClient  # Import du modèle de liaison
from shapely import wkt

def index(request):
    return render(request, 'frontoffice/index.html')

def panier(request):
    # Récupère la liste des zones pour la liste déroulante
    zones = db.fetch_query("SELECT id, nom FROM zones")
    # Ici, tu peux aussi récupérer le contenu du panier si besoin
    return render(request, "frontoffice/panier.html", {
        "zones": zones,
    })

def valider_panier(request):
    if request.method == "POST":
        mode_paiement = request.POST.get("mode_paiement")
        zone_id = int(request.POST.get("zone_id"))  # zone_id = point_recup_id si tu utilises la même logique
        user_id = request.user.id

        # 1. Récupérer la commande en cours
        commande_id = Commande.get_commande_en_cours(user_id)
        if not commande_id:
            return render(request, "frontoffice/panier.html", {
                "zones": db.fetch_query("SELECT id, nom FROM zones"),
                "error": "Aucune commande en cours à valider."
            })

        # 2. Mettre à jour le statut de la commande
        statut_en_cours = db.fetch_one("SELECT id FROM statut_commande WHERE appellation='En cours'")
        if not statut_en_cours:
            return render(request, "frontoffice/panier.html", {
                "zones": db.fetch_query("SELECT id, nom FROM zones"),
                "error": "Statut de commande 'En cours' introuvable."
            })

        # 3. Créer la commande avec le point de récupération
        Commande.create(user_id, zone_id, statut_en_cours['id'])

        # 4. Choisir un livreur pour la zone
        livreur_id = Commande.choisir_livreur(zone_id)
        if not livreur_id:
            return render(request, "frontoffice/panier.html", {
                "zones": db.fetch_query("SELECT id, nom FROM zones"),
                "error": "Aucun livreur disponible pour cette zone."
            })

        # 5. Créer la livraison avec le statut "En attente"
        statut_livraison = db.fetch_one("SELECT id FROM statut_livraison WHERE appellation='En attente'")
        if not statut_livraison:
            return render(request, "frontoffice/panier.html", {
                "zones": db.fetch_query("SELECT id, nom FROM zones"),
                "error": "Statut de livraison 'En attente' introuvable."
            })
        Livraison.create(livreur_id, commande_id, statut_livraison['id'])

        # 6. Vider le panier
        Commande.vider_panier(commande_id)

        return render(request, "frontoffice/panier.html", {
            "zones": db.fetch_query("SELECT id, nom FROM zones"),
            "message": "Votre commande a été validée avec succès !"
        })
    else:
        return redirect("panier")
    
def user_logout(request):
    """Déconnecte l'utilisateur et redirige vers la page de connexion"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('login')  # Remplacer par votre URL de page de login


@csrf_exempt  # Adding this to allow testing without CSRF
def inscription_page(request):
    # Initialize error variable to None
    error = None

    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        mot_de_passe = request.POST.get('mot_de_passe')
        telephone = request.POST.get('telephone')
        secteur_nom = request.POST.get('secteur')

        # Vérifier que tous les champs sont remplis
        if not all([nom, prenom, email, mot_de_passe, telephone]):
            error = "Tous les champs sont obligatoires."
        # Vérifier que le secteur est fourni
        elif not secteur_nom:
            error = "Veuillez sélectionner un secteur en cliquant sur la carte."
        else:
            # 1. Insérer client via ORM
            result = ClientService.create_client(email, mot_de_passe, contact=telephone, prenom=prenom, nom=nom)
            if 'error' in result:
                error = result['error']
            else:
                client_id = result['client']['id']

                # 2. Vérifier que la zone existe et récupérer son instance
                try:
                    zone = Zone.objects.get(nom=secteur_nom)
                except Zone.DoesNotExist:
                    error = f"Secteur '{secteur_nom}' introuvable."
                else:
                    # 3. Lier client/zone via ZoneClient
                    try:
                        client = Client.objects.get(id=client_id)
                        ZoneClient.objects.create(client=client, zone=zone)
                        # Si tout s'est bien passé, rediriger vers la page d'accueil
                        return redirect('frontoffice_index')
                    except Exception as e:
                        error = f"Erreur lors de l'insertion dans zones_clients: {e}"

    # Préparer les données des zones pour l'affichage de la carte
    zones = Zone.objects.all()
    zones_features = []
    for z in zones:
        try:
            geom = wkt.loads(z.zone)
            zones_features.append({
                'type': 'Feature',
                'geometry': json.loads(geom.to_geojson()),
                'properties': {'id': z.id, 'nom': z.nom}
            })
        except Exception:
            continue

    # Retourner le template avec les zones et l'erreur si elle existe
    return render(request, 'frontoffice/inscription.html', {
        'zones': zones_features,
        'erreur': error
    })

def api_zone_from_coord(request):
    try:
        lat = float(request.GET.get('lat'))
        lon = float(request.GET.get('lon'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Coordonnées invalides'})

    zone = ZoneService.get_zone_by_coord(lat, lon)
    if zone:
        return JsonResponse({'success': True, 'nom': zone['nom'], 'zone_id': zone['id']})
    else:
        return JsonResponse({'success': False})


def deconnexion(request):
    request.session.flush()  # Supprimer toutes les données de session
    return redirect('frontoffice_index') 
