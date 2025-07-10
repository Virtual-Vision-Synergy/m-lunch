#!/usr/bin/env python
"""
Script de test pour diagnostiquer la création des suivis
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlunch.settings')
django.setup()

from mlunch.core.models import (
    Client, Commande, CommandeRepas, Repas, RestaurantRepas, Restaurant, 
    SuivisCommande, PointRecup, ModePaiement, StatutCommande, HistoriqueStatutCommande
)
from mlunch.core.services.panier_service import PanierService
from mlunch.core.services.commande_service import CommandeService
from mlunch.core.services.suivisCommande_service import SuivisCommandeService

def test_suivi_creation():
    """Test complet de la création des suivis"""
    print("=== TEST DE CRÉATION DES SUIVIS ===\n")
    
    # 1. Vérifier les données de base
    print("1. Vérification des données de base:")
    clients = Client.objects.all()
    restaurants = Restaurant.objects.all()
    repas = Repas.objects.all()
    restaurant_repas = RestaurantRepas.objects.all()
    
    print(f"   - Clients: {clients.count()}")
    print(f"   - Restaurants: {restaurants.count()}")
    print(f"   - Repas: {repas.count()}")
    print(f"   - Relations RestaurantRepas: {restaurant_repas.count()}")
    
    if clients.count() == 0:
        print("   ERREUR: Aucun client trouvé!")
        return
    
    if restaurants.count() == 0:
        print("   ERREUR: Aucun restaurant trouvé!")
        return
        
    if repas.count() == 0:
        print("   ERREUR: Aucun repas trouvé!")
        return
        
    if restaurant_repas.count() == 0:
        print("   ERREUR: Aucune relation RestaurantRepas trouvée!")
        return
    
    # 2. Vérifier les relations RestaurantRepas
    print("\n2. Vérification des relations RestaurantRepas:")
    for rr in restaurant_repas[:5]:  # Afficher les 5 premières
        print(f"   - Repas '{rr.repas.nom}' (ID: {rr.repas.id}) -> Restaurant '{rr.restaurant.nom}' (ID: {rr.restaurant.id})")
    
    # 3. Tester avec un client existant
    client = clients.first()
    print(f"\n3. Test avec le client: {client.email} (ID: {client.id})")
    
    # 4. Vérifier les points de récupération et modes de paiement
    points_recup = PointRecup.objects.all()
    modes_paiement = ModePaiement.objects.all()
    
    print(f"   - Points de récupération: {points_recup.count()}")
    print(f"   - Modes de paiement: {modes_paiement.count()}")
    
    if points_recup.count() == 0:
        print("   ERREUR: Aucun point de récupération trouvé!")
        return
        
    if modes_paiement.count() == 0:
        print("   ERREUR: Aucun mode de paiement trouvé!")
        return
    
    # 5. Tester l'ajout d'un repas au panier
    print("\n4. Test d'ajout d'un repas au panier:")
    premier_repas = repas.first()
    print(f"   - Ajout du repas: {premier_repas.nom} (ID: {premier_repas.id})")
    
    result = PanierService.add_to_panier(client.id, premier_repas.id, 1)
    if 'error' in result:
        print(f"   ERREUR: {result['error']}")
        return
    else:
        print(f"   SUCCÈS: {result['message']}")
    
    # 6. Vérifier le contenu du panier
    print("\n5. Vérification du contenu du panier:")
    items = PanierService.get_panier_items(client.id)
    if isinstance(items, dict) and 'error' in items:
        print(f"   ERREUR: {items['error']}")
        return
    
    print(f"   - Nombre d'articles dans le panier: {len(items)}")
    for item in items:
        print(f"   - Article: {item['nom']} x{item['quantite']} ({item['restaurant_nom']})")
    
    # 7. Vérifier les commandes existantes
    print("\n6. Vérification des commandes:")
    commandes = Commande.objects.filter(client_id=client.id)
    print(f"   - Nombre de commandes pour ce client: {commandes.count()}")
    
    for commande in commandes:
        last_statut = commande.historiques.order_by('-mis_a_jour_le').first()
        statut_id = last_statut.statut_id if last_statut else "Aucun"
        print(f"   - Commande {commande.id}: statut = {statut_id}")
        
        # Vérifier les repas de cette commande
        commande_repas = CommandeRepas.objects.filter(commande=commande)
        print(f"     * Nombre de repas: {commande_repas.count()}")
        for cr in commande_repas:
            print(f"     * Repas: {cr.repas.nom} x{cr.quantite}")
    
    # 8. Tester la validation de commande
    print("\n7. Test de validation de commande:")
    point_recup = points_recup.first()
    mode_paiement = modes_paiement.first()
    
    print(f"   - Point de récupération: {point_recup.nom} (ID: {point_recup.id})")
    print(f"   - Mode de paiement: {mode_paiement.nom} (ID: {mode_paiement.id})")
    
    # Ajouter plus de debug
    print("\n8. Debug avancé avant validation:")
    commandes_en_cours = Commande.objects.filter(client_id=client.id)
    for commande in commandes_en_cours:
        last_statut = commande.historiques.order_by('-mis_a_jour_le').first()
        if last_statut and last_statut.statut_id == 1:
            print(f"   - Commande en cours trouvée: {commande.id}")
            # Vérifier les repas et leurs restaurants
            repas_commande = CommandeRepas.objects.filter(commande=commande)
            for cr in repas_commande:
                rr = RestaurantRepas.objects.filter(repas=cr.repas).first()
                if rr:
                    print(f"     * Repas {cr.repas.id} -> Restaurant {rr.restaurant.id} ({rr.restaurant.nom})")
                else:
                    print(f"     * PROBLÈME: Repas {cr.repas.id} n'a pas de restaurant associé!")
            
            # Tester la méthode get_all_id_restaurant_from_commande
            restaurant_ids = CommandeService.get_all_id_restaurant_from_commande(commande.id)
            print(f"     * Restaurants trouvés par le service: {restaurant_ids}")
    
    success, message = PanierService.validate_commande(client.id, point_recup.id, mode_paiement.id)
    
    print(f"   - Résultat: {'SUCCÈS' if success else 'ÉCHEC'}")
    print(f"   - Message: {message}")
    
    # 9. Vérifier les suivis créés
    print("\n9. Vérification des suivis créés:")
    suivis = SuivisCommande.objects.all()
    print(f"   - Nombre total de suivis: {suivis.count()}")
    
    for suivi in suivis:
        print(f"   - Suivi: Commande {suivi.commande.id} -> Restaurant {suivi.restaurant.nom} (Statut: {suivi.statut})")
    
    print("\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_suivi_creation()
