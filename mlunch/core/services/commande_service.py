from django.utils.timezone import now
from django.db import transaction
import pdb
from django.db.models import Sum

from mlunch.core.models import (
    Commande, StatutCommande, HistoriqueStatutCommande, Repas, CommandeRepas,
    PointRecup, Client, RestaurantRepas, Restaurant
)

class CommandeService:
    @staticmethod
    def create_commande(client_id, point_recup_id, initial_statut_id):
        # pdb.set_trace()
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
        # pdb.set_trace()
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
        # pdb.set_trace()
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
        # pdb.set_trace()
        try:
            commande = Commande.objects.select_related('client', 'point_recup').get(id=commande_id)
            client = commande.client
            # Récupérer la zone (secteur) du client
            zone_client = getattr(client, 'zoneclient_set', None)
            secteur = None
            if zone_client and zone_client.exists():
                secteur = zone_client.first().zone.nom
            # Récupérer les repas de la commande
            repas_commandes = CommandeRepas.objects.filter(commande=commande).select_related('repas')
            # Récupérer le restaurant via la table RestaurantRepas
            restaurant_nom = None
            for rc in repas_commandes:
                restaurant_repas = RestaurantRepas.objects.filter(repas=rc.repas).select_related('restaurant').first()
                if restaurant_repas:
                    restaurant_nom = restaurant_repas.restaurant.nom
                    break
            # Nombre de repas
            nombre_repas = sum(rc.quantite for rc in repas_commandes)
            # Prix total via la fonction utilitaire
            prix_total = CommandeService.get_total_commande(commande_id)
            return {
                "client": f"{client.prenom} {client.nom}",
                "secteur": secteur,
                "restaurant": restaurant_nom,
                "date_heure_commande": commande.cree_le,
                "nombre_repas": nombre_repas,
                "prix_total": prix_total
            }
        except Commande.DoesNotExist:
            return {"error": "Commande non trouvée"}
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des détails : {str(e)}"}

    @staticmethod
    def list_commandes_by_client(client_id):
        # pdb.set_trace()
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
        # pdb.set_trace()
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

    @staticmethod
    def get_commandes_en_attente():
        # pdb.set_trace()
        """
        Retourne la liste détaillée des commandes ayant le statut 'En attente'
        Utilise list_commandes_by_statut et get_commande_details.
        """
        try:
            statut = StatutCommande.objects.filter(appellation__iexact="En attente").first()
            if not statut:
                return {"error": "Statut 'En attente' non trouvé"}
            commandes = CommandeService.list_commandes_by_statut(statut.id)
            # Si une erreur est retournée par list_commandes_by_statut
            if isinstance(commandes, dict) and "error" in commandes:
                return commandes
            # Retourne les détails pour chaque commande
            return [CommandeService.get_commande_details(c["id"]) for c in commandes]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des commandes en attente : {str(e)}"}

    @staticmethod
    def get_total_commande(commande_id):
        # pdb.set_trace()
        """
        Retourne la somme totale pour une commande (somme des quantités * prix des repas).
        """
        try:
            repas_commandes = CommandeRepas.objects.filter(commande_id=commande_id).select_related('repas')
            total = sum(rc.quantite * rc.repas.prix for rc in repas_commandes)
            return total
        except Exception as e:
            return {"error": f"Erreur lors du calcul du total de la commande : {str(e)}"}

    @staticmethod
    def get_repas(commande_id):
        # pdb.set_trace()
        """
        Retourne la liste des repas (nom et quantité) pour une commande donnée.
        """
        try:
            repas_commandes = CommandeRepas.objects.filter(commande_id=commande_id).select_related('repas')
            return [
                {
                    "nom": rc.repas.nom,
                    "quantite": rc.quantite
                }
                for rc in repas_commandes
            ]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des repas : {str(e)}"}

    @staticmethod
    def get_all_commandes():
        # pdb.set_trace()
        """
        Retourne la liste de toutes les commandes avec tous les détails (get_commande_details)
        + le statut actuel et le mode de paiement utilisé (si disponible).
        """
        try:
            commandes = Commande.objects.all()
            result = []
            for commande in commandes:
                details = CommandeService.get_commande_details(commande.id)
                # Récupérer le dernier statut
                historique = HistoriqueStatutCommande.objects.filter(commande=commande).order_by('-mis_a_jour_le').first()
                statut = None
                if historique and hasattr(historique, 'statut') and historique.statut:
                    statut = historique.statut.appellation
                # Récupérer le mode de paiement si le modèle Commande a ce champ (ex: commande.mode_paiement)
                mode_paiement = getattr(commande, 'mode_paiement', None)
                # Ajout au résultat
                details['statut'] = statut
                details['mode_paiement'] = mode_paiement
                result.append(details)
            return result
        except Exception as e:
            return {"error": f"Erreur lors de la récupération de toutes les commandes : {str(e)}"}

    @staticmethod
    def get_commandes_by_client(client_id):
        commandes = (
            Commande.objects
            .filter(client_id=client_id)
            .order_by('-cree_le')
        )

        commandes_data = []
        for c in commandes:
            repas = CommandeRepas.objects.filter(commande=c)
            total_articles = repas.aggregate(Sum('quantite'))['quantite__sum'] or 0
            total_prix = sum([r.repas.prix * r.quantite for r in repas])
            statut = (
                HistoriqueStatutCommande.objects
                .filter(commande=c)
                .order_by('-mis_a_jour_le')
                .first()
            )
            commandes_data.append({
                'commande': c,
                'articles': total_articles,
                'total': total_prix,
                'statut': statut.statut.appellation if statut else "Inconnu"
            })

        return commandes_data

    @staticmethod
    def get_commande_detail(commande_id):
        try:
            commande = Commande.objects.get(id=commande_id)
            repas = CommandeRepas.objects.filter(commande=commande)
            statut = (
                HistoriqueStatutCommande.objects
                .filter(commande=commande)
                .order_by('-mis_a_jour_le')
                .first()
            )
            total = sum([r.repas.prix * r.quantite for r in repas])
            return {
                'commande': commande,
                'repas': list(repas),
                'statut': statut.statut.appellation if statut else "Inconnu",
                'total': total
            }
        except Commande.DoesNotExist:
            return {"error": "Commande non trouvée"}
        except Exception as e:
            return {"error": f"Erreur : {str(e)}"}
