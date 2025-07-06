from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from mlunch.core.models import (
    Livreur, Zone, StatutLivreur, HistoriqueStatutLivreur,
    Livraison, StatutLivraison, HistoriqueStatutLivraison,
    ZoneLivreur, Commande
)

# ========== VUE PRINCIPALE UNIFIÉE ==========

def livraison_livreur_dashboard(request):
    """Vue fusionnée principale pour gérer les livraisons et les livreurs"""
    # Paramètres de filtrage
    secteur = request.GET.get('secteur')
    statut_livreur = request.GET.get('statut_livreur')
    statut_livraison = request.GET.get('statut_livraison')
    view_type = request.GET.get('view', 'livreurs')  # Par défaut afficher les livreurs

    # Données pour les filtres
    secteurs = Zone.objects.all()
    statuts_livreur = StatutLivreur.objects.all()
    statuts_livraison = StatutLivraison.objects.all()

    # Gestion des livreurs avec filtres
    livreurs = Livreur.objects.all()
    if secteur:
        livreurs = livreurs.filter(zonelivreur__zone__nom=secteur)
    if statut_livreur:
        livreurs = livreurs.filter(
            historiques__statut__appellation=statut_livreur,
            historiques__id__in=[
                hist.id for hist in HistoriqueStatutLivreur.objects.filter(
                    livreur__in=livreurs
                ).order_by('livreur', '-mis_a_jour_le').distinct('livreur')
            ]
        )

    # Préparation des données livreurs avec leurs statuts actuels
    livreurs_with_status = []
    for livreur in livreurs:
        latest_status = livreur.historiques.order_by('-mis_a_jour_le').first()
        secteur_livreur = livreur.zonelivreur_set.first()

        # Compter les livraisons en cours pour ce livreur via l'historique
        livraisons_en_cours = 0
        for livraison in livreur.livraisons.all():
            latest_livraison_status = livraison.historiques.order_by('-mis_a_jour_le').first()
            if latest_livraison_status and latest_livraison_status.statut.appellation in ['En cours', 'Assignée']:
                livraisons_en_cours += 1

        livreurs_with_status.append({
            'id': livreur.id,
            'nom': livreur.nom,
            'contact': livreur.contact,
            'secteur': secteur_livreur.zone.nom if secteur_livreur else 'Non défini',
            'statut': latest_status.statut.appellation if latest_status else 'Non défini',
            'date_inscri': livreur.date_inscri,
            'livraisons_en_cours': livraisons_en_cours
        })

    # Gestion des livraisons avec filtres
    livraisons = Livraison.objects.select_related('livreur', 'commande').all()
    if secteur:
        livraisons = livraisons.filter(livreur__zonelivreur__zone__nom=secteur)
    if statut_livraison:
        # Filtrer par statut en utilisant l'historique
        livraison_ids_with_status = []
        for livraison in livraisons:
            latest_status = livraison.historiques.order_by('-mis_a_jour_le').first()
            if latest_status and latest_status.statut.appellation == statut_livraison:
                livraison_ids_with_status.append(livraison.id)
        livraisons = livraisons.filter(id__in=livraison_ids_with_status)

    # Préparation des données livraisons
    livraisons_with_details = []
    for livraison in livraisons:
        latest_status = livraison.historiques.order_by('-mis_a_jour_le').first()
        livraisons_with_details.append({
            'id': livraison.id,
            'commande_id': livraison.commande.id if livraison.commande else None,
            'livreur_nom': livraison.livreur.nom if livraison.livreur else 'Non assigné',
            'livreur_id': livraison.livreur.id if livraison.livreur else None,
            'statut': latest_status.statut.appellation if latest_status else 'Non défini',
            'attribue_le': livraison.attribue_le,
            'adresse_livraison': livraison.commande.point_recup.nom if livraison.commande and livraison.commande.point_recup else 'Non définie'
        })

    # Récupérer les commandes non assignées pour le bouton d'assignment
    commandes_non_assignees = Commande.objects.filter(livraisons__isnull=True)

    return render(request, 'backoffice/livraison_livreur_dashboard.html', {
        'livreurs': livreurs_with_status,
        'livraisons': livraisons_with_details,
        'commandes_non_assignees': commandes_non_assignees,
        'secteurs': secteurs,
        'statuts_livreur': statuts_livreur,
        'statuts_livraison': statuts_livraison,
        'selected_secteur': secteur,
        'selected_statut_livreur': statut_livreur,
        'selected_statut_livraison': statut_livraison,
        'view_type': view_type
    })

# ========== GESTION DES ASSIGNATIONS ==========

def livreur_assigner_commande(request, livreur_id):
    """Vue pour assigner une commande à un livreur (inverse de commande_attribuer)"""
    livreur = get_object_or_404(Livreur, id=livreur_id)

    # Récupérer les commandes non assignées
    commandes_disponibles = Commande.objects.filter(livraisons__isnull=True)

    # Filtrer par secteur du livreur si nécessaire
    secteur_livreur = livreur.zonelivreur_set.first()
    if secteur_livreur:
        # Optionnel: filtrer les commandes par zone du livreur
        commandes_disponibles = commandes_disponibles.filter(
            client__zoneclient__zone=secteur_livreur.zone
        )

    if request.method == 'POST':
        commande_id = request.POST.get('commande_id')
        if commande_id:
            try:
                commande = get_object_or_404(Commande, id=commande_id)

                # Créer la livraison
                livraison = Livraison.objects.create(
                    livreur=livreur,
                    commande=commande
                )

                # Créer l'historique de statut initial
                statut_assigne, created = StatutLivraison.objects.get_or_create(
                    appellation='Assignée'
                )
                HistoriqueStatutLivraison.objects.create(
                    livraison=livraison,
                    statut=statut_assigne
                )

                messages.success(request, f"Commande #{commande.id} assignée avec succès à {livreur.nom}")
                return redirect('livraison_livreur_dashboard')

            except Exception as e:
                messages.error(request, f"Erreur lors de l'assignation: {str(e)}")

    return render(request, 'backoffice/livreur_assigner_commande.html', {
        'livreur': livreur,
        'commandes_disponibles': commandes_disponibles,
        'secteur_livreur': secteur_livreur.zone.nom if secteur_livreur else 'Non défini'
    })

# ========== GESTION INDIVIDUELLE DES LIVREURS ==========

def livreur_detail(request, livreur_id):
    """Détail d'un livreur spécifique"""
    livreur = get_object_or_404(Livreur, id=livreur_id)
    latest_status = livreur.historiques.order_by('-mis_a_jour_le').first()
    secteur_livreur = livreur.zonelivreur_set.first()

    # Récupérer les livraisons du livreur
    livraisons = livreur.livraisons.all()
    livraisons_data = []
    for livraison in livraisons:
        latest_livraison_status = livraison.historiques.order_by('-mis_a_jour_le').first()
        livraisons_data.append({
            'id': livraison.id,
            'commande_id': livraison.commande.id,
            'statut': latest_livraison_status.statut.appellation if latest_livraison_status else 'Non défini',
            'attribue_le': livraison.attribue_le,
            'adresse': livraison.commande.point_recup.nom if livraison.commande and livraison.commande.point_recup else 'Non définie'
        })

    livreur_data = {
        'id': livreur.id,
        'nom': livreur.nom,
        'contact': livreur.contact,
        'secteur': secteur_livreur.zone.nom if secteur_livreur else 'Non défini',
        'statut': latest_status.statut.appellation if latest_status else 'Non défini',
        'date_inscri': livreur.date_inscri,
        'livraisons': livraisons_data
    }

    return render(request, 'backoffice/livreurs/livreur_detail.html', {'livreur': livreur_data})

def livreur_add(request):
    """Ajouter un nouveau livreur"""
    if request.method == 'POST':
        nom = request.POST.get('nom')
        contact = request.POST.get('contact')
        secteur = request.POST.get('secteur')
        statut = request.POST.get('statut')

        try:
            # Validation des données
            if not nom:
                messages.error(request, "Le nom du livreur est obligatoire")
                raise ValueError("Nom obligatoire")

            # Créer le livreur
            livreur = Livreur.objects.create(
                nom=nom,
                contact=contact or ""
            )

            # Ajouter la relation zone
            if secteur:
                zone = Zone.objects.get(nom=secteur)
                ZoneLivreur.objects.create(zone=zone, livreur=livreur)

            # Ajouter le statut (par défaut 'Actif' si non spécifié)
            if statut:
                statut_obj = StatutLivreur.objects.get(appellation=statut)
            else:
                statut_obj, created = StatutLivreur.objects.get_or_create(appellation='Actif')

            HistoriqueStatutLivreur.objects.create(livreur=livreur, statut=statut_obj)

            messages.success(request, f"Livreur {nom} ajouté avec succès")
            return redirect('livraison_livreur_dashboard')

        except Zone.DoesNotExist:
            messages.error(request, "Secteur sélectionné introuvable")
        except StatutLivreur.DoesNotExist:
            messages.error(request, "Statut sélectionné introuvable")
        except Exception as e:
            messages.error(request, f"Erreur lors de la création: {str(e)}")

    secteurs = Zone.objects.all()
    statuts = StatutLivreur.objects.all()
    return render(request, 'backoffice/livreurs/livreur_form.html', {
        'secteurs': secteurs,
        'statuts': statuts,
        'action': 'Ajouter'
    })

def livreur_edit(request, livreur_id):
    """Modifier un livreur existant"""
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

            if livreur_data['nom'] != nom:
                changements.append({
                    'champ': 'Nom',
                    'avant': livreur_data['nom'],
                    'apres': nom
                })

            if livreur_data['contact'] != contact:
                changements.append({
                    'champ': 'Contact',
                    'avant': livreur_data['contact'] or 'Non défini',
                    'apres': contact or 'Non défini'
                })

            if livreur_data['secteur'] != secteur:
                changements.append({
                    'champ': 'Secteur',
                    'avant': livreur_data['secteur'] or 'Non défini',
                    'apres': secteur
                })

            if livreur_data['statut'] != statut:
                changements.append({
                    'champ': 'Statut',
                    'avant': livreur_data['statut'] or 'Non défini',
                    'apres': statut
                })

            return JsonResponse({'changements': changements})

        # Si confirm=1, on effectue les modifications
        if request.POST.get('confirm') == '1':
            # Mettre à jour les infos de base
            livreur.nom = nom
            livreur.contact = contact
            livreur.save()

            # Mettre à jour la zone
            if secteur != livreur_data['secteur']:
                ZoneLivreur.objects.filter(livreur=livreur).delete()
                if secteur:
                    zone = Zone.objects.get(nom=secteur)
                    ZoneLivreur.objects.create(zone=zone, livreur=livreur)

            # Mettre à jour le statut
            if statut != livreur_data['statut']:
                statut_obj = StatutLivreur.objects.get(appellation=statut)
                HistoriqueStatutLivreur.objects.create(livreur=livreur, statut=statut_obj)

            messages.success(request, f"Livreur {nom} modifié avec succès")
            return redirect('livraison_livreur_dashboard')

    return render(request, 'backoffice/livreurs/livreur_form.html', {
        'livreur': livreur_data,
        'secteurs': secteurs,
        'statuts': statuts,
        'action': 'Modifier'
    })

def livreur_delete(request, livreur_id):
    """Supprimer/Désactiver un livreur"""
    livreur = get_object_or_404(Livreur, id=livreur_id)

    # Vérifier s'il a des livraisons en cours
    active_deliveries = livreur.livraisons.filter(
        historiques__statut__appellation__in=['En cours', 'En préparation', 'Assignée']
    ).exists()

    if active_deliveries:
        messages.error(request, "Impossible de supprimer ce livreur : il a des livraisons en cours.")
        return redirect('livraison_livreur_dashboard')

    # Vérifier s'il est déjà inactif
    latest_status = livreur.historiques.order_by('-mis_a_jour_le').first()
    if latest_status and latest_status.statut.appellation == 'Inactif':
        messages.info(request, "Ce livreur est déjà inactif.")
        return redirect('livraison_livreur_dashboard')

    if request.method == 'POST':
        # Mettre le statut à inactif au lieu de supprimer
        statut_inactif, created = StatutLivreur.objects.get_or_create(appellation='Inactif')
        HistoriqueStatutLivreur.objects.create(livreur=livreur, statut=statut_inactif)
        messages.success(request, f"Livreur {livreur.nom} désactivé avec succès")
        return redirect('livraison_livreur_dashboard')

    return render(request, 'backoffice/livreurs/livreur_delete_confirm.html', {
        'livreur': livreur
    })

# ========== GESTION INDIVIDUELLE DES LIVRAISONS ==========

def livraison_detail(request, livraison_id):
    """Détail d'une livraison spécifique"""
    livraison = get_object_or_404(Livraison, id=livraison_id)
    latest_status = livraison.historiques.order_by('-mis_a_jour_le').first()

    livraison_data = {
        'id': livraison.id,
        'livreur_nom': livraison.livreur.nom,
        'livreur_id': livraison.livreur.id,
        'commande_id': livraison.commande.id,
        'adresse': livraison.commande.point_recup.nom,
        'statut': latest_status.statut.appellation if latest_status else 'Non défini',
        'attribue_le': livraison.attribue_le,
        'historique': livraison.historiques.order_by('-mis_a_jour_le').all()
    }

    return render(request, 'backoffice/livraisons/livraison_detail.html', {'livraison': livraison_data})

def livraison_edit(request, livraison_id):
    """Modifier une livraison existante"""
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

            if livraison_data['livreur_id'] != new_livreur_id:
                new_livreur = Livreur.objects.get(id=new_livreur_id)
                changements.append({
                    'champ': 'Livreur',
                    'avant': livraison_data['livreur_nom'],
                    'apres': new_livreur.nom
                })

            if livraison_data['statut'] != new_statut:
                changements.append({
                    'champ': 'Statut',
                    'avant': livraison_data['statut'] or 'Non défini',
                    'apres': new_statut
                })

            return JsonResponse({'changements': changements})

        # Si confirm=1, on effectue les modifications
        if request.POST.get('confirm') == '1':
            # Mettre à jour le statut
            if new_statut != livraison_data['statut']:
                statut_obj = StatutLivraison.objects.get(appellation=new_statut)
                HistoriqueStatutLivraison.objects.create(livraison=livraison, statut=statut_obj)

            # Mettre à jour le livreur
            if livraison_data['livreur_id'] != new_livreur_id:
                livraison.livreur_id = new_livreur_id
                livraison.save()

            messages.success(request, "Livraison modifiée avec succès")
            return redirect('livraison_livreur_dashboard')

    return render(request, 'backoffice/livraisons/livraison_form.html', {
        'livraison': livraison_data,
        'statuts': statuts,
        'livreurs': livreurs,
        'action': 'Modifier'
    })

def livraison_delete(request, livraison_id):
    """Annuler une livraison"""
    try:
        livraison = get_object_or_404(Livraison, id=livraison_id)
        latest_status = livraison.historiques.order_by('-mis_a_jour_le').first()
        current_status = latest_status.statut.appellation if latest_status else None

        # Vérifier si la livraison peut être annulée
        if current_status in ['Livrée', 'Livrée']:
            messages.error(request, "Impossible d'annuler une livraison déjà effectuée.")
            return redirect('livraison_livreur_dashboard')

        if current_status in ['Annulée', 'Annulée']:
            messages.info(request, "Cette livraison est déjà annulée.")
            return redirect('livraison_livreur_dashboard')

        if request.method == 'POST':
            # Créer ou récupérer le statut 'Annulée'
            statut_annule, created = StatutLivraison.objects.get_or_create(appellation='Annulée')

            # Créer l'entrée d'historique
            HistoriqueStatutLivraison.objects.create(livraison=livraison, statut=statut_annule)

            messages.success(request, "La livraison a été annulée avec succès.")
            return redirect('livraison_livreur_dashboard')

    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('livraison_livreur_dashboard')

    return render(request, 'backoffice/livraisons/livraison_delete_confirm.html', {
        'livraison': {
            'id': livraison.id,
            'livreur_nom': livraison.livreur.nom,
            'commande_id': livraison.commande.id,
            'adresse': livraison.commande.point_recup.nom
        }
    })
