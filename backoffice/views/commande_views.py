from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from mlunch.core.services.commande_service import CommandeService
from mlunch.core.models import Commande, StatutCommande
import json

def commande_list(request):
    """Liste toutes les commandes pour le backoffice"""
    commandes = CommandeService.get_all_commandes()
    statuts = StatutCommande.objects.all()

    # Filtrage par statut si spécifié
    statut_id = request.GET.get('statut')
    if statut_id:
        commandes = commandes.filter(statut_id=statut_id)

    return render(request, 'backoffice/commande.html', {
        'commandes': commandes,
        'statuts': statuts,
        'selected_statut': int(statut_id) if statut_id else None
    })

def commande_detail(request, commande_id):
    """Détail d'une commande spécifique"""
    commande = get_object_or_404(Commande, id=commande_id)
    return render(request, 'backoffice/commande_detail.html', {
        'commande': commande
    })

@csrf_exempt
def commande_update_statut(request, commande_id):
    """Met à jour le statut d'une commande"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nouveau_statut_id = data.get('statut_id')

            commande = get_object_or_404(Commande, id=commande_id)
            CommandeService.update_statut_commande(commande, nouveau_statut_id)

            return JsonResponse({'success': True, 'message': 'Statut mis à jour avec succès'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

def commandes_en_attente(request):
    """Liste des commandes en attente pour le dashboard"""
    commandes = CommandeService.get_commandes_en_attente()
    return render(request, 'backoffice/commandes_en_attente.html', {
        'commandes': commandes
    })

def commande_attribuer(request, commande_id):
    """Page d'attribution d'une commande à un livreur"""
    from mlunch.core.models import Livreur, ZoneLivreur, ZoneClient
    from mlunch.core.services.livreur_service import LivreurService
    from mlunch.core.services.distance_service import DistanceService

    commande = get_object_or_404(Commande, id=commande_id)

    # Récupérer la zone du client pour cette commande
    try:
        zone_client = ZoneClient.objects.get(client=commande.client)
        zone = zone_client.zone

        # Récupérer les livreurs disponibles dans cette zone
        livreurs_zone = ZoneLivreur.objects.filter(zone=zone).select_related('livreur')
        livreurs_disponibles = [zl.livreur for zl in livreurs_zone]

    except ZoneClient.DoesNotExist:
        # Si le client n'a pas de zone définie, récupérer tous les livreurs
        livreurs_disponibles = Livreur.objects.all()
        zone = None

    # Calculer la distance pour chaque livreur
    livreurs_avec_distance = []
    for livreur in livreurs_disponibles:
        distance_info = DistanceService.get_distance(livreur.id, commande_id)
        livreur_data = {
            'livreur': livreur,
            'distance_totale': distance_info.get('distance_totale', 0),
            'temps_estime': distance_info.get('temps_estime', 0),
            'nombre_restaurants': distance_info.get('nombre_restaurants', 0),
            'error': distance_info.get('error', None)
        }
        livreurs_avec_distance.append(livreur_data)

    # Trier les livreurs par distance (les plus proches en premier)
    livreurs_avec_distance.sort(key=lambda x: x['distance_totale'])

    return render(request, 'backoffice/commande_attribuer.html', {
        'commande': commande,
        'livreurs_avec_distance': livreurs_avec_distance,
        'zone': zone
    })

def commande_attribuer_confirmer(request, commande_id):
    """Confirme l'attribution d'une commande à un livreur"""
    from mlunch.core.models import Livraison, Livreur
    from mlunch.core.services.livraison_service import LivraisonService

    if request.method == 'POST':
        commande = get_object_or_404(Commande, id=commande_id)
        livreur_id = request.POST.get('livreur_id')

        if not livreur_id:
            messages.error(request, 'Veuillez sélectionner un livreur.')
            return redirect('commande_attribuer', commande_id=commande_id)

        try:
            livreur = get_object_or_404(Livreur, id=livreur_id)

            # Créer la livraison
            livraison = Livraison.objects.create(
                livreur=livreur,
                commande=commande
            )

            # Mettre à jour le statut de la commande (supposons que le statut "En livraison" existe)
            try:
                statut_en_livraison = StatutCommande.objects.get(appellation="En livraison")
                CommandeService.update_statut_commande(commande, statut_en_livraison.id)
            except StatutCommande.DoesNotExist:
                pass  # Si le statut n'existe pas, on continue sans mettre à jour

            messages.success(request, f'Commande #{commande.id} attribuée avec succès à {livreur.nom}.')
            return redirect('index')

        except Exception as e:
            messages.error(request, f'Erreur lors de l\'attribution : {str(e)}')
            return redirect('commande_attribuer', commande_id=commande_id)

    return redirect('commande_attribuer', commande_id=commande_id)
