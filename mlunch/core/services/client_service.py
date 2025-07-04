from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from ..models import Client, Commande, ZoneClient
from datetime import datetime
from django.utils.timezone import now
import pdb

class ClientService:
    @staticmethod
    def create_client(email, mot_de_passe, contact=None, prenom=None, nom=None):
        #pdb.set_trace()
        try:
            validate_email(email)
        except ValidationError:
            return {"error": "Email invalide"}
        if not mot_de_passe:
            return {"error": "Mot de passe invalide"}
        try:
            client = Client.objects.create(
                email=email,
                mot_de_passe=mot_de_passe,
                contact=contact,
                prenom=prenom,
                nom=nom
            )
            return {"client": {
                "id": client.id,
                "email": client.email,
                "contact": client.contact,
                "prenom": client.prenom,
                "nom": client.nom,
                "date_inscri": client.date_inscri
            }}
        except Exception as e:
            return {"error": f"Erreur lors de la création du client : {str(e)}"}

    @staticmethod
    def get_client_by_id(client_id):
        #pdb.set_trace()
        try:
            client = Client.objects.get(id=client_id)
            return {
                "id": client.id,
                "email": client.email,
                "contact": client.contact,
                "prenom": client.prenom,
                "nom": client.nom,
                "date_inscri": client.date_inscri
            }
        except ObjectDoesNotExist:
            return {"error": "Client non trouvé"}
        except Exception as e:
            return {"error": f"Erreur : {str(e)}"}

    @staticmethod
    def get_client_by_email(email):
        #pdb.set_trace()
        try:
            validate_email(email)
        except ValidationError:
            return {"error": "Format d'email invalide"}
        try:
            client = Client.objects.get(email=email)
            return {
                "id": client.id,
                "email": client.email,
                "contact": client.contact,
                "prenom": client.prenom,
                "nom": client.nom,
                "date_inscri": client.date_inscri
            }
        except ObjectDoesNotExist:
            return {"error": "Client non trouvé"}
        except Exception as e:
            return {"error": f"Erreur : {str(e)}"}

    @staticmethod
    def get_all_clients():
        #pdb.set_trace()
        try:
            clients = Client.objects.all().order_by('nom', 'prenom')
            return [{
                "id": c.id,
                "email": c.email,
                "contact": c.contact,
                "prenom": c.prenom,
                "nom": c.nom,
                "date_inscri": c.date_inscri
            } for c in clients] or {"error": "Aucun client trouvé"}
        except Exception as e:
            return {"error": f"Erreur : {str(e)}"}

    @staticmethod
    def update_client(client_id, email=None, mot_de_passe=None, contact=None, prenom=None, nom=None):
        #pdb.set_trace()
        try:
            client = Client.objects.get(id=client_id)
            if email:
                validate_email(email)
                client.email = email
            if mot_de_passe:
                client.mot_de_passe = mot_de_passe
            if contact is not None:
                client.contact = contact
            if prenom is not None:
                client.prenom = prenom
            if nom is not None:
                client.nom = nom
            client.save()
            return {
                "id": client.id,
                "email": client.email,
                "contact": client.contact,
                "prenom": client.prenom,
                "nom": client.nom,
                "date_inscri": client.date_inscri
            }
        except ObjectDoesNotExist:
            return {"error": "Client non trouvé"}
        except ValidationError:
            return {"error": "Format d'email invalide"}
        except Exception as e:
            return {"error": f"Erreur : {str(e)}"}

    @staticmethod
    def list_commandes(client_id):
        #pdb.set_trace()
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
    def get_zones(client_id):
        """Liste les zones associées à un client."""
        try:
            zones = ZoneClient.objects.filter(client_id=client_id).select_related('zone')
            return [{
                "id": z.zone.id,
                "nom": z.zone.nom,
                "description": z.zone.description
            } for z in zones]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des zones : {str(e)}"}