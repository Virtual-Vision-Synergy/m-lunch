from django.shortcuts import render
from django.contrib import messages
from mlunch.core.Client import Client
from mlunch.core.Commande import Commande
from mlunch.core.Livraison import Livraison
from mlunch.core.Livreur import Livreur
from mlunch.core.Repas import Repas
from mlunch.core.Restaurant import Restaurant
from mlunch.core.Zone import Zone
from mlunch.core.Entite import Entite

from django.http import JsonResponse
from django.db import connection
from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta

def test_create_client(request):
    # Créer le client
    # result = Client.CreateClient('email@example.com', 'mot_de_passe', '555', 'ddd', 'dddddd')
    
    # if 'error' in result:
    #     messages.error(request, result['error'])
    # else:
    #     messages.success(request, f"Client créé avec succès : {result['client']['email']}")
    #     print(result)
    # return render(request, 'backoffice/index.html')
    
    #recuperer le client by ID
    # try:
    #         client_id = int(2)  # Assurer que client_id est un entier
    #         result = Client.GetClientFromId(client_id)
            
    #         if "error" in result:
    #             print(f"Erreur: {result['error']}")  # Affichage dans le terminal
    #             messages.error(request, result["error"])
    #             return render(request, 'backoffice/index.html', {"client": None})
            
    #         print(f"Client récupéré: {result}")  # Affichage dans le terminal
    #         messages.success(request, f"Client récupéré avec succès : {result['email']}")
    #         return render(request, 'backoffice/index.html', {"client": result})
        
    # except ValueError:
    #         print(f"Erreur: L'ID fourni n'est pas un entier valide")  # Affichage dans le terminal
    #         messages.error(request, "L'ID fourni n'est pas un entier valide")
    #         return render(request, 'backoffice/index.html', {"client": None})
    # recuperer le client by email
    # """Vue Django pour tester la récupération d'un client par email avec affichage dans le terminal."""
    # result = Client.GetClientFromEmail('email@example.com')
    
    # if "error" in result:
    #     print(f"Erreur: {result['error']}")  # Affichage dans le terminal
    #     messages.error(request, result["error"])
    #     return render(request, 'backoffice/index.html', {"client": None})
    
    # print(f"Client récupéré: {result}")  # Affichage dans le terminal
    # messages.success(request, f"Client récupéré avec succès : {result['email']}")
    # return render(request, 'backoffice/index.html', {"client": result})
    
    #recuperer tous les clients
    """Vue Django pour tester la récupération de tous les clients avec affichage dans le terminal."""
    result = Client.GetAllClients()
        
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"clients": []})
    print(f"Clients récupérés: {result}")  # Affichage dans le terminal
    messages.success(request, f"{len(result)} client(s) récupéré(s) avec succès")
    return render(request, 'backoffice/index.html', {"clients": result})

def test_update_client(request):
    """Vue Django pour tester la mise à jour d'un client avec affichage dans le terminal."""
    try:
        client_id = int(1)  # Assurer que client_id est un entier
        # Exemple de données pour le test (à ajuster selon vos besoins)
        update_data = {
            "email": "updated@example.com",
            "mot_de_passe": "newpassword123",
            "contact": "123456789",
            "prenom": "Jean",
            "nom": "Dupont"
        }
        result = Client.UpdateClient(
            client_id,
            email=update_data["email"],
            mot_de_passe=update_data["mot_de_passe"],
            contact=update_data["contact"],
            prenom=update_data["prenom"],
            nom=update_data["nom"]
        )
        
        if "error" in result:
            print(f"Erreur: {result['error']}")  # Affichage dans le terminal
            messages.error(request, result["error"])
            return render(request, 'backoffice/index.html', {"client": None})
        
        print(f"Client mis à jour: {result}")  # Affichage dans le terminal
        messages.success(request, f"Client mis à jour avec succès : {result['email']}")
        return render(request, 'backoffice/index.html', {"client": result})
    
    except ValueError:
        print(f"Erreur: L'ID fourni n'est pas un entier valide")  # Affichage dans le terminal
        messages.error(request, "L'ID fourni n'est pas un entier valide")
        return render(request, 'backoffice/index.html', {"client": None})

def test_create_commande(request):
    """Vue Django pour tester la création d'une commande avec affichage dans le terminal."""

    # Valeurs de test à insérer ici (exemples à ajuster selon ta base)
    client_id = 1
    point_recup_id = 1
    initial_statut_id = 1

    try:
        result = Commande.CreateCommande(client_id, point_recup_id, initial_statut_id)
        
        if "error" in result:
            print(f"Erreur: {result['error']}")  # Affichage dans le terminal
            messages.error(request, result["error"])
            return render(request, 'backoffice/index.html', {"commande": None})
        
        print(f"Commande créée: {result}")  # Affichage dans le terminal
        messages.success(request, f"Commande ID {result['commande']['id']} créée avec succès")
        return render(request, 'backoffice/index.html', {"commande": result["commande"]})

    except ValueError:
        print("Erreur: Les IDs doivent être des entiers valides")  # Affichage dans le terminal
        messages.error(request, "Les IDs doivent être des entiers valides")
        return render(request, 'backoffice/index.html', {"commande": None})

def test_get_commande_from_id(request):
    """Vue Django pour tester la récupération d'une commande par ID."""
    try:
        commande_id = int(1)
        result = Commande.GetCommandeFromId(commande_id)
        
        if "error" in result:
            print(f"Erreur: {result['error']}")  # Affichage dans le terminal
            messages.error(request, result["error"])
            return render(request, 'backoffice/index.html', {"commande": None})
        
        print(f"Commande récupérée: {result}")  # Affichage dans le terminal
        messages.success(request, f"Commande ID {result['data'][0]['id']} récupérée avec succès")
        return render(request, 'backoffice/index.html', {"commande": result["data"]})
    
    except ValueError:
        print("Erreur: L'ID doit être un entier valide")  # Affichage dans le terminal
        messages.error(request, "L'ID doit être un entier valide")
        return render(request, 'backoffice/index.html', {"commande": None})

def test_get_all_commandes(request):
    """Vue Django pour tester la récupération de toutes les commandes."""
    result = Commande.GetAllCommandes()
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"commandes": []})
    
    print(f"Commandes récupérées: {result}")  # Affichage dans le terminal
    messages.success(request, f"{len(result)} commande(s) récupérée(s) avec succès")
    return render(request, 'backoffice/index.html', {"commandes": result})

def test_update_commande(request):
    """Vue Django pour tester la mise à jour du statut d'une commande."""
    try:
        commande_id = int(1)
        statut_id = int(2)
        result = Commande.UpdateCommande(commande_id, statut_id)
        
        if "error" in result:
            print(f"Erreur: {result['error']}")  # Affichage dans le terminal
            messages.error(request, result["error"])
            return render(request, 'backoffice/index.html', {"commande": None})
        
        print(f"Statut de commande mis à jour: {result}")  # Affichage dans le terminal
        messages.success(request, f"Statut de la commande ID {result['commande_id']} mis à jour")
        return render(request, 'backoffice/index.html', {"commande": result})
    
    except ValueError:
        print("Erreur: Les IDs doivent être des entiers valides")  # Affichage dans le terminal
        messages.error(request, "Les IDs doivent être des entiers valides")
        return render(request, 'backoffice/index.html', {"commande": None})

def test_delete_commande(request):
    """Vue Django pour tester le marquage d'une commande comme supprimée."""
    try:
        commande_id = int(1)
        statut_id = int(3)
        result = Commande.DeleteCommande(commande_id, statut_id)
        
        if "error" in result:
            print(f"Erreur: {result['error']}")  # Affichage dans le terminal
            messages.error(request, result["error"])
            return render(request, 'backoffice/index.html', {"commande": None})
        
        print(f"Commande marquée comme supprimée: {result}")  # Affichage dans le terminal
        messages.success(request, f"Commande ID {result['commande_id']} marquée comme supprimée (statut ID {result['statut_id']})")
        return render(request, 'backoffice/index.html', {"commande": result})
    
    except ValueError:
        print("Erreur: Les IDs doivent être des entiers valides")  # Affichage dans le terminal
        messages.error(request, "Les IDs doivent être des entiers valides")
        return render(request, 'backoffice/index.html', {"commande": None})
    
def test_create_entite(request):
        """Vue Django pour tester la création d'une entité."""
        result = Entite.CreateEntite('universite')
        
        if "error" in result:
            print(f"Erreur: {result['error']}")  # Affichage dans le terminal
            messages.error(request, result["error"])
            return render(request, 'backoffice/index.html', {"entite": None})
        
        print(f"Entité créée: {result}")  # Affichage dans le terminal
        messages.success(request, f"Entité '{result['entite']['nom']}' créée avec succès")
        return render(request, 'backoffice/index.html', {"entite": result["entite"]})
    
def test_get_entite_from_id(request, entite_id):
    """Vue Django pour tester la récupération d'une entité par ID."""
    try:
        entite_id = int(entite_id)
        result = Entite.GetEntiteFromId(entite_id)
        
        if "error" in result:
            print(f"Erreur: {result['error']}")  # Affichage dans le terminal
            messages.error(request, result["error"])
            return render(request, 'backoffice/index.html', {"entite": None})
        
        print(f"Entité récupérée: {result}")  # Affichage dans le terminal
        messages.success(request, f"Entité ID {result['data'][0]['entite_id']} récupérée avec succès")
        return render(request, 'backoffice/index.html', {"entite": result["data"]})
    
    except ValueError:
        print("Erreur: L'ID doit être un entier valide")  # Affichage dans le terminal
        messages.error(request, "L'ID doit être un entier valide")
        return render(request, 'backoffice/index.html', {"entite": None})

def test_get_all_entites(request):
    """Vue Django pour tester la récupération de toutes les entités."""
    result = Entite.GetAllEntites()
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"entites": []})
    
    print(f"Entités récupérées: {result}")  # Affichage dans le terminal
    messages.success(request, f"{len(result)} entité(s) récupérée(s) avec succès")
    return render(request, 'backoffice/index.html', {"entites": result})

def test_update_entite(request):
    """Vue Django pour tester la mise à jour d'une entité."""
    try:
        entite_id = int(1)
        statut_id = int(2)
        result = Entite.UpdateEntite(entite_id, statut_id)
        
        if "error" in result:
            print(f"Erreur: {result['error']}")  # Affichage dans le terminal
            messages.error(request, result["error"])
            return render(request, 'backoffice/index.html', {"entite": None})
        
        print(f"Entité mise à jour: {result}")  # Affichage dans le terminal
        messages.success(request, f"Entité ID {result['entite']['id']} mise à jour avec succès")
        return render(request, 'backoffice/index.html', {"entite": result["entite"]})
    
    except ValueError:
        print("Erreur: Les IDs doivent être des entiers valides")  # Affichage dans le terminal
        messages.error(request, "Les IDs doivent être des entiers valides")
        return render(request, 'backoffice/index.html', {"entite": None})

def test_delete_entite(request, entite_id):
    """Vue Django pour tester le marquage d'une entité comme inactive."""
    try:
        entite_id = int(entite_id)
        result = Entite.DeleteEntite(entite_id)
        
        if result:
            print(f"Erreur: {result['error']}")  # Affichage dans le terminal
            messages.error(request, result["error"])
            return render(request, 'backoffice/index.html', {"entite": None})
        
        print(f"Entité marquée comme inactive: {result}")  # Affichage dans le terminal
        messages.success(request, f"Entité ID {result['entite_id']} marquée comme inactive")
        return render(request, 'backoffice/index.html', {"entite": result})
    
    except ValueError:
        print("Erreur: L'ID doit être un entier valide")  # Affichage dans le terminal
        messages.error(request, "L'ID doit être un entier valide")
        return render(request, 'backoffice/index.html', {"entite": None})
    
def test_create_livreur(request):
    """Vue Django pour tester la création d'un livreur avec données brutes."""
    result = Livreur.CreateLivreur(nom="Jean Dupont", initial_statut_id=1, contact="1234567890", position=(2.3522, 48.8566))
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"livreur": None})
    
    print(f"Livreur créé: {result}")  # Affichage dans le terminal
    messages.success(request, f"Livreur '{result['livreur']['nom']}' créé avec succès")
    return render(request, 'backoffice/index.html', {"livreur": result["livreur"]})

def test_get_livreur_from_id(request):
    """Vue Django pour tester la récupération d'un livreur par ID avec données brutes."""
    livreur_id = 1
    result = Livreur.GetLivreurFromId(livreur_id)
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"livreur": None})
    
    print(f"Livreur récupéré: {result}")  # Affichage dans le terminal
    messages.success(request, f"Livreur ID {result['data'][0]['livreur_id']} récupéré avec succès")
    return render(request, 'backoffice/index.html', {"livreur": result["data"]})

def test_get_all_livreurs(request):
    """Vue Django pour tester la récupération de tous les livreurs."""
    result = Livreur.GetAllLivreurs()
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"livreurs": []})
    
    print(f"Livreurs récupérés: {result}")  # Affichage dans le terminal
    messages.success(request, f"{len(result)} livreur(s) récupéré(s) avec succès")
    return render(request, 'backoffice/index.html', {"livreurs": result})

def test_update_livreur(request):
    """Vue Django pour tester la mise à jour d'un livreur avec données brutes."""
    livreur_id = 1
    result = Livreur.UpdateLivreur(livreur_id, nom="Marie Martin", contact="0987654321", position=(2.3600, 48.8600))
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"livreur": None})
    
    print(f"Livreur mis à jour: {result}")  # Affichage dans le terminal
    messages.success(request, f"Livreur ID {result['id']} mis à jour avec succès")
    return render(request, 'backoffice/index.html', {"livreur": result})

def test_delete_livreur(request):
    """Vue Django pour tester le marquage d'un livreur comme renvoyé avec données brutes."""
    livreur_id = 1
    result = Livreur.DeleteLivreur(livreur_id)
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"livreur": None})
    
    print(f"Livreur marqué comme renvoyé: {result}")  # Affichage dans le terminal
    messages.success(request, f"Livreur ID {result['livreur_id']} marqué comme renvoyé")
    return render(request, 'backoffice/index.html', {"livreur": result})

def test_create_repas_success(request):
        result = Repas.CreateRepas(
            nom="Pizza Margherita",
            type_id=1,
            prix=1200,
            description="Pizza classique avec tomate et mozzarella",
            image="/images/pizza_margherita.jpg",
            est_dispo=True
        )
        print(f"Test CreateRepas: Succès - {result}")
        return render(request, 'backoffice/index.html', {"livreur": result})

def test_get_repas_from_id(request):
    """Vue Django pour tester la récupération d'un repas par ID avec données brutes."""
    repas_id = 1
    result = Repas.GetRepasFromId(repas_id)
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"repas": None})
    
    print(f"Repas récupéré: {result}")  # Affichage dans le terminal
    messages.success(request, f"Repas ID {result['data'][0]['repas_id']} récupéré avec succès")
    return render(request, 'backoffice/index.html', {"repas": result["data"]})

def test_get_all_repas(request):
    """Vue Django pour tester la récupération de tous les repas."""
    result = Repas.GetAllRepas()
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"repas_list": []})
    
    print(f"Repas récupérés: {result}")  # Affichage dans le terminal
    messages.success(request, f"{len(result)} repas récupéré(s) avec succès")
    return render(request, 'backoffice/index.html', {"repas_list": result})

def test_update_repas(request):
    """Vue Django pour tester la mise à jour d'un repas avec données brutes."""
    repas_id = 1
    result = Repas.UpdateRepas(
        repas_id,
        nom="Pizza Quattro",
        type_id=1,
        prix=1500,
        description="Pizza avec quatre fromages",
        image="/images/pizza_quattro.jpg",
        est_dispo=False
    )
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"repas": None})
    
    print(f"Repas mis à jour: {result}")  # Affichage dans le terminal
    messages.success(request, f"Repas ID {result['repas']['id']} mis à jour avec succès")
    return render(request, 'backoffice/index.html', {"repas": result["repas"]})

def test_delete_repas(request):
    """Vue Django pour tester le marquage d'un repas comme non disponible avec données brutes."""
    repas_id = 1
    result = Repas.DeleteRepas(repas_id)
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"repas": None})
    
    print(f"Repas marqué comme non disponible: {result}")  # Affichage dans le terminal
    messages.success(request, f"Repas ID {result['repas_id']} marqué comme non disponible")
    return render(request, 'backoffice/index.html', {"repas": result})

def test_create_restaurant(request):
    """Vue Django pour tester la création d'un restaurant avec données brutes."""
    result = Restaurant.CreateRestaurant(
        nom="Le Bistro Parisien",
        initial_statut_id=1,
        adresse="12 Rue de Rivoli, 75004 Paris",
        image="/images/bistro_parisien.jpg",
        geo_position=(2.3522, 48.8566)
    )
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"restaurant": None})
    
    print(f"Restaurant créé: {result}")  # Affichage dans le terminal
    messages.success(request, f"Restaurant '{result['restaurant']['nom']}' créé avec succès")
    return render(request, 'backoffice/index.html', {"restaurant": result["restaurant"]})

def test_get_restaurant_from_id(request):
    """Vue Django pour tester la récupération d'un restaurant par ID avec données brutes."""
    restaurant_id = 1
    result = Restaurant.GetRestaurantFromId(restaurant_id)
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"restaurant": None})
    
    print(f"Restaurant récupéré: {result}")  # Affichage dans le terminal
    messages.success(request, f"Restaurant ID {result['data'][0]['restaurant_id']} récupéré avec succès")
    return render(request, 'backoffice/index.html', {"restaurant": result["data"]})

def test_get_all_restaurants(request):
    """Vue Django pour tester la récupération de tous les restaurants."""
    result = Restaurant.GetAllRestaurants()
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"restaurants": []})
    
    print(f"Restaurants récupérés: {result}")  # Affichage dans le terminal
    messages.success(request, f"{len(result)} restaurant(s) récupéré(s) avec succès")
    return render(request, 'backoffice/index.html', {"restaurants": result})

def test_update_restaurant(request):
    """Vue Django pour tester la mise à jour d'un restaurant avec données brutes."""
    restaurant_id = 1
    result = Restaurant.UpdateRestaurant(
        restaurant_id,
        nom="Le Nouveau Bistro",
        adresse="15 Rue de la Paix, 75002 Paris",
        image="/images/nouveau_bistro.jpg",
        geo_position=(2.3300, 48.8693),
        statut_id=2
    )
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"restaurant": None})
    
    print(f"Restaurant mis à jour: {result}")  # Affichage dans le terminal
    messages.success(request, f"Restaurant ID {result['restaurant']['id']} mis à jour avec succès")
    return render(request, 'backoffice/index.html', {"restaurant": result["restaurant"]})

def test_delete_restaurant(request):
    """Vue Django pour tester le marquage d'un restaurant comme fermé avec données brutes."""
    restaurant_id = 1
    result = Restaurant.DeleteRestaurant(restaurant_id)
    
    if "error" in result:
        print(f"Erreur: {result['error']}")  # Affichage dans le terminal
        messages.error(request, result["error"])
        return render(request, 'backoffice/index.html', {"restaurant": None})
    
    print(f"Restaurant marqué comme fermé: {result}")  # Affichage dans le terminal
    messages.success(request, f"Restaurant ID {result['restaurant_id']} marqué comme fermé")
    return render(request, 'backoffice/index.html', {"restaurant": result})