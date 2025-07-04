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
