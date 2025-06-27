from django.shortcuts import render, redirect
from mlunch.core.Commande import Commande
from mlunch.core.Livraison import Livraison
from database import db
from django.contrib.auth import logout
from django.contrib import messages


def index(request):
    return render(request, 'frontoffice/index.html')

def user_logout(request):
    """Déconnecte l'utilisateur et redirige vers la page de connexion"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('login')  # Remplacer par votre URL de page de login

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
        zone_id = int(request.POST.get("zone_id"))
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
        Commande.update(commande_id, statut_en_cours['id'])

        # 3. Choisir un livreur pour la zone
        livreur_id = Commande.choisir_livreur(zone_id)
        if not livreur_id:
            return render(request, "frontoffice/panier.html", {
                "zones": db.fetch_query("SELECT id, nom FROM zones"),
                "error": "Aucun livreur disponible pour cette zone."
            })

        # 4. Créer la livraison avec le statut "En attente"
        statut_livraison = db.fetch_one("SELECT id FROM statut_livraison WHERE appellation='En attente'")
        if not statut_livraison:
            return render(request, "frontoffice/panier.html", {
                "zones": db.fetch_query("SELECT id, nom FROM zones"),
                "error": "Statut de livraison 'En attente' introuvable."
            })
        Livraison.create(livreur_id, commande_id, statut_livraison['id'])

        # 5. Vider le panier
        Commande.vider_panier(commande_id)

        return render(request, "frontoffice/panier.html", {
            "zones": db.fetch_query("SELECT id, nom FROM zones"),
            "message": "Votre commande a été validée avec succès !"
        })
    else:
        return redirect("panier")