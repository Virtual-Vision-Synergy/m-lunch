from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from mlunch.core.models import (
    Livreur, Zone, StatutLivreur, HistoriqueStatutLivreur,
    Livraison, StatutLivraison, HistoriqueStatutLivraison,
    ZoneLivreur
)

def livreurs_list(request):
    secteur = request.GET.get('secteur')
    statut = request.GET.get('statut')

    # Base queryset
    livreurs = Livreur.objects.all()

    # Apply filters
    if secteur:
        livreurs = livreurs.filter(zonelivreur__zone__nom=secteur)

    if statut:
        # Get current status from history
        livreurs = livreurs.filter(
            historiques__statut__appellation=statut,
            historiques__id__in=[
                hist.id for hist in HistoriqueStatutLivreur.objects.filter(
                    livreur__in=livreurs
                ).order_by('livreur', '-mis_a_jour_le').distinct('livreur')
            ]
        )

    # Get data for filters
    secteurs = Zone.objects.all()
    statuts = StatutLivreur.objects.all()

    # Add current status to each livreur
    livreurs_with_status = []
    for livreur in livreurs:
        latest_status = livreur.historiques.order_by('-mis_a_jour_le').first()
        secteur_livreur = livreur.zonelivreur_set.first()
        livreurs_with_status.append({
            'id': livreur.id,
            'nom': livreur.nom,
            'contact': livreur.contact,
            'secteur': secteur_livreur.zone.nom if secteur_livreur else 'Non défini',
            'statut': latest_status.statut.appellation if latest_status else 'Non défini',
            'date_inscri': livreur.date_inscri
        })

    return render(request, 'backoffice/livreurs/livreurs_list.html', {
        'livreurs': livreurs_with_status,
        'secteurs': secteurs,
        'statuts': statuts,
        'selected_secteur': secteur,
        'selected_statut': statut,
    })


def livreur_detail(request, livreur_id):
    livreur = get_object_or_404(Livreur, id=livreur_id)
    latest_status = livreur.historiques.order_by('-mis_a_jour_le').first()
    secteur_livreur = livreur.zonelivreur_set.first()

    livreur_data = {
        'id': livreur.id,
        'nom': livreur.nom,
        'contact': livreur.contact,
        'secteur': secteur_livreur.zone.nom if secteur_livreur else 'Non défini',
        'statut': latest_status.statut.appellation if latest_status else 'Non défini',
        'date_inscri': livreur.date_inscri,
        'position': livreur.position
    }

    return render(request, 'backoffice/livreurs/livreur_detail.html', {'livreur': livreur_data})


def livreur_add(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        contact = request.POST.get('contact')
        secteur = request.POST.get('secteur')
        statut = request.POST.get('statut')

        # Create livreur
        livreur = Livreur.objects.create(
            nom=nom,
            contact=contact
        )

        # Add zone relationship
        if secteur:
            zone = Zone.objects.get(nom=secteur)
            ZoneLivreur.objects.create(zone=zone, livreur=livreur)

        # Add status
        if statut:
            statut_obj = StatutLivreur.objects.get(appellation=statut)
            HistoriqueStatutLivreur.objects.create(livreur=livreur, statut=statut_obj)

        return redirect('livreurs_list')

    secteurs = Zone.objects.all()
    statuts = StatutLivreur.objects.all()
    return render(request, 'backoffice/livreurs/livreur_form.html', {
        'secteurs': secteurs,
        'statuts': statuts,
        'action': 'Ajouter'
    })


def livreur_edit(request, livreur_id):
    livreur = get_object_or_404(Livreur, id=livreur_id)
    latest_status = livreur.historiques.order_by('-mis_a_jour_le').first()
    secteur_livreur = livreur.zonelivreur_set.first()

    secteurs = Zone.objects.all()
    statuts = StatutLivreur.objects.all()

    livreur_data = {
        'id': livreur.id,
        'nom': livreur.nom,
        'contact': livreur.contact,
        'secteur': secteur_livreur.zone.nom if secteur_livreur else None,
        'statut': latest_status.statut.appellation if latest_status else None,
    }

    if request.method == 'POST':
        nom = request.POST.get('nom')
        contact = request.POST.get('contact')
        secteur = request.POST.get('secteur')
        statut = request.POST.get('statut')

        # Si c'est une requête AJAX, on renvoie les changements
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            changements = []

            # Verifier les changements de nom
            if livreur_data['nom'] != nom:
                changements.append({
                    'champ': 'Nom',
                    'avant': livreur_data['nom'],
                    'apres': nom
                })

            # Verifier les changements de contact
            if livreur_data['contact'] != contact:
                changements.append({
                    'champ': 'Contact',
                    'avant': livreur_data['contact'] or 'Non defini',
                    'apres': contact or 'Non defini'
                })

            # Verifier les changements de secteur
            if livreur_data['secteur'] != secteur:
                changements.append({
                    'champ': 'Secteur',
                    'avant': livreur_data['secteur'] or 'Non defini',
                    'apres': secteur
                })

            # Verifier les changements de statut
            if livreur_data['statut'] != statut:
                changements.append({
                    'champ': 'Statut',
                    'avant': livreur_data['statut'] or 'Non defini',
                    'apres': statut
                })

            return JsonResponse({'changements': changements})

        # Si confirm=1, on effectue les modifications
        if request.POST.get('confirm') == '1':
            # Update basic info
            livreur.nom = nom
            livreur.contact = contact
            livreur.save()

            # Update zone
            if secteur != livreur_data['secteur']:
                # Remove old zone relationships
                ZoneLivreur.objects.filter(livreur=livreur).delete()
                # Add new zone relationship
                if secteur:
                    zone = Zone.objects.get(nom=secteur)
                    ZoneLivreur.objects.create(zone=zone, livreur=livreur)

            # Update status
            if statut != livreur_data['statut']:
                statut_obj = StatutLivreur.objects.get(appellation=statut)
                HistoriqueStatutLivreur.objects.create(livreur=livreur, statut=statut_obj)

            return redirect('livreurs_list')

    return render(request, 'backoffice/livreurs/livreur_form.html', {
        'livreur': livreur_data,
        'secteurs': secteurs,
        'statuts': statuts,
        'action': 'Modifier'
    })


def livreur_delete(request, livreur_id):
    livreur = get_object_or_404(Livreur, id=livreur_id)

    # Check if livreur has active deliveries
    active_deliveries = livreur.livraisons.filter(
        historiques__statut__appellation__in=['En cours', 'En préparation', 'Attribuée']
    ).exists()

    if active_deliveries:
        return render(request, 'backoffice/livreurs/livreur_delete_error.html', {
            'reason': "Impossible de supprimer ce livreur : il a des livraisons en cours."
        })

    # Check if already inactive
    latest_status = livreur.historiques.order_by('-mis_a_jour_le').first()
    if latest_status and latest_status.statut.appellation == 'Inactif':
        return redirect('livreurs_list')

    if request.method == 'POST':
        # Set status to inactive instead of deleting
        statut_inactif, created = StatutLivreur.objects.get_or_create(appellation='Inactif')
        HistoriqueStatutLivreur.objects.create(livreur=livreur, statut=statut_inactif)
        return redirect('livreurs_list')

    return render(request, 'backoffice/livreurs/livreur_delete_confirm.html', {
        'livreur_id': livreur_id
    })


def livraisons_list(request):
    # Recuperer les filtres
    secteur = request.GET.get('secteur')
    statut = request.GET.get('statut')
    adresse = request.GET.get('adresse')
    livreur_id = request.GET.get('livreur')

    # Base queryset
    livraisons = Livraison.objects.select_related('livreur', 'commande', 'commande__point_recup').all()

    # Apply filters
    if secteur:
        livraisons = livraisons.filter(livreur__zonelivreur__zone__nom=secteur)

    if statut:
        livraisons = livraisons.filter(
            historiques__statut__appellation=statut,
            historiques__id__in=[
                hist.id for hist in HistoriqueStatutLivraison.objects.filter(
                    livraison__in=livraisons
                ).order_by('livraison', '-mis_a_jour_le').distinct('livraison')
            ]
        )

    if adresse:
        livraisons = livraisons.filter(
            Q(commande__point_recup__nom__icontains=adresse)
        )

    if livreur_id:
        livraisons = livraisons.filter(livreur_id=livreur_id)

    # Prepare livraisons data with current status
    livraisons_data = []
    for livraison in livraisons:
        latest_status = livraison.historiques.order_by('-mis_a_jour_le').first()
        livraisons_data.append({
            'id': livraison.id,
            'livreur_nom': livraison.livreur.nom,
            'livreur_id': livraison.livreur.id,
            'commande_id': livraison.commande.id,
            'adresse': livraison.commande.point_recup.nom,
            'statut': latest_status.statut.appellation if latest_status else 'Non défini',
            'attribue_le': livraison.attribue_le
        })

    # Recuperer les donnees pour les filtres
    secteurs = Zone.objects.all()
    statuts = StatutLivraison.objects.all()
    livreurs = Livreur.objects.all()

    return render(request, 'backoffice/livraisons/livraisons_list.html', {
        'livraisons': livraisons_data,
        'secteurs': secteurs,
        'statuts': statuts,
        'livreurs': livreurs,
        'selected_secteur': secteur,
        'selected_statut': statut,
        'selected_adresse': adresse,
        'selected_livreur': livreur_id,
    })


def livraison_detail(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id)
    latest_status = livraison.historiques.order_by('-mis_a_jour_le').first()

    livraison_data = {
        'id': livraison.id,
        'livreur_nom': livraison.livreur.nom,
        'livreur_id': livraison.livreur.id,
        'commande_id': livraison.commande.id,
        'adresse': livraison.commande.point_recup.nom,
        'statut': latest_status.statut.appellation if latest_status else 'Non défini',
        'attribue_le': livraison.attribue_le
    }

    return render(request, 'backoffice/livraisons/livraison_detail.html', {'livraison': livraison_data})


def livraison_edit(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id)
    latest_status = livraison.historiques.order_by('-mis_a_jour_le').first()

    statuts = StatutLivraison.objects.all()
    livreurs = Livreur.objects.all()

    livraison_data = {
        'id': livraison.id,
        'livreur_id': livraison.livreur.id,
        'livreur_nom': livraison.livreur.nom,
        'statut': latest_status.statut.appellation if latest_status else None,
        'commande_id': livraison.commande.id,
        'adresse': livraison.commande.point_recup.nom,
        'attribue_le': livraison.attribue_le
    }

    if request.method == 'POST':
        new_livreur_id = int(request.POST.get('livreur_id'))
        new_statut = request.POST.get('statut')

        # Si c'est une requête AJAX, on renvoie les changements
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            changements = []

            # Verifier les changements de livreur
            if livraison_data['livreur_id'] != new_livreur_id:
                new_livreur = Livreur.objects.get(id=new_livreur_id)
                changements.append({
                    'champ': 'Livreur',
                    'avant': livraison_data['livreur_nom'],
                    'apres': new_livreur.nom
                })

            # Verifier les changements de statut
            if livraison_data['statut'] != new_statut:
                changements.append({
                    'champ': 'Statut',
                    'avant': livraison_data['statut'] or 'Non defini',
                    'apres': new_statut
                })

            return JsonResponse({'changements': changements})

        # Si confirm=1, on effectue les modifications
        if request.POST.get('confirm') == '1':
            # Update status
            if new_statut != livraison_data['statut']:
                statut_obj = StatutLivraison.objects.get(appellation=new_statut)
                HistoriqueStatutLivraison.objects.create(livraison=livraison, statut=statut_obj)

            # Update livreur
            if livraison_data['livreur_id'] != new_livreur_id:
                livraison.livreur_id = new_livreur_id
                livraison.save()

            return redirect('livraisons_list')

    return render(request, 'backoffice/livraisons/livraison_form.html', {
        'livraison': livraison_data,
        'statuts': statuts,
        'livreurs': livreurs,
        'action': 'Modifier'
    })


def livraison_delete(request, livraison_id):
    try:
        livraison = get_object_or_404(Livraison, id=livraison_id)
        latest_status = livraison.historiques.order_by('-mis_a_jour_le').first()
        current_status = latest_status.statut.appellation if latest_status else None

        # Verifier si la livraison peut être annulee
        if current_status in ['Livree', 'Livrée']:
            return render(request, 'backoffice/livraisons/livraison_delete_error.html', {
                'reason': "Impossible d'annuler une livraison dejà effectuee."
            })

        if current_status in ['Annulee', 'Annulée']:
            messages.info(request, "Cette livraison est dejà annulee.")
            return redirect('livraisons_list')

        if request.method == 'POST':
            # Get or create 'Annulee' status
            statut_annule, created = StatutLivraison.objects.get_or_create(appellation='Annulée')

            # Create status history entry
            HistoriqueStatutLivraison.objects.create(livraison=livraison, statut=statut_annule)

            messages.success(request, "La livraison a ete annulee avec succès.")
            return redirect('livraisons_list')

    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('livraisons_list')

    return render(request, 'backoffice/livraisons/livraison_delete_confirm.html', {
        'livraison': {
            'id': livraison.id,
            'livreur_nom': livraison.livreur.nom,
            'commande_id': livraison.commande.id,
            'adresse': livraison.commande.point_recup.nom
        }
    })
