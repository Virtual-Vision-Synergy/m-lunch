from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from mlunch.core.models import Livreur, StatutLivreur, ZoneLivreur, Commande, HistoriqueStatutLivreur
from mlunch.core.services.commande_service import CommandeService
from mlunch.core.services.livraison_service import LivraisonService
from mlunch.core.services.distance_service import DistanceService
import json
import logging

logger = logging.getLogger(__name__)

def livreurs_list(request):
    """Liste de tous les livreurs avec filtres"""
    livreurs = Livreur.objects.all()

    # Récupérer tous les statuts pour le filtre
    statuts = StatutLivreur.objects.all()

    # Récupérer tous les secteurs pour le filtre
    secteurs = ZoneLivreur.objects.select_related('zone').values_list('zone__nom', flat=True).distinct()

    # Filtrage par secteur
    secteur_filter = request.GET.get('secteur')
    if secteur_filter:
        livreurs = livreurs.filter(zonelivreur__zone__nom=secteur_filter)

    # Filtrage par statut - on filtrera après avoir récupéré les statuts actuels
    statut_filter = request.GET.get('statut')

    # Préparer les données pour le template
    livreurs_data = []
    for livreur in livreurs:
        # Récupérer le secteur du livreur
        try:
            zone_livreur = ZoneLivreur.objects.get(livreur=livreur)
            secteur = zone_livreur.zone.nom
        except ZoneLivreur.DoesNotExist:
            secteur = "Non défini"

        # Récupérer le statut actuel du livreur via l'historique
        try:
            historique_statut = HistoriqueStatutLivreur.objects.filter(
                livreur=livreur
            ).order_by('-mis_a_jour_le').first()

            if historique_statut:
                statut_actuel = historique_statut.statut.appellation
            else:
                statut_actuel = "Non défini"
        except:
            statut_actuel = "Non défini"

        # Vérifier si le livreur est disponible
        est_disponible = statut_actuel.strip().lower() == 'disponible'

        # Debug: imprimer le statut pour diagnostiquer
        print(f"DEBUG - Livreur {livreur.nom}: statut='{statut_actuel}', disponible={est_disponible}")

        livreur_data = {
            'id': livreur.id,
            'nom': livreur.nom,
            'contact': livreur.contact,
            'secteur': secteur,
            'statut': statut_actuel,
            'date_inscri': livreur.date_inscri,
            'est_disponible': est_disponible
        }

        # Appliquer le filtre de statut si nécessaire
        if statut_filter and statut_filter != statut_actuel:
            continue

        livreurs_data.append(livreur_data)

    return render(request, 'backoffice/livreurs/livreurs_list.html', {
        'livreurs': livreurs_data,
        'statuts': statuts,
        'secteurs': [{'nom': s} for s in secteurs],
        'selected_secteur': secteur_filter,
        'selected_statut': statut_filter
    })

def livreur_detail(request, livreur_id):
    """Détail d'un livreur spécifique"""
    livreur = get_object_or_404(Livreur, id=livreur_id)
    return render(request, 'backoffice/livreurs/livreur_detail.html', {
        'livreur': livreur
    })

def livreur_add(request):
    """Ajouter un nouveau livreur"""
    if request.method == 'POST':
        # Logique d'ajout de livreur à implémenter
        pass
    return render(request, 'backoffice/livreurs/livreur_add.html')

def livreur_edit(request, livreur_id):
    """Modifier un livreur existant"""
    livreur = get_object_or_404(Livreur, id=livreur_id)
    if request.method == 'POST':
        # Logique de modification à implémenter
        pass
    return render(request, 'backoffice/livreurs/livreur_edit.html', {
        'livreur': livreur
    })

def livreur_delete(request, livreur_id):
    """Désactiver un livreur"""
    livreur = get_object_or_404(Livreur, id=livreur_id)
    # Logique de désactivation à implémenter
    return redirect('livreurs_list')

def livreur_assigner_commande(request, livreur_id):
    """Page d'attribution d'une commande à un livreur spécifique"""
    livreur = get_object_or_404(Livreur, id=livreur_id)

    # Récupérer le statut actuel du livreur via l'historique
    try:
        historique_statut = HistoriqueStatutLivreur.objects.filter(
            livreur=livreur
        ).order_by('-mis_a_jour_le').first()

        if historique_statut:
            statut_actuel = historique_statut.statut.appellation
        else:
            statut_actuel = "Non défini"
    except:
        statut_actuel = "Non défini"

    # Vérifier que le livreur est disponible
    if statut_actuel.strip().lower() != 'disponible':
        messages.error(request, f'Le livreur {livreur.nom} n\'est pas disponible (statut: {statut_actuel}).')
        return redirect('livreurs_list')

    # Récupérer les commandes prêtes
    commandes_pretes = CommandeService.get_commandes_en_attente()

    if not commandes_pretes:
        messages.info(request, 'Aucune commande prête pour attribution.')
        return redirect('livreurs_list')

    # Calculer la distance pour chaque commande
    commandes_avec_distance = []
    for commande in commandes_pretes:
        # commande est un dictionnaire, donc on utilise commande['id'] ou commande.get('id')
        commande_id = commande.get('id') if isinstance(commande, dict) else commande.id

        try:
            distance_info = DistanceService.get_distance(livreur_id, commande_id)
            commande_data = {
                'commande': commande,
                'distance_totale': distance_info.get('distance_totale', 0),
                'temps_estime': distance_info.get('temps_estime', 0),
                'nombre_restaurants': distance_info.get('nombre_restaurants', 0),
                'error': distance_info.get('error', None)
            }
        except Exception as e:
            # En cas d'erreur de calcul de distance, on ajoute quand même la commande
            logger.error(f"Erreur calcul distance pour commande {commande_id}: {e}")
            commande_data = {
                'commande': commande,
                'distance_totale': 999,  # Distance élevée pour la mettre en fin de liste
                'temps_estime': 0,
                'nombre_restaurants': 0,
                'error': f"Erreur calcul distance: {str(e)}"
            }

        commandes_avec_distance.append(commande_data)

    # Trier les commandes par distance (les plus proches en premier)
    commandes_avec_distance.sort(key=lambda x: x['distance_totale'])

    return render(request, 'backoffice/livreurs/livreur_assigner_commande.html', {
        'livreur': livreur,
        'commandes_avec_distance': commandes_avec_distance
    })

def livreur_assigner_commande_confirmer(request, livreur_id):
    """Confirme l'attribution d'une commande à un livreur"""
    logger.info(f"Début de livreur_assigner_commande_confirmer pour livreur {livreur_id}")

    if request.method == 'POST':
        livreur = get_object_or_404(Livreur, id=livreur_id)
        commande_id = request.POST.get('commande_id')

        logger.info(f"POST reçu - livreur: {livreur_id}, commande_id: {commande_id}")

        if not commande_id:
            logger.warning("Aucune commande sélectionnée")
            messages.error(request, 'Veuillez sélectionner une commande.')
            return redirect('livreur_assigner_commande', livreur_id=livreur_id)

        try:
            logger.info(f"Tentative de création de livraison - livreur: {livreur_id}, commande: {commande_id}")
            # Utiliser le service de livraison pour créer la livraison
            result = LivraisonService.create_livraison(livreur_id, commande_id)

            logger.info(f"Résultat du service: {result}")

            if "error" in result:
                logger.error(f"Erreur du service: {result['error']}")
                messages.error(request, result["error"])
                return redirect('livreur_assigner_commande', livreur_id=livreur_id)

            # Succès
            logger.info(f"Attribution réussie, redirection vers livreurs_list")
            messages.success(request, f'Commande #{commande_id} attribuée avec succès au livreur {livreur.nom}.')
            return redirect('livreurs_list')

        except Exception as e:
            logger.error(f"Exception lors de l'attribution: {str(e)}")
            messages.error(request, f'Erreur lors de l\'attribution : {str(e)}')
            return redirect('livreur_assigner_commande', livreur_id=livreur_id)

    logger.info("Méthode non POST, redirection vers livreur_assigner_commande")
    return redirect('livreur_assigner_commande', livreur_id=livreur_id)
