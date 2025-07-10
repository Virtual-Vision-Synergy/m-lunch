#!/usr/bin/env python
"""
Script pour vérifier et corriger la disponibilité des repas
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlunch.settings')
django.setup()

from mlunch.core.models import Repas, DisponibiliteRepas

def check_and_fix_disponibilite():
    """Vérifier et corriger la disponibilité des repas"""
    print("=== VÉRIFICATION DE LA DISPONIBILITÉ DES REPAS ===\n")
    
    # 1. Vérifier tous les repas
    repas_list = Repas.objects.all()
    print(f"Nombre total de repas: {repas_list.count()}")
    
    # 2. Vérifier les disponibilités existantes
    disponibilites = DisponibiliteRepas.objects.all()
    print(f"Nombre total de disponibilités: {disponibilites.count()}")
    
    # 3. Afficher quelques exemples
    print("\nExemples de disponibilités existantes:")
    for dispo in disponibilites[:10]:
        status = "DISPONIBLE" if dispo.est_dispo else "INDISPONIBLE"
        print(f"  - {dispo.repas.nom}: {status}")
    
    # 4. Vérifier les repas sans disponibilité
    repas_sans_dispo = []
    repas_indisponibles = []
    
    for repas in repas_list:
        dispo = DisponibiliteRepas.objects.filter(repas=repas).first()
        if not dispo:
            repas_sans_dispo.append(repas)
        elif not dispo.est_dispo:
            repas_indisponibles.append(repas)
    
    print(f"\nRepas SANS disponibilité définie: {len(repas_sans_dispo)}")
    for repas in repas_sans_dispo[:5]:  # Afficher les 5 premiers
        print(f"  - {repas.nom} (ID: {repas.id})")
    
    print(f"\nRepas marqués comme INDISPONIBLES: {len(repas_indisponibles)}")
    for repas in repas_indisponibles[:5]:  # Afficher les 5 premiers
        print(f"  - {repas.nom} (ID: {repas.id})")
    
    # 5. Corriger le problème
    print("\n=== CORRECTION ===")
    
    # Créer des disponibilités pour les repas qui n'en ont pas
    created_count = 0
    for repas in repas_sans_dispo:
        DisponibiliteRepas.objects.create(
            repas=repas,
            est_dispo=True
        )
        created_count += 1
    
    print(f"Créé {created_count} nouvelles disponibilités")
    
    # Mettre à jour les repas indisponibles
    updated_count = 0
    for repas in repas_indisponibles:
        dispo = DisponibiliteRepas.objects.filter(repas=repas).first()
        if dispo:
            dispo.est_dispo = True
            dispo.save()
            updated_count += 1
    
    print(f"Mis à jour {updated_count} disponibilités")
    
    # 6. Vérifier le résultat
    print("\n=== VÉRIFICATION FINALE ===")
    disponibles = DisponibiliteRepas.objects.filter(est_dispo=True).count()
    indisponibles = DisponibiliteRepas.objects.filter(est_dispo=False).count()
    
    print(f"Repas disponibles: {disponibles}")
    print(f"Repas indisponibles: {indisponibles}")
    
    print("\n=== CORRECTION TERMINÉE ===")

if __name__ == "__main__":
    check_and_fix_disponibilite()
