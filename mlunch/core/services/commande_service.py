from django.utils.timezone import now
from django.db import transaction
import pdb
from django.db.models import Sum

from mlunch.core.models import (
    Commande, StatutCommande, HistoriqueStatutCommande, Repas, CommandeRepas,
    PointRecup, Client, RestaurantRepas, Restaurant, SuivisCommande
)
from mlunch.core.services.suivisCommande_service import SuivisCommandeService

class CommandeService:
    @staticmethod
    def create_commande(client_id, point_recup_id, initial_statut_id):
        try:
            with transaction.atomic():
                # Créer la commande
                commande = Commande.objects.create(
                    client_id=client_id,
                    point_recup_id=point_recup_id
                )

                # Vérifier que le statut existe
                if not StatutCommande.objects.filter(id=initial_statut_id).exists():
                    return {"error": "Statut non trouvé"}

                # Ajouter l'historique du statut
                historique = HistoriqueStatutCommande.objects.create(
                    commande=commande,
                    statut_id=initial_statut_id
                )

                # Récupérer les restaurants liés à cette commande
                restaurant_ids = CommandeService.get_all_id_restaurant_from_commande(commande.id)

                # Créer un suivi pour chaque restaurant via le service
                suivis_list = []
                for restaurant_id in restaurant_ids:
                    suivi_data = SuivisCommandeService.create_suivi(
                        commande_id=commande.id,
                        restaurant_id=restaurant_id,
                    )
                    suivis_list.append(suivi_data)

                # Retourner la réponse complète
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
                    },
                    "suivis": suivis_list
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
                "id": commande_id,  # Ajouter l'ID de la commande
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

    @staticmethod
    def get_commandes_en_cours(client_id):
        """
        Récupère les commandes en cours pour un client
        """
        try:
            from django.db.models import Q
            from ..models import Commande, HistoriqueStatutCommande, StatutCommande

            # Récupérer les statuts qui indiquent une commande en cours
            statuts_en_cours = StatutCommande.objects.filter(
                Q(appellation__icontains='attente') |
                Q(appellation__icontains='preparation') |
                Q(appellation__icontains='pret') |
                Q(appellation__icontains='en cours')
            ).values_list('id', flat=True)

            # Récupérer les commandes du client
            commandes = Commande.objects.filter(client_id=client_id).order_by('-cree_le')

            commandes_en_cours = []
            for commande in commandes:
                # Récupérer le dernier statut
                dernier_historique = HistoriqueStatutCommande.objects.filter(
                    commande=commande
                ).order_by('-mis_a_jour_le').first()

                if dernier_historique and dernier_historique.statut_id in statuts_en_cours:
                    commande_dict = {
                        'id': commande.id,
                        'cree_le': commande.cree_le,
                        'point_recup_nom': commande.point_recup.nom if commande.point_recup else 'Non défini',
                        'statut': dernier_historique.statut.appellation,
                        'statut_id': dernier_historique.statut_id,
                        'mis_a_jour_le': dernier_historique.mis_a_jour_le
                    }

                    # Vérifier si la commande peut être annulée
                    commande_dict['peut_annuler'] = CommandeService.peut_annuler_commande(commande.id)

                    # Calculer le temps estimé (placeholder)
                    commande_dict['temps_estime'] = "15-30 minutes"

                    commandes_en_cours.append(commande_dict)

            return commandes_en_cours

        except Exception as e:
            return {"error": f"Erreur lors de la récupération des commandes en cours : {str(e)}"}

    @staticmethod
    def get_historique_commandes(client_id):
        """
        Récupère l'historique complet des commandes pour un client
        """
        try:
            from ..models import Commande, HistoriqueStatutCommande

            commandes = Commande.objects.filter(client_id=client_id).order_by('-cree_le')

            historique = []
            for commande in commandes:
                # Récupérer le dernier statut
                dernier_historique = HistoriqueStatutCommande.objects.filter(
                    commande=commande
                ).order_by('-mis_a_jour_le').first()

                commande_dict = {
                    'id': commande.id,
                    'cree_le': commande.cree_le,
                    'point_recup_nom': commande.point_recup.nom if commande.point_recup else 'Non défini',
                    'statut': dernier_historique.statut.appellation if dernier_historique else 'Inconnu',
                    'statut_id': dernier_historique.statut_id if dernier_historique else None,
                    'mis_a_jour_le': dernier_historique.mis_a_jour_le if dernier_historique else commande.cree_le
                }

                # Calculer le total de la commande
                total = CommandeService.calculate_commande_total(commande.id)
                commande_dict['total'] = total.get('total', 0) if isinstance(total, dict) else 0

                historique.append(commande_dict)

            return historique

        except Exception as e:
            return {"error": f"Erreur lors de la récupération de l'historique : {str(e)}"}

    @staticmethod
    def peut_annuler_commande(commande_id):
        """
        Vérifie si une commande peut être annulée
        """
        try:
            from ..models import HistoriqueStatutCommande, StatutCommande

            # Récupérer le dernier statut
            dernier_historique = HistoriqueStatutCommande.objects.filter(
                commande_id=commande_id
            ).order_by('-mis_a_jour_le').first()

            if not dernier_historique:
                return False

            # Les commandes peuvent être annulées si elles sont en attente ou en préparation
            statuts_annulables = StatutCommande.objects.filter(
                appellation__in=['En attente', 'En préparation', 'Confirmée']
            ).values_list('id', flat=True)

            return dernier_historique.statut_id in statuts_annulables

        except Exception as e:
            return False

    @staticmethod
    def annuler_commande(commande_id, client_id):
        """
        Annule une commande si possible
        """
        try:
            from django.db import transaction
            from ..models import Commande, HistoriqueStatutCommande, StatutCommande

            # Vérifier que la commande appartient au client
            try:
                commande = Commande.objects.get(id=commande_id, client_id=client_id)
            except Commande.DoesNotExist:
                return False, "Commande non trouvée"

            # Vérifier si la commande peut être annulée
            if not CommandeService.peut_annuler_commande(commande_id):
                return False, "Cette commande ne peut plus être annulée"

            # Récupérer le statut "Annulée"
            try:
                statut_annule = StatutCommande.objects.get(appellation__iexact='Annulée')
            except StatutCommande.DoesNotExist:
                # Créer le statut s'il n'existe pas
                statut_annule = StatutCommande.objects.create(appellation='Annulée')

            # Mettre à jour le statut avec transaction
            with transaction.atomic():
                HistoriqueStatutCommande.objects.create(
                    commande=commande,
                    statut=statut_annule,
                    mis_a_jour_le=now()
                )

            return True, f"Commande #{commande_id} annulée avec succès"

        except Exception as e:
            return False, f"Erreur lors de l'annulation : {str(e)}"

    @staticmethod
    def calculate_commande_total(commande_id):
        """
        Calcule le total d'une commande
        """
        try:
            from django.db.models import Sum, F
            from ..models import CommandeRepas

            total = CommandeRepas.objects.filter(
                commande_id=commande_id
            ).aggregate(
                total=Sum(F('quantite') * F('repas__prix'))
            )['total'] or 0

            # Ajouter les frais de livraison (placeholder)
            frais_livraison = 2000
            total_final = total + frais_livraison

            return {
                'sous_total': total,
                'frais_livraison': frais_livraison,
                'total': total_final
            }

        except Exception as e:
            return {"error": f"Erreur lors du calcul du total : {str(e)}"}

    @staticmethod
    def get_all_id_restaurant_from_commande(commande_id):
        """
        Retourne la liste des IDs des restaurants liés aux repas d'une commande.
        """
        try:
            # Récupérer tous les repas liés à la commande
            repas_ids = CommandeRepas.objects.filter(commande_id=commande_id).values_list('repas_id', flat=True)

            # Rechercher les restaurants liés à ces repas
            restaurant_ids = RestaurantRepas.objects.filter(
                repas_id__in=repas_ids
            ).values_list('restaurant_id', flat=True).distinct()

            # Retourner la liste (évaluée)
            return list(restaurant_ids)

        except Exception as e:
            return {"error": f"Erreur lors de la récupération des restaurants de la commande : {str(e)}"}

    @staticmethod
    def check_if_commande_done(commande_id):
        """
        Vérifie si tous les suivis liés à une commande ont un statut True.
        """
        try:
            existe_suivi_non_traite = SuivisCommande.objects.filter(
                commande_id=commande_id,
                statut=False
            ).exists()

            if existe_suivi_non_traite:
                return False  

            return True

        except Exception as e:
            return {"error": f"Erreur lors de la vérification de la commande : {str(e)}"}
    
    @staticmethod
    def change_state_auto(commande_id):
        """
        Change automatiquement l'état de la commande en 'Prête' si tous les suivis sont traités
        et que le statut actuel de la commande est 'En cours' (avec ou sans accent, minuscule ou majuscule).
        """
        try:
            if not CommandeService.check_if_commande_done(commande_id):
                return {"success": False, "message": "Tous les suivis ne sont pas traités."}

            # Récupérer la commande
            commande = Commande.objects.get(id=commande_id)

            # Récupérer le dernier historique de statut (le plus récent)
            dernier_statut_commande = commande.historiques.order_by('-mis_a_jour_le').first()

            if not dernier_statut_commande:
                return {"error": "Aucun statut trouvé pour cette commande."}

            # Vérifier que le statut actuel est "En cours" (variantes accent/casse)
            appellations_en_cours = ['En cours', 'en cours', 'EN COURS', 'Encours', 'encours', 'ENCOURS']
            statut_actuel = dernier_statut_commande.statut.appellation or ""

            if statut_actuel.lower().replace(" ", "") not in [a.lower().replace(" ", "") for a in appellations_en_cours]:
                return {"success": False, "message": f"Le statut actuel de la commande n'est pas 'En cours' mais '{statut_actuel}'."}

            # Trouver le statut "Prête" dans la base (avec variantes)
            appellations_prete = ['Prête', 'Prete', 'prête', 'prete', 'PRÊTE', 'PRETE']
            statut_prete = None
            for appellation in appellations_prete:
                try:
                    statut_prete = StatutCommande.objects.get(appellation__iexact=appellation)
                    break
                except StatutCommande.DoesNotExist:
                    continue

            if statut_prete is None:
                return {"error": "Le statut 'Prête' (ou variantes) n'existe pas dans la base de données."}

            # Changer le statut de la commande en "Prête"
            CommandeService.changer_statut_commande(commande_id, statut_prete.id)

            return {"success": True, "message": "Commande marquée comme prête."}

        except Commande.DoesNotExist:
            return {"error": "Commande introuvable."}
        except Exception as e:
            return {"error": f"Erreur lors du changement d'état automatique : {str(e)}"}


