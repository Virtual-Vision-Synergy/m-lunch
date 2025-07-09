from django.utils.timezone import now
from django.db import transaction
from django.db.models import Q

from mlunch.core.models import (
    Livraison, Livreur, Commande, StatutLivraison, HistoriqueStatutLivraison,
    StatutCommande, HistoriqueStatutCommande, StatutLivreur, HistoriqueStatutLivreur
)

class LivraisonService:
    @staticmethod
    def create_livraison(livreur_id, commande_id):
        """
        Crée une nouvelle livraison et met à jour le statut de la commande et du livreur
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"Début create_livraison - livreur_id: {livreur_id}, commande_id: {commande_id}")

        try:
            with transaction.atomic():
                # Vérifier que la commande et le livreur existent
                try:
                    commande = Commande.objects.get(id=commande_id)
                    livreur = Livreur.objects.get(id=livreur_id)
                    logger.info(f"Commande et livreur trouvés - Commande: {commande}, Livreur: {livreur}")
                except (Commande.DoesNotExist, Livreur.DoesNotExist):
                    logger.error("Commande ou livreur non trouvé")
                    return {"error": "Commande ou livreur non trouvé"}

                # Créer la livraison
                livraison = Livraison.objects.create(
                    livreur=livreur,
                    commande=commande
                    # attribue_le est automatiquement défini par default=now
                )
                logger.info(f"Livraison créée avec ID: {livraison.id}")

                # Mettre à jour le statut de la commande vers "En livraison"
                try:
                    statut_en_livraison = StatutCommande.objects.get(appellation="En livraison")
                    HistoriqueStatutCommande.objects.create(
                        commande=commande,
                        statut=statut_en_livraison,
                        mis_a_jour_le=now()
                    )
                    logger.info(f"Statut commande mis à jour vers 'En livraison'")
                except StatutCommande.DoesNotExist:
                    logger.warning("Statut 'En livraison' non trouvé pour les commandes")
                    pass  # Si le statut n'existe pas, on continue

                # Mettre à jour le statut du livreur vers "Occupé"
                try:
                    statut_occupe = StatutLivreur.objects.get(appellation="Occupé")
                    HistoriqueStatutLivreur.objects.create(
                        livreur=livreur,
                        statut=statut_occupe,
                        mis_a_jour_le=now()
                    )
                    logger.info(f"Statut livreur mis à jour vers 'Occupé'")
                except StatutLivreur.DoesNotExist:
                    logger.warning("Statut 'Occupé' non trouvé pour les livreurs")
                    pass  # Si le statut n'existe pas, on continue

                # Créer le statut initial de la livraison
                try:
                    statut_assignee = StatutLivraison.objects.get(appellation="Assignée")
                    HistoriqueStatutLivraison.objects.create(
                        livraison=livraison,
                        statut=statut_assignee,
                        mis_a_jour_le=now()
                    )
                    logger.info(f"Statut livraison créé: 'Assignée'")
                except StatutLivraison.DoesNotExist:
                    logger.warning("Statut 'Assignée' non trouvé pour les livraisons")
                    pass

                result = {
                    "success": True,
                    "livraison": {
                        "id": livraison.id,
                        "livreur": livreur.nom,
                        "commande_id": commande.id,
                        "cree_le": livraison.attribue_le
                    }
                }
                logger.info(f"create_livraison terminé avec succès: {result}")
                return result

        except Exception as e:
            logger.error(f"Exception dans create_livraison: {str(e)}")
            return {"error": f"Erreur lors de la création de la livraison : {str(e)}"}

    @staticmethod
    def get_livraisons_by_livreur(livreur_id):
        """
        Récupère toutes les livraisons d'un livreur
        """
        try:
            livraisons = Livraison.objects.filter(livreur_id=livreur_id).select_related('commande')

            result = []
            for livraison in livraisons:
                # Récupérer le statut actuel de la livraison
                dernier_statut = HistoriqueStatutLivraison.objects.filter(
                    livraison=livraison
                ).order_by('-mis_a_jour_le').first()

                result.append({
                    "id": livraison.id,
                    "commande_id": livraison.commande.id,
                    "client": f"{livraison.commande.client.prenom} {livraison.commande.client.nom}",
                    "point_recup": livraison.commande.point_recup.nom,
                    "cree_le": livraison.cree_le,
                    "statut": dernier_statut.statut.appellation if dernier_statut else "Inconnu"
                })

            return result

        except Exception as e:
            return {"error": f"Erreur lors de la récupération des livraisons : {str(e)}"}

    @staticmethod
    def update_statut_livraison(livraison_id, statut_id):
        """
        Met à jour le statut d'une livraison
        """
        try:
            # Vérifier que la livraison et le statut existent
            if not Livraison.objects.filter(id=livraison_id).exists():
                return {"error": "Livraison non trouvée"}

            if not StatutLivraison.objects.filter(id=statut_id).exists():
                return {"error": "Statut de livraison non trouvé"}

            # Créer l'historique du statut
            historique = HistoriqueStatutLivraison.objects.create(
                livraison_id=livraison_id,
                statut_id=statut_id,
                mis_a_jour_le=now()
            )

            return {
                "success": True,
                "historique": {
                    "id": historique.id,
                    "livraison_id": historique.livraison_id,
                    "statut_id": historique.statut_id,
                    "mis_a_jour_le": historique.mis_a_jour_le
                }
            }

        except Exception as e:
            return {"error": f"Erreur lors de la mise à jour du statut : {str(e)}"}

    @staticmethod
    def get_livraisons_actives():
        """
        Récupère toutes les livraisons en cours
        """
        try:
            # Récupérer les statuts qui indiquent une livraison en cours
            statuts_actifs = StatutLivraison.objects.filter(
                Q(appellation__icontains='Assignée') |
                Q(appellation__icontains='En route') |
                Q(appellation__icontains='Récupérée')
            ).values_list('id', flat=True)

            # Récupérer les livraisons avec ces statuts
            livraisons_actives = []
            livraisons = Livraison.objects.all().select_related('livreur', 'commande')

            for livraison in livraisons:
                dernier_statut = HistoriqueStatutLivraison.objects.filter(
                    livraison=livraison
                ).order_by('-mis_a_jour_le').first()

                if dernier_statut and dernier_statut.statut_id in statuts_actifs:
                    livraisons_actives.append({
                        "id": livraison.id,
                        "livreur": livraison.livreur.nom,
                        "commande_id": livraison.commande.id,
                        "client": f"{livraison.commande.client.prenom} {livraison.commande.client.nom}",
                        "point_recup": livraison.commande.point_recup.nom,
                        "statut": dernier_statut.statut.appellation,
                        "mis_a_jour_le": dernier_statut.mis_a_jour_le
                    })

            return livraisons_actives

        except Exception as e:
            return {"error": f"Erreur lors de la récupération des livraisons actives : {str(e)}"}

    @staticmethod
    def terminer_livraison(livraison_id):
        """
        Marque une livraison comme terminée et libère le livreur
        """
        try:
            with transaction.atomic():
                livraison = Livraison.objects.get(id=livraison_id)

                # Mettre à jour le statut de la livraison vers "Livrée"
                try:
                    statut_livree = StatutLivraison.objects.get(appellation="Livrée")
                    HistoriqueStatutLivraison.objects.create(
                        livraison=livraison,
                        statut=statut_livree,
                        mis_a_jour_le=now()
                    )
                except StatutLivraison.DoesNotExist:
                    pass

                # Mettre à jour le statut de la commande vers "Livrée"
                try:
                    statut_commande_livree = StatutCommande.objects.get(appellation="Livrée")
                    HistoriqueStatutCommande.objects.create(
                        commande=livraison.commande,
                        statut=statut_commande_livree,
                        mis_a_jour_le=now()
                    )
                except StatutCommande.DoesNotExist:
                    pass

                # Remettre le livreur en statut "Disponible"
                try:
                    statut_disponible = StatutLivreur.objects.get(appellation="Disponible")
                    HistoriqueStatutLivreur.objects.create(
                        livreur=livraison.livreur,
                        statut=statut_disponible,
                        mis_a_jour_le=now()
                    )
                except StatutLivreur.DoesNotExist:
                    pass

                return {
                    "success": True,
                    "message": f"Livraison #{livraison_id} terminée avec succès"
                }

        except Livraison.DoesNotExist:
            return {"error": "Livraison non trouvée"}
        except Exception as e:
            return {"error": f"Erreur lors de la finalisation de la livraison : {str(e)}"}

    @staticmethod
    def get_statistiques_livraisons():
        """
        Récupère les statistiques des livraisons
        """
        try:
            total_livraisons = Livraison.objects.count()

            # Compter les livraisons par statut
            stats_par_statut = {}
            livraisons = Livraison.objects.all()

            for livraison in livraisons:
                dernier_statut = HistoriqueStatutLivraison.objects.filter(
                    livraison=livraison
                ).order_by('-mis_a_jour_le').first()

                if dernier_statut:
                    statut_nom = dernier_statut.statut.appellation
                    stats_par_statut[statut_nom] = stats_par_statut.get(statut_nom, 0) + 1

            return {
                "total_livraisons": total_livraisons,
                "stats_par_statut": stats_par_statut
            }

        except Exception as e:
            return {"error": f"Erreur lors de la récupération des statistiques : {str(e)}"}
