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

class RepasService:
    @staticmethod
    def create_repas(nom, type_id, prix, description=None, image=None, est_dispo=True):
        # pdb.set_trace()
        if not nom or len(nom) > 100:
            return {"error": "Le nom doit être une chaîne non vide de 100 caractères maximum"}
        if not isinstance(prix, int) or prix <= 0:
            return {"error": "Le prix doit être un entier positif"}
        try:
            repas = Repas.objects.create(
                nom=nom,
                type_id=type_id,
                prix=prix,
                description=description,
                image=image,
                est_dispo=est_dispo
            )
            return {
                "id": repas.id,
                "nom": repas.nom,
                "type_id": repas.type_id,
                "prix": repas.prix,
                "description": repas.description,
                "image": repas.image,
                "est_dispo": repas.est_dispo
            }
        except Exception as e:
            return {"error": f"Erreur lors de la création du repas : {str(e)}"}

    @staticmethod
    def list_repas_disponibles():
        # pdb.set_trace()
        """Liste tous les repas disponibles."""
        try:
            repas = Repas.objects.filter(est_dispo=True)
            return [{
                "id": r.id,
                "nom": r.nom,
                "prix": r.prix,
                "type": r.type.nom,
                "description": r.description,
                "image": r.image
            } for r in repas]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des repas disponibles : {str(e)}"}

    @staticmethod
    def list_repas_by_type(type_id):
        # pdb.set_trace()
        """Liste les repas par type."""
        try:
            repas = Repas.objects.filter(type_id=type_id)
            return [{
                "id": r.id,
                "nom": r.nom,
                "prix": r.prix,
                "description": r.description,
                "image": r.image
            } for r in repas]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des repas par type : {str(e)}"}