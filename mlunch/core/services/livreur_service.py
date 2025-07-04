import pdb
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from shapely import wkt
from shapely.geometry import Point
from django.db import transaction
from django.utils.timezone import now
from datetime import datetime

from ..models import (
    Client, StatutCommande, Zone, ZoneClient, PointRecup,
    Commande, HistoriqueStatutCommande,
    StatutRestaurant, Restaurant, HistoriqueStatutRestaurant,
    TypeRepas, Repas,
    StatutLivreur, Livreur, HistoriqueStatutLivreur,
    StatutZone, HistoriqueStatutZone,
    StatutLivraison, Livraison, HistoriqueStatutLivraison,
    CommandeRepas, RestaurantRepas, ZoneRestaurant,
    Commission, Horaire, HoraireSpecial,
    Promotion, LimiteCommandesJournalieres
)


class LivreurService:
    @staticmethod
    def create_livreur(nom, initial_statut_id, contact=None, position=None):
        # pdb.set_trace()
        from django.db import transaction
        if not nom or len(nom) > 100:
            return {"error": "Le nom doit être une chaîne non vide de 100 caractères maximum"}
        try:
            with transaction.atomic():
                if not StatutLivreur.objects.filter(id=initial_statut_id).exists():
                    return {"error": "Statut non trouvé"}
                livreur = Livreur.objects.create(
                    nom=nom,
                    contact=contact,
                    position=f"POINT({position[0]} {position[1]})" if position else None
                )
                historique = HistoriqueStatutLivreur.objects.create(
                    livreur=livreur,
                    statut_id=initial_statut_id
                )
                return {
                    "livreur": {
                        "id": livreur.id,
                        "nom": livreur.nom,
                        "contact": livreur.contact,
                        "position": livreur.position,
                        "date_inscri": livreur.date_inscri
                    },
                    "historique": {
                        "id": historique.id,
                        "livreur_id": historique.livreur_id,
                        "statut_id": historique.statut_id,
                        "mis_a_jour_le": historique.mis_a_jour_le
                    }
                }
        except Exception as e:
            return {"error": f"Erreur lors de la création du livreur : {str(e)}"}

    @staticmethod
    def list_livreurs_actifs():
        # pdb.set_trace()
        """Liste tous les livreurs actifs (dernier statut = actif)."""
        try:
            actifs = []
            for l in Livreur.objects.all():
                dernier_statut = l.historiques.order_by('-mis_a_jour_le').first()
                if dernier_statut and dernier_statut.statut.appellation and dernier_statut.statut.appellation.lower() == "actif":
                    actifs.append({
                        "id": l.id,
                        "nom": l.nom,
                        "contact": l.contact,
                        "position": l.position,
                        "date_inscri": l.date_inscri
                    })
            return actifs
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des livreurs actifs : {str(e)}"}

    @staticmethod
    def list_livreurs_par_zone(zone_id):
        # pdb.set_trace()
        """
        Liste tous les livreurs associés à une zone donnée via ZoneLivreur.
        """
        try:
            from ..models import ZoneLivreur
            livreur_ids = ZoneLivreur.objects.filter(zone_id=zone_id).values_list('livreur_id', flat=True)
            livreurs = []
            for l in Livreur.objects.filter(id__in=livreur_ids):
                livreurs.append({
                    "id": l.id,
                    "nom": l.nom,
                    "contact": l.contact,
                    "position": l.position,
                    "date_inscri": l.date_inscri
                })
            return livreurs
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des livreurs pour la zone : {str(e)}"}

    @staticmethod
    def list_livreurs_par_statut(statut_id):
        # pdb.set_trace()
        """
        Liste tous les livreurs ayant un statut donné (dernier statut).
        """
        try:
            livreurs = []
            for l in Livreur.objects.all():
                dernier_statut = l.historiques.order_by('-mis_a_jour_le').first()
                if dernier_statut and dernier_statut.statut_id == statut_id:
                    livreurs.append({
                        "id": l.id,
                        "nom": l.nom,
                        "contact": l.contact,
                        "position": l.position,
                        "date_inscri": l.date_inscri
                    })
            return livreurs
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des livreurs par statut : {str(e)}"}

    @staticmethod
    def list_livreurs_par_date_inscription(date_debut, date_fin):
        # pdb.set_trace()
        """
        Liste tous les livreurs inscrits entre deux dates.
        """
        try:
            livreurs = []
            for l in Livreur.objects.filter(date_inscri__range=[date_debut, date_fin]):
                livreurs.append({
                    "id": l.id,
                    "nom": l.nom,
                    "contact": l.contact,
                    "position": l.position,
                    "date_inscri": l.date_inscri
                })
            return livreurs
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des livreurs par date d'inscription : {str(e)}"}

    @staticmethod
    def list_livreurs_disponibles():
        # pdb.set_trace()
        """
        Liste tous les livreurs disponibles (dernier statut = disponible).
        """
        try:
            disponibles = []
            for l in Livreur.objects.all():
                dernier_statut = l.historiques.order_by('-mis_a_jour_le').first()
                if dernier_statut and dernier_statut.statut.appellation and dernier_statut.statut.appellation.lower() == "disponible":
                    disponibles.append({
                        "id": l.id,
                        "nom": l.nom,
                        "contact": l.contact,
                        "position": l.position,
                        "date_inscri": l.date_inscri
                    })
            return disponibles
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des livreurs disponibles : {str(e)}"}