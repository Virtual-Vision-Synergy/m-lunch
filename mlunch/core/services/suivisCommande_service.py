from django.utils.timezone import now
from django.db import transaction
from mlunch.core.models import SuivisCommande


class SuivisCommandeService:
    @staticmethod
    def ajouter_suivi(commande_id, restaurant_id, statut="En attente"):
        """
        Ajoute un nouveau suivi pour une commande et un restaurant.
        """
        try:
            with transaction.atomic():
                suivi = SuivisCommande.objects.create(
                    commande_id=commande_id,
                    restaurant_id=restaurant_id,
                    statut=statut,
                    mis_a_jour_le=now()
                )
                return {
                    "id": suivi.id,
                    "commande_id": suivi.commande_id,
                    "restaurant_id": suivi.restaurant_id,
                    "statut": suivi.statut,
                    "mis_a_jour_le": suivi.mis_a_jour_le
                }
        except Exception as e:
            return {"error": f"Erreur lors de l'ajout du suivi oaaa: {str(e)}"}

    @staticmethod
    def changer_statut(commande_id, restaurant_id):
        """
        Inverse le statut booléen (False -> True, True -> False) pour un suivi donné.
        """
        try:
            suivi = SuivisCommande.objects.get(commande_id=commande_id, restaurant_id=restaurant_id)
            suivi.statut = not suivi.statut
            suivi.mis_a_jour_le = now()
            suivi.save()

            return {
                "id": suivi.id,
                "commande_id": suivi.commande_id,
                "restaurant_id": suivi.restaurant_id,
                "statut": suivi.statut,
                "mis_a_jour_le": suivi.mis_a_jour_le
            }
        except SuivisCommande.DoesNotExist:
            return {"error": "Suivi non trouvé"}
        except Exception as e:
            return {"error": f"Erreur lors de la mise à jour du suivi : {str(e)}"}


    @staticmethod
    def get_suivis_par_commande(commande_id):
        """
        Récupère tous les suivis d'une commande.
        """
        try:
            suivis = SuivisCommande.objects.filter(commande_id=commande_id).select_related('restaurant')
            return [{
                "id": s.id,
                "restaurant": s.restaurant.nom,
                "statut": s.statut,
                "mis_a_jour_le": s.mis_a_jour_le
            } for s in suivis]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des suivis : {str(e)}"}

    @staticmethod
    def get_suivi(commande_id, restaurant_id):
        """
        Récupère un suivi précis (commande + restaurant).
        """
        try:
            suivi = SuivisCommande.objects.get(commande_id=commande_id, restaurant_id=restaurant_id)
            return {
                "id": suivi.id,
                "commande_id": suivi.commande_id,
                "restaurant_id": suivi.restaurant_id,
                "statut": suivi.statut,
                "mis_a_jour_le": suivi.mis_a_jour_le
            }
        except SuivisCommande.DoesNotExist:
            return {"error": "Suivi non trouvé"}
        except Exception as e:
            return {"error": f"Erreur lors de la récupération du suivi : {str(e)}"}

    @staticmethod
    def supprimer_suivi(commande_id, restaurant_id):
        """
        Supprime un suivi pour une commande et un restaurant.
        """
        try:
            suivi = SuivisCommande.objects.get(commande_id=commande_id, restaurant_id=restaurant_id)
            suivi.delete()
            return {"success": f"Suivi supprimé (Commande {commande_id}, Restaurant {restaurant_id})"}
        except SuivisCommande.DoesNotExist:
            return {"error": "Suivi non trouvé"}
        except Exception as e:
            return {"error": f"Erreur lors de la suppression du suivi : {str(e)}"}
