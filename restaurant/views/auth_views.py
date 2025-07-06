from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from mlunch.core.models import Restaurant, RestaurantRepas, Repas, DisponibiliteRepas, Commande, CommandeRepas
from mlunch.core.services.repas_service import RepasService
import json

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
            # Récupérer la disponibilité du repas
            try:
                disponibilite = DisponibiliteRepas.objects.get(repas=repas)
                est_disponible = disponibilite.est_dispo
            except DisponibiliteRepas.DoesNotExist:
                # Si pas d'entrée, considérer comme disponible par défaut
                est_disponible = True

            plats_avec_dispo.append({
                'repas': repas,
                'est_disponible': est_disponible
            })

        # Récupérer les commandes du restaurant
        # Une commande concerne le restaurant si elle contient des repas du restaurant
        repas_ids = [rr.repas.id for rr in restaurant_repas]
        commandes_restaurant = Commande.objects.filter(
            repas_commandes__repas__id__in=repas_ids
        ).distinct().select_related('client', 'point_recup').prefetch_related(
            'repas_commandes__repas',
            'historiques__statut'
        ).order_by('-cree_le')[:10]  # Les 10 dernières commandes

        # Enrichir les commandes avec les détails
        commandes_enrichies = []
        for commande in commandes_restaurant:
            # Récupérer les repas de cette commande qui appartiennent à ce restaurant
            repas_commande = CommandeRepas.objects.filter(
                commande=commande,
                repas__id__in=repas_ids
            ).select_related('repas')

            # Calculer le total pour ce restaurant
            total_restaurant = sum(cr.repas.prix * cr.quantite for cr in repas_commande)

            # Récupérer le statut actuel de la commande
            dernier_historique = commande.historiques.order_by('-mis_a_jour_le').first()
            statut_actuel = dernier_historique.statut.appellation if dernier_historique else "En attente"

            commandes_enrichies.append({
                'commande': commande,
                'repas_commande': repas_commande,
                'total_restaurant': total_restaurant,
                'statut': statut_actuel
            })

        context = {
            'restaurant': restaurant,
            'plats_avec_dispo': plats_avec_dispo,
            'nombre_plats': len(plats_avec_dispo),
            'commandes': commandes_enrichies,
            'nombre_commandes': len(commandes_enrichies)
        }
        return render(request, 'dashboard.html', context)
    except Restaurant.DoesNotExist:
        # Si le restaurant n'existe plus, déconnecter
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

            return JsonResponse(result)

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
        statut_actuel = dernier_historique.statut if dernier_historique else None

        # Récupérer tous les statuts disponibles
        from mlunch.core.models import StatutCommande
        statuts_disponibles = StatutCommande.objects.all()

        context = {
            'restaurant': restaurant,
            'commande': commande,
            'repas_enrichis': repas_enrichis,
            'total_restaurant': total_restaurant,
            'statut_actuel': statut_actuel,
            'statuts_disponibles': statuts_disponibles
        }
        return render(request, 'commande_details.html', context)

    except (Restaurant.DoesNotExist, Commande.DoesNotExist):
        messages.error(request, 'Commande ou restaurant introuvable')
        return redirect('restaurant_dashboard')

def modifier_statut_commande(request):
    """API pour modifier le statut d'une commande"""
    if request.method == 'POST':
        if 'restaurant_id' not in request.session:
            return JsonResponse({'error': 'Non authentifié'}, status=401)

        try:
            data = json.loads(request.body)
            commande_id = data.get('commande_id')
            nouveau_statut_id = data.get('statut_id')

            if not commande_id or not nouveau_statut_id:
                return JsonResponse({'error': 'Paramètres manquants'}, status=400)

            # Vérifications de sécurité
            restaurant = Restaurant.objects.get(id=request.session['restaurant_id'])
            commande = Commande.objects.get(id=commande_id)

            # Vérifier que cette commande concerne ce restaurant
            restaurant_repas = RestaurantRepas.objects.filter(restaurant=restaurant)
            repas_ids = [rr.repas.id for rr in restaurant_repas]
            repas_commande = CommandeRepas.objects.filter(
                commande=commande,
                repas__id__in=repas_ids
            )

            if not repas_commande.exists():
                return JsonResponse({'error': 'Cette commande ne concerne pas votre restaurant'}, status=403)

            # Créer un nouvel historique de statut
            from mlunch.core.models import StatutCommande, HistoriqueStatutCommande
            nouveau_statut = StatutCommande.objects.get(id=nouveau_statut_id)

            HistoriqueStatutCommande.objects.create(
                commande=commande,
                statut=nouveau_statut
            )

            return JsonResponse({
                'success': True,
                'message': f'Statut mis à jour vers "{nouveau_statut.appellation}"',
                'nouveau_statut': nouveau_statut.appellation
            })

        except (Restaurant.DoesNotExist, Commande.DoesNotExist, StatutCommande.DoesNotExist):
            return JsonResponse({'error': 'Ressource introuvable'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Données JSON invalides'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
