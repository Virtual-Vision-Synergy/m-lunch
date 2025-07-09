from django.db.models import Sum, F
from django.utils.timezone import now
from ..models import (
    Repas, RestaurantRepas, PointRecup, DisponibiliteRepas,
    Commande, CommandeRepas, HistoriqueStatutCommande, StatutCommande, ModePaiement
)


class PanierService:
    """
    Service pour gérer le panier en utilisant les sessions Django
    """

    @staticmethod
    def get_panier_items(client_id):
        """
        Récupère les articles du panier (commande en cours) depuis la base de données.
        """
        try:
            # Chercher la commande en cours (statut_id=1)
            commande = None
            commandes = Commande.objects.filter(client_id=client_id)
            for c in commandes:
                last_statut = c.historiques.order_by('-mis_a_jour_le').first()
                if last_statut and last_statut.statut_id == 1:
                    commande = c
                    break

            if not commande:
                return []

            items = []
            commande_repas = CommandeRepas.objects.filter(commande=commande).select_related('repas')
            for cr in commande_repas:
                repas = cr.repas
                # On récupère le premier restaurant associé au repas (si plusieurs)
                restaurant_repas = RestaurantRepas.objects.filter(repas=repas).select_related('restaurant').first()
                restaurant_nom = restaurant_repas.restaurant.nom if restaurant_repas else ""
                items.append({
                    'item_id': cr.id,
                    'repas_id': repas.id,
                    'nom': repas.nom,
                    'prix': repas.prix,
                    'quantite': cr.quantite,
                    'restaurant_nom': restaurant_nom,
                    'image': repas.image,
                    'total': cr.quantite * repas.prix
                })

            return items

        except Exception as e:
            return {"error": f"Erreur lors de la récupération du panier : {str(e)}"}
        
    @staticmethod
    def calculate_totals(client_id):
        """
        Calcule les totaux du panier
        """
        try:
            items = PanierService.get_panier_items(client_id)

            if isinstance(items, dict) and 'error' in items:
                return items

            sous_total = sum(item.get('total', 0) for item in items)
            frais_livraison = 3000  # Frais fixes pour l'exemple
            total = sous_total + frais_livraison

            return {
                'sous_total': sous_total,
                'frais_livraison': frais_livraison,
                'total': total,
                'nb_items': len(items)
            }

        except Exception as e:
            return {"error": f"Erreur lors du calcul des totaux : {str(e)}"}

    @staticmethod
    def add_to_panier(client_id, repas_id, quantite=1):
        """
        Ajoute un repas au panier (à implémenter avec session ou base de données)
        """
        try:
            # Vérifier que le repas existe et est disponible
            repas = Repas.objects.get(id=repas_id)

            # Vérifier la disponibilité
            is_dispo = DisponibiliteRepas.objects.filter(
                repas=repas,
                est_dispo=True
            ).exists()

            if not is_dispo:
                return {"error": "Ce repas n'est pas disponible actuellement"}

            # Récupérer le restaurant qui propose ce repas
            restaurant_repas = RestaurantRepas.objects.filter(repas=repas).first()
            if not restaurant_repas:
                return {"error": "Restaurant non trouvé pour ce repas"}

            restaurant = restaurant_repas.restaurant

            # --- Nouvelle logique pour commande/statut ---
            from django.db import transaction
            
            with transaction.atomic():
                # Chercher une commande existante avec statut_id=1 (dernier statut)
                commande = None
                commandes = Commande.objects.filter(client_id=client_id)
                for c in commandes:
                    last_statut = c.historiques.order_by('-mis_a_jour_le').first()
                    if last_statut and last_statut.statut_id == 1:
                        commande = c
                        break
                if not commande:
                    # Créer une nouvelle commande
                    commande = Commande.objects.create(client_id=client_id, point_recup_id=None)
                    # Ajouter le statut initial (id=1)
                    HistoriqueStatutCommande.objects.create(commande=commande, statut_id=1)
                # Ajouter ou mettre à jour le repas dans commande_repas
                cr, created = CommandeRepas.objects.get_or_create(
                    commande=commande,
                    repas=repas,
                    defaults={'quantite': quantite}
                )
                if not created:
                    cr.quantite += quantite
                    cr.save()

            return {
                "success": True,
                "message": f"{repas.nom} ajouté au panier",
                "repas": {
                    "id": repas.id,
                    "nom": repas.nom,
                    "prix": repas.prix,
                    "restaurant": restaurant.nom
                }
            }

        except Repas.DoesNotExist:
            return {"error": "Repas non trouvé"}
        except Exception as e:
            return {"error": f"Erreur lors de l'ajout au panier : {str(e)}"}
        
    @staticmethod
    def get_points_recuperation():
        """
        Récupère tous les points de récupération disponibles
        """
        try:
            points = PointRecup.objects.all().values('id', 'nom', 'geo_position')
            return list(points)

        except Exception as e:
            return {"error": f"Erreur lors de la récupération des points de récupération : {str(e)}"}

    
    @staticmethod
    def remove_from_panier(client_id, item_id):
        """
        Supprime un article du panier (commande en cours) pour le client donné.
        """
        try:
            # Trouver la commande en cours (statut_id=1)
            commande = None
            commandes = Commande.objects.filter(client_id=client_id)
            for c in commandes:
                last_statut = c.historiques.order_by('-mis_a_jour_le').first()
                if last_statut and last_statut.statut_id == 1:
                    commande = c
                    break
    
            if not commande:
                return {"error": "Aucune commande en cours trouvée."}
    
            # Supprimer l'article CommandeRepas correspondant
            deleted, _ = CommandeRepas.objects.filter(id=item_id, commande=commande).delete()
            if deleted == 0:
                return {"error": "Article non trouvé dans le panier."}
    
            return {"success": True, "message": "Article supprimé du panier"}
    
        except Exception as e:
            return {"error": f"Erreur lors de la suppression : {str(e)}"}

    @staticmethod
    def clear_panier(client_id):
        """
        Vide le panier
        """
        try:
            # Logique de vidage à implémenter
            return {"success": True, "message": "Panier vidé"}

        except Exception as e:
            return {"error": f"Erreur lors du vidage du panier : {str(e)}"}

    @staticmethod
    def update_quantity(client_id, item_id, nouvelle_quantite):
        """
        Met à jour la quantité d'un article dans le panier
        """
        try:
            if nouvelle_quantite <= 0:
                return PanierService.remove_from_panier(client_id, item_id)

            # Trouver la commande en cours (statut_id=1)
            commande = None
            commandes = Commande.objects.filter(client_id=client_id)
            for c in commandes:
                last_statut = c.historiques.order_by('-mis_a_jour_le').first()
                if last_statut and last_statut.statut_id == 1:
                    commande = c
                    break

            if not commande:
                return {"error": "Aucune commande en cours trouvée."}

            # Trouver l'article à mettre à jour
            try:
                cr = CommandeRepas.objects.get(id=item_id, commande=commande)
            except CommandeRepas.DoesNotExist:
                return {"error": "Article non trouvé dans le panier."}

            cr.quantite = nouvelle_quantite
            cr.save()

            return {"success": True, "message": "Quantité mise à jour"}

        except Exception as e:
            return {"error": f"Erreur lors de la mise à jour : {str(e)}"}

    @staticmethod
    def get_panier_restaurants(client_id):
        """
        Récupère la liste des restaurants présents dans le panier
        """
        try:
            items = PanierService.get_panier_items(client_id)

            if isinstance(items, dict) and 'error' in items:
                return items

            restaurants = list(set(item.get('restaurant_nom', '') for item in items))
            return restaurants

        except Exception as e:
            return {"error": f"Erreur lors de la récupération des restaurants : {str(e)}"}

    @staticmethod
    def validate_panier_for_checkout(client_id):
        """
        Valide le panier avant la commande
        """
        try:
            items = PanierService.get_panier_items(client_id)

            if isinstance(items, dict) and 'error' in items:
                return items

            if not items:
                return {"error": "Le panier est vide"}

            # Vérifier que tous les articles sont encore disponibles
            for item in items:
                repas = Repas.objects.get(id=item['repas_id'])
                is_dispo = DisponibiliteRepas.objects.filter(
                    repas=repas,
                    est_dispo=True
                ).exists()

                if not is_dispo:
                    return {"error": f"Le repas '{item['nom']}' n'est plus disponible"}

            # Vérifier qu'il n'y a qu'un seul restaurant dans le panier
            restaurants = PanierService.get_panier_restaurants(client_id)
            if len(restaurants) > 1:
                return {"error": "Vous ne pouvez commander que dans un seul restaurant à la fois"}

            return {"success": True, "message": "Panier valide pour la commande"}

        except Exception as e:
            return {"error": f"Erreur lors de la validation : {str(e)}"}

    @staticmethod
    def validate_commande(client_id, point_recup_id, mode_paiement):
        """
        Valide une commande et la crée en base de données
        """
        try:
            from ..models import Commande, CommandeRepas, PointRecup, ModePaiement, StatutCommande, HistoriqueStatutCommande
            from django.db import transaction

            # Vérifier que le panier n'est pas vide
            items = PanierService.get_panier_items(client_id)
            if isinstance(items, dict) and 'error' in items:
                return False, items['error']

            if not items:
                return False, "Votre panier est vide"

            # Valider le panier
            validation_result = PanierService.validate_panier_for_checkout(client_id)
            if isinstance(validation_result, dict) and 'error' in validation_result:
                return False, validation_result['error']

            # Vérifier que le point de récupération existe
            try:
                point_recup = PointRecup.objects.get(id=point_recup_id)
            except PointRecup.DoesNotExist:
                return False, "Point de récupération invalide"

            # Vérifier que le mode de paiement existe
            mode_paiement_obj = None
            if mode_paiement:
                try:
                    mode_paiement_obj = ModePaiement.objects.get(id=mode_paiement)
                except ModePaiement.DoesNotExist:
                    return False, "Mode de paiement invalide"

            # Créer la commande
            with transaction.atomic():
                # Chercher une commande existante avec statut_id=1 (dernier statut)
                commande = None
                commandes = Commande.objects.filter(client_id=client_id)
                for c in commandes:
                    last_statut = c.historiques.order_by('-mis_a_jour_le').first()
                    if last_statut and last_statut.statut_id == 1:
                        commande = c
                        break
                if not commande:
                    # Créer une nouvelle commande
                    commande = Commande.objects.create(client_id=client_id, point_recup_id=None)
                    # Ajouter le statut initial (id=1)
                    HistoriqueStatutCommande.objects.create(commande=commande, statut_id=1)

                # Ajouter les repas à la commande
                for item in items:
                    CommandeRepas.objects.create(
                        commande=commande,
                        repas_id=item['repas_id'],
                        quantite=item['quantite']
                    )

                # Créer l'historique de statut initial
                try:
                    statut_initial = StatutCommande.objects.filter(
                        appellation__icontains='en attente'
                    ).first()

                    if not statut_initial:
                        statut_initial = StatutCommande.objects.first()

                    if statut_initial:
                        HistoriqueStatutCommande.objects.create(
                            commande=commande,
                            statut=statut_initial
                        )
                except Exception:
                    pass  # Pas critique si l'historique échoue

                # Vider le panier après création de la commande
                PanierService.clear_panier(client_id)

                return True, f"Commande #{commande.id} créée avec succès"

        except Exception as e:
            return False, f"Erreur lors de la validation de la commande : {str(e)}"

    @staticmethod
    def finalize_commande(client_id, point_recup_id, mode_paiement_id):
        """
        Met à jour le statut de la commande à 2 (par exemple : 'validée'),
        et met à jour le point de récupération et le mode de paiement.
        """
        try:
            
            from django.db import transaction

            with transaction.atomic():
                commande = None
                commandes = Commande.objects.filter(client_id=client_id)
                for c in commandes:
                    last_statut = c.historiques.order_by('-mis_a_jour_le').first()
                    if last_statut and last_statut.statut_id == 1:
                        commande = c
                        break
            
                # Mettre à jour le point de récupération et le mode de paiement
                commande.point_recup_id = point_recup_id
                if hasattr(commande, 'mode_paiement_id'):
                    commande.mode_paiement_id = mode_paiement_id
                commande.save()

                # Mettre à jour le statut à 3
                statut = StatutCommande.objects.get(id=2)
                HistoriqueStatutCommande.objects.create(
                    commande=commande,
                    statut=statut
                )

            return {"success": True, "message": "Commande finalisée avec succès."}

        except Commande.DoesNotExist:
            return {"error": "Commande non trouvée."}
        except StatutCommande.DoesNotExist:
            return {"error": "Statut de commande non trouvé."}
        except Exception as e:
            return {"error": f"Erreur lors de la finalisation de la commande : {str(e)}"}
        
    @staticmethod
    def get_all_modes_paiement():
        """
        Récupère tous les modes de paiement disponibles.
        """
        try:
            modes = ModePaiement.objects.all().values('id', 'nom')
            return list(modes)
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des modes de paiement : {str(e)}"}