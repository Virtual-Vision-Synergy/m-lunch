from django.utils.timezone import now
from django.db import transaction
from ..models import Commande, StatutCommande, HistoriqueStatutCommande, Repas, CommandeRepas, PointRecup, Client

class CommandeService:
    @staticmethod
    def create_commande(client_id, point_recup_id, initial_statut_id):
        from django.db import transaction
        try:
            with transaction.atomic():
                commande = Commande.objects.create(
                    client_id=client_id,
                    point_recup_id=point_recup_id
                )
                # Vérifier si le statut existe
                if not StatutCommande.objects.filter(id=initial_statut_id).exists():
                    return {"error": "Statut non trouvé"}
                historique = HistoriqueStatutCommande.objects.create(
                    commande=commande,
                    statut_id=initial_statut_id
                )
                return {
                    "commande": {
                        "id": commande.id,
                        "client_id": commande.client_id,
                        "point_recup_id": commande.point_recup_id,
                        "cree_le": commande.cree_le
                    },
                    "historique": {
                        "id": historique.id,
                        "commande_id": historique.commande_id,
                        "statut_id": historique.statut_id,
                        "mis_a_jour_le": historique.mis_a_jour_le
                    }
                }
        except Exception as e:
            return {"error": f"Erreur lors de la création de la commande : {str(e)}"}

    @staticmethod
    def add_repas_to_commande(commande_id, repas_id, quantite):
        try:
            with transaction.atomic():
                if quantite <= 0:
                    return {"error": "Quantité invalide"}

                if not Commande.objects.filter(id=commande_id).exists():
                    return {"error": "Commande non trouvée"}

                if not Repas.objects.filter(id=repas_id).exists():
                    return {"error": "Repas non trouvé"}

                obj, created = CommandeRepas.objects.update_or_create(
                    commande_id=commande_id,
                    repas_id=repas_id,
                    defaults={"quantite": quantite, "ajoute_le": now()}
                )

                return {
                    "id": obj.id,
                    "commande_id": obj.commande_id,
                    "repas_id": obj.repas_id,
                    "quantite": obj.quantite,
                    "ajoute_le": obj.ajoute_le,
                    "created": created
                }
        except Exception as e:
            return {"error": f"Erreur lors de l'ajout du repas à la commande : {str(e)}"}

    @staticmethod
    def changer_statut_commande(commande_id, statut_id):
        try:
            if not Commande.objects.filter(id=commande_id).exists():
                return {"error": "Commande non trouvée"}

            if not StatutCommande.objects.filter(id=statut_id).exists():
                return {"error": "Statut de commande non trouvé"}

            historique = HistoriqueStatutCommande.objects.create(
                commande_id=commande_id,
                statut_id=statut_id
            )
            return {
                "id": historique.id,
                "commande_id": historique.commande_id,
                "statut_id": historique.statut_id,
                "mis_a_jour_le": historique.mis_a_jour_le
            }
        except Exception as e:
            return {"error": f"Erreur lors du changement de statut : {str(e)}"}

    @staticmethod
    def get_commande_details(commande_id):
        try:
            commande = Commande.objects.select_related('client', 'point_recup').get(id=commande_id)
            repas = CommandeRepas.objects.filter(commande=commande).select_related('repas')
            historiques = HistoriqueStatutCommande.objects.filter(commande=commande).select_related('statut')

            return {
                "id": commande.id,
                "client": f"{commande.client.prenom} {commande.client.nom}",
                "point_recup": commande.point_recup.nom,
                "cree_le": commande.cree_le,
                "repas": [{
                    "id": r.repas.id,
                    "nom": r.repas.nom,
                    "quantite": r.quantite,
                    "ajoute_le": r.ajoute_le
                } for r in repas],
                "statuts": [{
                    "statut": h.statut.appellation,
                    "mis_a_jour_le": h.mis_a_jour_le
                } for h in historiques.order_by('-mis_a_jour_le')]
            }
        except Commande.DoesNotExist:
            return {"error": "Commande non trouvée"}
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des détails : {str(e)}"}

    @staticmethod
    def list_commandes_by_client(client_id):
        """Liste toutes les commandes d'un client."""
        try:
            commandes = Commande.objects.filter(client_id=client_id)
            return [{
                "id": c.id,
                "point_recup": c.point_recup.nom,
                "cree_le": c.cree_le
            } for c in commandes]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des commandes : {str(e)}"}

    @staticmethod
    def list_commandes_by_statut(statut_id):
        """Liste toutes les commandes ayant un statut donné (dernier statut)."""
        try:
            commandes_ids = HistoriqueStatutCommande.objects.filter(
                statut_id=statut_id
            ).order_by('commande_id', '-mis_a_jour_le').distinct('commande_id').values_list('commande_id', flat=True)
            commandes = Commande.objects.filter(id__in=commandes_ids)
            return [{
                "id": c.id,
                "client": f"{c.client.prenom} {c.client.nom}",
                "point_recup": c.point_recup.nom,
                "cree_le": c.cree_le
            } for c in commandes]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des commandes par statut : {str(e)}"}