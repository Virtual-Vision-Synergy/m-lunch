from django.shortcuts import render
from django.contrib import messages
from mlunch.core.services import (
    ClientService, CommandeService, LivraisonService,
    LivreurService, RepasService, RestaurantService, ZoneService
)
from mlunch.core.models import Client, Commande, Livraison, Livreur, Repas, Restaurant, Zone

from django.http import JsonResponse
from django.db import connection
from datetime import datetime, timedelta

def test_create_client(request):
    """Test de création d'un client avec les nouveaux services Django."""
    # Créer le client avec le nouveau service
    result = ClientService.create_client(
        email='email@example.com',
        mot_de_passe='mot_de_passe',
        contact='555',
        prenom='ddd',
        nom='dddddd'
    )

    if 'error' in result:
        messages.error(request, result['error'])
    else:
        messages.success(request, f"Client créé avec succès : {result['client']['email']}")
        print(result)

    return render(request, 'backoffice/index.html')

def test_get_client_by_id(request):
    """Test de récupération d'un client par ID."""
    try:
        client_id = 2  # ID du client à récupérer
        result = ClientService.get_client_by_id(client_id)

        if "error" in result:
            print(f"Erreur: {result['error']}")
            messages.error(request, result["error"])
            return render(request, 'backoffice/index.html', {"client": None})
        
        print(f"Client récupéré: {result}")
        messages.success(request, f"Client récupéré avec succès : {result['email']}")
        return render(request, 'backoffice/index.html', {"client": result})

    except Exception as e:
        print(f"Erreur: {str(e)}")
        messages.error(request, f"Erreur lors de la récupération : {str(e)}")
        return render(request, 'backoffice/index.html', {"client": None})

def test_get_client_by_email(request):
    """Test de récupération d'un client par email."""
    result = ClientService.get_client_by_email('email@example.com')

    if "error" in result:
        print(f"Erreur: {result['error']}")
        messages.error(request, result["error"])
    else:
        print(f"Client récupéré: {result}")
        messages.success(request, f"Client trouvé : {result['email']}")

    return render(request, 'backoffice/index.html', {"client": result if "error" not in result else None})

def test_create_restaurant(request):
    """Test de création d'un restaurant."""
    # D'abord créer un statut restaurant si nécessaire
    from mlunch.core.models import StatutRestaurant
    statut, created = StatutRestaurant.objects.get_or_create(nom="Ouvert")

    result = RestaurantService.create_restaurant(
        nom="Restaurant Test",
        initial_statut_id=statut.id,
        adresse="123 Test Street"
    )

    if 'error' in result:
        messages.error(request, result['error'])
    else:
        messages.success(request, f"Restaurant créé : {result['restaurant']['nom']}")
        print(result)

    return render(request, 'backoffice/index.html')

def test_create_commande(request):
    """Test de création d'une commande."""
    # Créer les dépendances nécessaires si elles n'existent pas
    from mlunch.core.models import StatutCommande, PointRecup

    # Créer un client test
    client_result = ClientService.create_client(
        email='test_commande@example.com',
        mot_de_passe='password123'
    )

    if 'error' in client_result:
        messages.error(request, f"Erreur création client : {client_result['error']}")
        return render(request, 'backoffice/index.html')

    # Créer point de récupération et statut
    point_recup, _ = PointRecup.objects.get_or_create(
        nom="Point Test",
        defaults={'adresse': "123 Test Address"}
    )
    statut, _ = StatutCommande.objects.get_or_create(nom="En attente")

    result = CommandeService.create_commande(
        client_id=client_result['client']['id'],
        point_recup_id=point_recup.id,
        initial_statut_id=statut.id
    )

    if 'error' in result:
        messages.error(request, result['error'])
    else:
        messages.success(request, f"Commande créée : ID {result['commande']['id']}")
        print(result)

    return render(request, 'backoffice/index.html')
