#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append('E:\\Projects\\Python\\Web\\Django\\m-lunch')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlunch.settings')
django.setup()

from mlunch.core.models import Livreur, StatutLivreur, ZoneLivreur, HistoriqueStatutLivreur
from mlunch.core.services.commande_service import CommandeService

def test_bouton_assigner_commande():
    """Test pour diagnostiquer pourquoi le bouton 'Assigner commande' ne fonctionne pas"""
    print("🔍 DIAGNOSTIC - BOUTON ASSIGNER COMMANDE")
    print("=" * 50)

    # 1. Vérifier les livreurs et leurs statuts
    print("\n1. VÉRIFICATION DES LIVREURS:")
    print("-" * 30)

    livreurs = Livreur.objects.all()
    livreurs_disponibles = 0

    for livreur in livreurs:
        print(f"\n📋 Livreur: {livreur.nom} (ID: {livreur.id})")

        # Récupérer le statut actuel via l'historique
        try:
            historique_statut = HistoriqueStatutLivreur.objects.filter(
                livreur=livreur
            ).order_by('-mis_a_jour_le').first()

            if historique_statut:
                statut_actuel = historique_statut.statut.appellation
                print(f"   → Statut actuel: '{statut_actuel}'")

                # Test de la condition de disponibilité
                est_disponible = statut_actuel.strip().lower() == 'disponible'
                print(f"   → Est disponible: {est_disponible}")

                if est_disponible:
                    livreurs_disponibles += 1
                    print(f"   ✅ BOUTON DEVRAIT ÊTRE VISIBLE")
                else:
                    print(f"   ❌ BOUTON NE DEVRAIT PAS ÊTRE VISIBLE (statut: '{statut_actuel}')")
            else:
                print(f"   ❌ AUCUN HISTORIQUE DE STATUT")

        except Exception as e:
            print(f"   ❌ ERREUR lors de la récupération du statut: {e}")

    print(f"\n📊 RÉSUMÉ:")
    print(f"   → Total livreurs: {livreurs.count()}")
    print(f"   → Livreurs disponibles: {livreurs_disponibles}")

    # 2. Vérifier les commandes prêtes
    print(f"\n2. VÉRIFICATION DES COMMANDES PRÊTES:")
    print("-" * 30)

    try:
        commandes_pretes = CommandeService.get_commandes_en_attente()
        print(f"   → Nombre de commandes prêtes: {len(commandes_pretes) if commandes_pretes else 0}")

        if commandes_pretes:
            print(f"   ✅ Il y a des commandes à assigner")
            for i, commande in enumerate(commandes_pretes[:3]):  # Afficher les 3 premières
                print(f"      - Commande {commande.id}: {commande.client}")
        else:
            print(f"   ❌ AUCUNE COMMANDE PRÊTE - Le système d'attribution ne fonctionnera pas")

    except Exception as e:
        print(f"   ❌ ERREUR lors de la récupération des commandes: {e}")

    # 3. Test de l'URL
    print(f"\n3. TEST DE L'URL:")
    print("-" * 30)

    if livreurs_disponibles > 0:
        premier_livreur_disponible = None
        for livreur in livreurs:
            try:
                historique_statut = HistoriqueStatutLivreur.objects.filter(
                    livreur=livreur
                ).order_by('-mis_a_jour_le').first()

                if historique_statut and historique_statut.statut.appellation.strip().lower() == 'disponible':
                    premier_livreur_disponible = livreur
                    break
            except:
                continue

        if premier_livreur_disponible:
            print(f"   → URL à tester: /staff/livreurs/{premier_livreur_disponible.id}/assigner-commande/")
            print(f"   → Livreur de test: {premier_livreur_disponible.nom}")
        else:
            print(f"   ❌ Aucun livreur disponible trouvé pour le test")
    else:
        print(f"   ❌ Aucun livreur disponible - Impossible de tester l'URL")

    # 4. Recommandations
    print(f"\n4. RECOMMANDATIONS:")
    print("-" * 30)

    if livreurs_disponibles == 0:
        print("❌ PROBLÈME PRINCIPAL: Aucun livreur disponible")
        print("   → Assurez-vous qu'au moins un livreur a le statut 'Disponible'")
        print("   → Vérifiez la table HistoriqueStatutLivreur")
    elif not commandes_pretes:
        print("❌ PROBLÈME PRINCIPAL: Aucune commande prête")
        print("   → Assurez-vous qu'il y a des commandes avec le statut 'Prête'")
    else:
        print("✅ CONDITIONS REMPLIES - Le bouton devrait fonctionner")
        print("   → Vérifiez les logs du serveur Django")
        print("   → Vérifiez la console du navigateur")
        print("   → Testez l'URL directement")

if __name__ == "__main__":
    test_bouton_assigner_commande()
