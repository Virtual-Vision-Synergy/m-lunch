from django.db.models import Sum, F
from django.utils.timezone import now
from ..models import (
    Client, Repas, RestaurantRepas, PointRecup, DisponibiliteRepas,
    Restaurant, ZoneClient, ZoneRestaurant
)

class PanierService:
    """
    Service pour gérer le panier en utilisant les sessions Django
    """

    @staticmethod
    def get_panier_items(client_id):
        """
        Récupère les articles du panier depuis la session
        En production, cela pourrait être stocké en base de données
        """
        try:
            # Pour l'instant, nous simulons des données de panier
            # En réalité, cela devrait venir de la session ou d'une table panier temporaire

            # Exemple de données simulées - à remplacer par la logique réelle
            items = [
                {
                    'item_id': 1,
                    'repas_id': 1,
                    'nom': 'Pizza Margherita',
                    'prix': 12000,
                    'quantite': 2,
                    'restaurant_nom': 'Chez Mario',
                    'image': '/static/images/pizza.jpg',
                    'total': 24000
                },
                {
                    'item_id': 2,
                    'repas_id': 2,
                    'nom': 'Burger Deluxe',
                    'prix': 15000,
                    'quantite': 1,
                    'restaurant_nom': 'Fast Food Plus',
                    'image': '/static/images/burger.jpg',
                    'total': 15000
                }
            ]

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
            frais_livraison = 2000  # Frais fixes pour l'exemple
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

            # Vérifier si le client peut commander dans ce restaurant (même zone)
            client_zones = ZoneClient.objects.filter(client_id=client_id).values_list('zone_id', flat=True)
            restaurant_zones = ZoneRestaurant.objects.filter(restaurant=restaurant).values_list('zone_id', flat=True)

            if not set(client_zones).intersection(set(restaurant_zones)):
                return {"error": "Ce restaurant ne livre pas dans votre zone"}

            # Logique d'ajout au panier (à implémenter selon votre choix : session, DB temporaire, etc.)
            # Pour l'instant, on retourne un succès

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
    def remove_from_panier(client_id, item_id):
        """
        Supprime un article du panier
        """
        try:
            # Logique de suppression à implémenter selon votre système de stockage
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

            # Logique de mise à jour à implémenter
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
                # Créer la commande
                commande = Commande.objects.create(
                    client_id=client_id,
                    point_recup=point_recup,
                    mode_paiement=mode_paiement_obj
                )

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
