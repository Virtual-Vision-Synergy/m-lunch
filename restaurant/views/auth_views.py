from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from mlunch.core.models import Restaurant, RestaurantRepas, Repas, DisponibiliteRepas, Commande, CommandeRepas, TypeRepas
from mlunch.core.services.commande_service import CommandeService
from mlunch.core.services.repas_service import RepasService
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from mlunch.core.services.suivisCommande_service import SuivisCommandeService
from mlunch.core.models import StatutCommande, HistoriqueStatutCommande
# Générer un nom de fichier unique
import os
from django.utils.text import slugify
from datetime import datetime
from django.conf import settings


def login_view(request):
    """Affiche la page de connexion pour les restaurants"""
    return render(request, 'login.html')

def login(request):
    """Traite la connexion d'un restaurant"""
    if request.method == 'POST':
        nom = request.POST.get('nom')
        mot_de_passe = request.POST.get('mot_de_passe')

        if not nom or not mot_de_passe:
            messages.error(request, 'Veuillez remplir tous les champs')
            return render(request, 'login.html')

        try:
            restaurant = Restaurant.objects.get(nom=nom)

            if restaurant.mot_de_passe == mot_de_passe:
                request.session['restaurant_id'] = restaurant.id
                request.session['restaurant_nom'] = restaurant.nom

                messages.success(request, f'Connexion réussie! Bienvenue {restaurant.nom}')
                return redirect('restaurant_dashboard')
            else:
                messages.error(request, 'Nom ou mot de passe incorrect')

        except Restaurant.DoesNotExist:
            messages.error(request, 'Nom ou mot de passe incorrect')
        except Exception as e:
            messages.error(request, f'Erreur lors de la connexion: {str(e)}')

    return render(request, 'login.html')

def logout(request):
    """Déconnecte le restaurant"""
    if 'restaurant_id' in request.session:
        del request.session['restaurant_id']
    if 'restaurant_nom' in request.session:
        del request.session['restaurant_nom']

    messages.success(request, 'Déconnexion réussie')
    return redirect('restaurant_login')

def dashboard_view(request):
    """Tableau de bord du restaurant (nécessite une connexion)"""
    if 'restaurant_id' not in request.session:
        messages.error(request, 'Veuillez vous connecter pour accéder au tableau de bord')
        return redirect('restaurant_login')

    try:
        restaurant = Restaurant.objects.get(id=request.session['restaurant_id'])

        # Récupérer les plats du restaurant avec leur disponibilité
        restaurant_repas = RestaurantRepas.objects.filter(restaurant=restaurant).select_related('repas', 'repas__type')
        plats_avec_dispo = []

        for rr in restaurant_repas:
            repas = rr.repas
            # Récupérer la disponibilité du repas (dernière entrée uniquement)
            disponibilite = DisponibiliteRepas.objects.filter(repas=repas).order_by('-mis_a_jour_le').first()

            # Définir la disponibilité basée sur le résultat
            if disponibilite:
                est_disponible = disponibilite.est_dispo
            else:
                # Si pas d'entrée, considérer comme disponible par défaut
                est_disponible = True

            plats_avec_dispo.append({
                'repas': repas,
                'est_disponible': est_disponible
            })

        repas_ids = [rr.repas.id for rr in restaurant_repas]

        # Import des modèles et fonctions nécessaires
        from django.db.models import OuterRef, Subquery
        from mlunch.core.models import StatutCommande, HistoriqueStatutCommande, Commande

        # Récupérer tous les statuts "en preparation" et "en cours"
        statuts_cibles = StatutCommande.objects.filter(appellation__in=["En preparation", "En cours","En attente"])

        # Sous-requête : statut du dernier historique pour chaque commande
        dernier_historique_statut = HistoriqueStatutCommande.objects.filter(
            commande=OuterRef('pk')
        ).order_by('-mis_a_jour_le').values('statut')[:1]

        commandes_en_attente = Commande.objects.filter(
            repas_commandes__repas__id__in=repas_ids,
        ).annotate(
            dernier_statut=Subquery(dernier_historique_statut)
        ).filter(
            dernier_statut__in=statuts_cibles.values_list('id', flat=True)
        ).distinct().select_related('client', 'point_recup').prefetch_related(
            'repas_commandes__repas',
            'historiques__statut'
        ).order_by('-cree_le')[:10]

        # Enrichir les commandes avec les détails
        commandes_enrichies = []
        for commande in commandes_en_attente:
            repas_commande = CommandeRepas.objects.filter(
                commande=commande,
                repas__id__in=repas_ids
            ).select_related('repas')

            total_restaurant = sum(cr.repas.prix * cr.quantite for cr in repas_commande)

            dernier_historique = commande.historiques.order_by('-mis_a_jour_le').first()
            statut_actuel = dernier_historique.statut.appellation if dernier_historique else "En attente"

            commandes_enrichies.append({
                'commande': commande,
                'repas_commande': repas_commande,
                'total_restaurant': total_restaurant,
                'statut': statut_actuel
            })

        # Récupérer le dernier statut du restaurant
        dernier_statut = restaurant.historiques.order_by('-mis_a_jour_le').first()
        statut_resto = dernier_statut.statut.appellation.lower() if dernier_statut and dernier_statut.statut and dernier_statut.statut.appellation else "inconnu"

        context = {
            'restaurant': restaurant,
            'plats_avec_dispo': plats_avec_dispo,
            'nombre_plats': len(plats_avec_dispo),
            'commandes': commandes_enrichies,
            'nombre_commandes': len(commandes_enrichies),
            'statut_resto': statut_resto
        }
        return render(request, 'dashboard.html', context)

    except Restaurant.DoesNotExist:
        del request.session['restaurant_id']
        del request.session['restaurant_nom']
        messages.error(request, 'Restaurant introuvable')
        return redirect('restaurant_login')


def toggle_disponibilite_repas(request):
    """API pour changer la disponibilité d'un repas"""
    if request.method == 'POST':
        if 'restaurant_id' not in request.session:
            return JsonResponse({'error': 'Non authentifié'}, status=401)

        try:
            data = json.loads(request.body)
            repas_id = data.get('repas_id')

            if not repas_id:
                return JsonResponse({'error': 'ID du repas manquant'}, status=400)

            restaurant_id = request.session['restaurant_id']
            result = RepasService.switch_disponibilite(repas_id, restaurant_id)

            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=400)

            # Reformater la réponse pour être cohérente
            response_data = {
                'success': result.get('success', True),
                'repas_id': result.get('repas_id', repas_id),
                'nouvelle_disponibilite': result.get('nouvelle_disponibilite', False),
                'message': result.get('message', 'Disponibilité mise à jour')
            }

            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Données JSON invalides'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def commande_details_view(request, commande_id):
    """Affiche les détails d'une commande pour le restaurant"""
    if 'restaurant_id' not in request.session:
        messages.error(request, 'Veuillez vous connecter pour accéder à cette page')
        return redirect('restaurant_login')

    try:
        restaurant = Restaurant.objects.get(id=request.session['restaurant_id'])
        commande = Commande.objects.get(id=commande_id)

        # Vérifier que cette commande concerne ce restaurant
        restaurant_repas = RestaurantRepas.objects.filter(restaurant=restaurant)
        repas_ids = [rr.repas.id for rr in restaurant_repas]

        # Récupérer les plats de cette commande qui appartiennent à ce restaurant
        repas_commande = CommandeRepas.objects.filter(
            commande=commande,
            repas__id__in=repas_ids
        ).select_related('repas', 'repas__type')

        if not repas_commande.exists():
            messages.error(request, 'Cette commande ne concerne pas votre restaurant')
            return redirect('restaurant_dashboard')

        # Enrichir les données avec les sous-totaux
        repas_enrichis = []
        total_restaurant = 0

        for repas_cmd in repas_commande:
            sous_total = repas_cmd.repas.prix * repas_cmd.quantite
            total_restaurant += sous_total

            repas_enrichis.append({
                'repas_cmd': repas_cmd,
                'sous_total': sous_total
            })

        # Récupérer le statut actuel de la commande
        dernier_historique = commande.historiques.order_by('-mis_a_jour_le').first()

        suivi_data = SuivisCommandeService.get_suivi(commande_id=commande.id, restaurant_id=restaurant.id)
        suivi_statut = suivi_data.get("statut", False) if isinstance(suivi_data, dict) else False
    
        context = {
            'restaurant': restaurant,
            'commande': commande,
            'repas_enrichis': repas_enrichis,
            'total_restaurant': total_restaurant,
            'suivi_statut': suivi_statut
        }
        return render(request, 'commande_details.html', context)

    except (Restaurant.DoesNotExist, Commande.DoesNotExist):
        messages.error(request, 'Commande ou restaurant introuvable')
        return redirect('restaurant_dashboard')

def modifier_statut_commande(request, commande_id):
    """Modifier le statut d'une commande et rediriger vers dashboard"""

    if request.method == 'POST':
        if 'restaurant_id' not in request.session:
            messages.error(request, "Non authentifié")
            return redirect('restaurant_login')

        try:
            restaurant = Restaurant.objects.get(id=request.session['restaurant_id'])
            commande = Commande.objects.get(id=commande_id)

            # Vérifier que la commande appartient bien à ce restaurant
            restaurant_repas = RestaurantRepas.objects.filter(restaurant=restaurant)
            repas_ids = [rr.repas.id for rr in restaurant_repas]
            repas_commande = CommandeRepas.objects.filter(
                commande=commande,
                repas__id__in=repas_ids
            )

            if not repas_commande.exists():
                messages.error(request, "Cette commande ne concerne pas votre restaurant")
                return redirect('restaurant_dashboard')

            # Mettre à jour le statut
            nouveau_statut = StatutCommande.objects.get(appellation="en preparation")

            HistoriqueStatutCommande.objects.create(
                commande=commande,
                statut=nouveau_statut
            )

            messages.success(request, f'Statut mis à jour vers "{nouveau_statut.appellation}"')
            return redirect('restaurant_dashboard')

        except (Restaurant.DoesNotExist, Commande.DoesNotExist, StatutCommande.DoesNotExist):
            messages.error(request, "Ressource introuvable")
            return redirect('restaurant_dashboard')

    # Pour GET ou autre méthode, on redirige vers dashboard
    return redirect('restaurant_dashboard')

@csrf_exempt
def modifier_statut_suivis(request):
    if request.method == 'POST':
        if 'restaurant_id' not in request.session:
            messages.error(request, 'Veuillez vous connecter pour effectuer cette action')
            return redirect('restaurant_login')

        try:
            commande_id = request.POST.get('commande_id')
            restaurant_id = request.session['restaurant_id']

            if not commande_id:
                messages.error(request, 'ID de la commande manquant')
                return redirect('restaurant_dashboard')

            # Vérifier que la commande existe
            try:
                commande = Commande.objects.get(id=commande_id)
            except Commande.DoesNotExist:
                messages.error(request, 'Commande introuvable')
                return redirect('restaurant_dashboard')

            # Vérifier que le restaurant existe
            try:
                restaurant = Restaurant.objects.get(id=restaurant_id)
            except Restaurant.DoesNotExist:
                messages.error(request, 'Restaurant introuvable')
                return redirect('restaurant_login')

            # Appeler le service pour changer le statut
            result = SuivisCommandeService.changer_statut(commande_id, restaurant_id)

            if 'error' in result:
                messages.error(request, f'Erreur lors du changement de statut: {result["error"]}')
                return redirect('restaurant_dashboard')

            # Changement automatique de l'état de la commande
            try:
                CommandeService.change_state_auto(commande_id)
            except Exception as e:
                # Ne pas bloquer si le changement automatique échoue, mais logger
                messages.warning(request, 'Statut mis à jour mais synchronisation automatique échouée')

            messages.success(request, 'Statut de la commande mis à jour avec succès')
            return redirect('restaurant_dashboard')

        except Exception as e:
            messages.error(request, f'Erreur inattendue lors de la mise à jour: {str(e)}')
            return redirect('restaurant_dashboard')

    messages.error(request, 'Méthode non autorisée')
    return redirect('restaurant_dashboard')

def form_modif_restaurant(request):
    """Affiche le formulaire de modification du restaurant"""
    if 'restaurant_id' not in request.session:
        messages.error(request, 'Veuillez vous connecter pour accéder à cette page')
        return redirect('restaurant_login')
    
    try:
        restaurant_id = request.session.get('restaurant_id')
        restaurant = Restaurant.objects.get(id=restaurant_id)
        
        context = {
            'restaurant': restaurant
        }
        return render(request, 'form-modification-restaurant.html', context)
        
    except Restaurant.DoesNotExist:
        messages.error(request, 'Restaurant introuvable')
        return redirect('restaurant_login')
    except Exception as e:
        messages.error(request, f'Erreur lors du chargement: {str(e)}')
        return redirect('restaurant_dashboard')

def modifer_restaurant(request):
    """Traite la modification des informations du restaurant"""
    if request.method == 'POST':
        if 'restaurant_id' not in request.session:
            messages.error(request, 'Veuillez vous connecter')
            return redirect('restaurant_login')

        try:
            restaurant = Restaurant.objects.get(id=request.session['restaurant_id'])
            
            # Récupération des données du formulaire
            adresse = request.POST.get('adresse', '').strip()
            description = request.POST.get('description', '').strip()
            image_file = request.FILES.get('image')
            
            # Gestion de l'upload d'image
            image_path = restaurant.image  # Conserver l'image actuelle par défaut
            if image_file:
                # Vérifier le type de fichier
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg']
                if image_file.content_type not in allowed_types:
                    messages.error(request, 'Type de fichier non supporté. Utilisez JPG, PNG ou GIF.')
                    return redirect('modifier_restaurant')
                
                # Vérifier la taille du fichier (max 5MB)
                if image_file.size > 5 * 1024 * 1024:
                    messages.error(request, 'L\'image ne doit pas dépasser 5MB.')
                    return redirect('modifier_restaurant')
                
                # Créer le répertoire s'il n'existe pas
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'restaurants')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Générer le nom du fichier
                nom_fichier = slugify(restaurant.nom)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                extension = os.path.splitext(image_file.name)[1]
                nom_complet = f"{nom_fichier}_{timestamp}{extension}"
                
                # Sauvegarder le fichier
                chemin_complet = os.path.join(upload_dir, nom_complet)
                with open(chemin_complet, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
                
                # Stocker seulement le nom du fichier avec extension dans la base de données
                image_path = nom_complet
            
            # Mise à jour des champs
            restaurant.adresse = adresse or None
            restaurant.description = description or None
            restaurant.image = image_path
            # La position géographique reste inchangée
            
            restaurant.save()
            
            messages.success(request, 'Informations du restaurant mises à jour avec succès!')
            return redirect('restaurant_dashboard')
            
        except Restaurant.DoesNotExist:
            messages.error(request, 'Restaurant introuvable')
            return redirect('restaurant_login')
        except Exception as e:
            messages.error(request, f'Erreur lors de la mise à jour: {str(e)}')
            return redirect('modifier_restaurant')
    
    # Si ce n'est pas une requête POST, rediriger vers le formulaire
    return redirect('modifier_restaurant')

def ajouter_plat_form(request):
    """Affiche le formulaire d'ajout de plat"""
    if 'restaurant_id' not in request.session:
        messages.error(request, 'Veuillez vous connecter pour accéder à cette page')
        return redirect('restaurant_login')
    
    try:
        restaurant = Restaurant.objects.get(id=request.session['restaurant_id'])
        types_repas = TypeRepas.objects.all()
        
        context = {
            'restaurant': restaurant,
            'types_repas': types_repas
        }
        return render(request, 'ajouter-plat.html', context)
        
    except Restaurant.DoesNotExist:
        messages.error(request, 'Restaurant introuvable')
        return redirect('restaurant_login')

def ajouter_plat(request):
    """Traite l'ajout d'un nouveau plat"""
    if request.method == 'POST':
        if 'restaurant_id' not in request.session:
            messages.error(request, 'Veuillez vous connecter')
            return redirect('restaurant_login')

        try:
            restaurant = Restaurant.objects.get(id=request.session['restaurant_id'])
            
            # Récupération des données du formulaire
            nom = request.POST.get('nom')
            description = request.POST.get('description')
            prix = request.POST.get('prix')
            type_id = request.POST.get('type_repas')
            image_file = request.FILES.get('image')
            
            # Validation
            if not nom or not prix or not type_id:
                messages.error(request, 'Veuillez remplir tous les champs obligatoires')
                return redirect('ajouter_plat')
            
            try:
                prix = int(prix)
                type_repas = TypeRepas.objects.get(id=type_id)
            except (ValueError, TypeRepas.DoesNotExist):
                messages.error(request, 'Données invalides')
                return redirect('ajouter_plat')
            
            # Gestion de l'upload d'image
            image_path = None
            if image_file:
                # Vérifier le type de fichier
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg']
                if image_file.content_type not in allowed_types:
                    messages.error(request, 'Type de fichier non supporté. Utilisez JPG, PNG ou GIF.')
                    return redirect('ajouter_plat')
                
                # Vérifier la taille du fichier (max 5MB)
                if image_file.size > 5 * 1024 * 1024:
                    messages.error(request, 'L\'image ne doit pas dépasser 5MB.')
                    return redirect('ajouter_plat')
                
                # Créer le répertoire s'il n'existe pas
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'plats')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Générer le nom du fichier
                nom_fichier = slugify(nom)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                extension = os.path.splitext(image_file.name)[1]
                nom_complet = f"{nom_fichier}_{timestamp}{extension}"
                
                # Sauvegarder le fichier
                chemin_complet = os.path.join(upload_dir, nom_complet)
                with open(chemin_complet, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
                
                # Stocker seulement le nom du fichier avec extension dans la base de données
                image_path = nom_complet
            
            # Création du repas
            repas = Repas.objects.create(
                nom=nom,
                description=description,
                prix=prix,
                type=type_repas,
                image=image_path
            )
            
            # Liaison avec le restaurant
            RestaurantRepas.objects.create(
                restaurant=restaurant,
                repas=repas
            )
            
            # Création de la disponibilité par défaut
            DisponibiliteRepas.objects.create(
                repas=repas,
                est_dispo=True
            )
            
            messages.success(request, f'Plat "{nom}" ajouté avec succès!')
            return redirect('restaurant_dashboard')
            
        except Restaurant.DoesNotExist:
            messages.error(request, 'Restaurant introuvable')
            return redirect('restaurant_login')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')
            return redirect('ajouter_plat')
    
    return redirect('ajouter_plat')

def changer_statut_restaurant(request):
    """Change le statut du restaurant (actif/inactif) avec vérifications"""
    if request.method == 'POST':
        if 'restaurant_id' not in request.session:
            messages.error(request, 'Veuillez vous connecter')
            return redirect('restaurant_login')

        try:
            restaurant = Restaurant.objects.get(id=request.session['restaurant_id'])
            
            # Récupérer le statut actuel du restaurant
            dernier_statut = restaurant.historiques.order_by('-mis_a_jour_le').first()
            statut_actuel = dernier_statut.statut.appellation.lower() if dernier_statut else 'inconnu'
            
            # Vérifier s'il y a des commandes en cours, en préparation ou en livraison
            # Récupérer toutes les commandes liées aux repas de ce restaurant
            commandes_restaurant = Commande.objects.filter(
                repas_commandes__repas__restaurants_repas__restaurant=restaurant
            ).distinct()
            
            # Vérifier les statuts des commandes
            statuts_bloquants = ['En cours', 'En préparation', 'En livraison']
            commandes_bloquantes = []
            
            for commande in commandes_restaurant:
                dernier_statut_commande = commande.historiques.order_by('-mis_a_jour_le').first()
                if dernier_statut_commande and dernier_statut_commande.statut.appellation in statuts_bloquants:
                    commandes_bloquantes.append(commande)
            
            # Si le restaurant est actif et qu'il y a des commandes en cours
            if statut_actuel == 'actif' and commandes_bloquantes:
                messages.error(request, 
                    f'Impossible de désactiver le restaurant. '
                    f'Il y a {len(commandes_bloquantes)} commande(s) en cours, '
                    f'en préparation ou en livraison.')
                return redirect('restaurant_dashboard')
            
            # Déterminer le nouveau statut
            if statut_actuel == 'actif':
                nouveau_statut_nom = 'Inactif'
                message_succes = 'Restaurant désactivé avec succès'
            else:
                nouveau_statut_nom = 'Actif'
                message_succes = 'Restaurant activé avec succès'
            
            # Récupérer ou créer le statut
            from mlunch.core.models import StatutRestaurant, HistoriqueStatutRestaurant
            nouveau_statut, created = StatutRestaurant.objects.get_or_create(
                appellation=nouveau_statut_nom
            )
            
            # Créer l'historique du nouveau statut
            HistoriqueStatutRestaurant.objects.create(
                restaurant=restaurant,
                statut=nouveau_statut
            )
            
            messages.success(request, message_succes)
            return redirect('restaurant_dashboard')
            
        except Restaurant.DoesNotExist:
            messages.error(request, 'Restaurant introuvable')
            return redirect('restaurant_login')
        except Exception as e:
            messages.error(request, f'Erreur lors du changement de statut: {str(e)}')
            return redirect('restaurant_dashboard')
    
    return redirect('restaurant_dashboard')
