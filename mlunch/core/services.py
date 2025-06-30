from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from shapely import wkt
from shapely.geometry import Point

from .models import (
    Client, Commande, StatutCommande, HistoriqueStatutCommande, PointRecup,
    Restaurant, HistoriqueStatutRestaurant, Repas, Livreur, StatutLivreur,
    HistoriqueStatutLivreur, Zone, StatutZone, HistoriqueStatutZone, StatutRestaurant,
    Livraison, StatutLivraison, HistoriqueStatutLivraison
)


class ClientService:
    @staticmethod
    def create_client(email, mot_de_passe, contact=None, prenom=None, nom=None):
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


class RestaurantService:
    @staticmethod
    def create_restaurant(nom, initial_statut_id, adresse=None, image=None, geo_position=None):
        from django.db import transaction
        if not nom or len(nom) > 150:
            return {"error": "Le nom doit être une chaîne non vide de 150 caractères maximum"}
        try:
            with transaction.atomic():
                if not StatutRestaurant.objects.filter(id=initial_statut_id).exists():
                    return {"error": "Statut non trouvé"}
                restaurant = Restaurant.objects.create(
                    nom=nom,
                    adresse=adresse,
                    image=image,
                    geo_position=f"POINT({geo_position[0]} {geo_position[1]})" if geo_position else None
                )
                historique = HistoriqueStatutRestaurant.objects.create(
                    restaurant=restaurant,
                    statut_id=initial_statut_id
                )
                return {
                    "restaurant": {
                        "id": restaurant.id,
                        "nom": restaurant.nom,
                        "adresse": restaurant.adresse,
                        "image": restaurant.image,
                        "geo_position": restaurant.geo_position
                    },
                    "historique": {
                        "id": historique.id,
                        "restaurant_id": historique.restaurant_id,
                        "statut_id": historique.statut_id,
                        "mis_a_jour_le": historique.mis_a_jour_le
                    }
                }
        except Exception as e:
            return {"error": f"Erreur lors de la création du restaurant : {str(e)}"}


class RepasService:
    @staticmethod
    def create_repas(nom, type_id, prix, description=None, image=None, est_dispo=True):
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


class LivreurService:
    @staticmethod
    def create_livreur(nom, initial_statut_id, contact=None, position=None):
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


class ZoneService:
    @staticmethod
    def create_zone(nom, description, coordinates, initial_statut_id):
        from django.db import transaction
        if not nom or len(nom) > 100 or not nom.strip():
            return {"error": "Nom de zone invalide"}
        if not isinstance(description, str) or len(description) > 100:
            return {"error": "Description invalide"}
        if not isinstance(initial_statut_id, int) or initial_statut_id <= 0:
            return {"error": "ID statut invalide"}
        if not isinstance(coordinates, list) or len(coordinates) < 3:
            return {"error": "Coordonnées du polygone invalides (minimum 3 points)"}
        try:
            with transaction.atomic():
                if not StatutZone.objects.filter(id=initial_statut_id).exists():
                    return {"error": "Statut zone non trouvé"}
                polygon_wkt = "POLYGON((" + ",".join([f"{lon} {lat}" for lon, lat in coordinates]) + "))"
                zone = Zone.objects.create(
                    nom=nom,
                    description=description,
                    zone=polygon_wkt
                )
                historique = HistoriqueStatutZone.objects.create(
                    zone=zone,
                    statut_id=initial_statut_id
                )
                return {
                    "zone": {
                        "id": zone.id,
                        "nom": zone.nom,
                        "description": zone.description,
                        "zone": zone.zone
                    },
                    "historique": {
                        "id": historique.id,
                        "zone_id": historique.zone_id,
                        "statut_id": historique.statut_id,
                        "mis_a_jour_le": historique.mis_a_jour_le
                    }
                }
        except Exception as e:
            return {"error": f"Erreur lors de la création de la zone : {str(e)}"}

    @staticmethod
    def get_zone_by_coord(lat, lon, max_distance_m=5000):
        """
        Retourne la zone contenant ou la plus proche (à < max_distance_m) d'un point (lat, lon).
        """
        point = Point(float(lon), float(lat))
        closest_zone = None
        closest_dist = None
        for zone in Zone.objects.all():
            try:
                poly = wkt.loads(zone.zone)
                if poly.contains(point):
                    return {'id': zone.id, 'nom': zone.nom}
                dist = poly.distance(point) * 111320  # deg -> m (approx)
                if closest_dist is None or dist < closest_dist:
                    closest_zone = zone
                    closest_dist = dist
            except Exception:
                continue
        if closest_zone and closest_dist < max_distance_m:
            return {'id': closest_zone.id, 'nom': closest_zone.nom}
        return None


class LivraisonService:
    @staticmethod
    def create_livraison(livreur_id, commande_id, initial_statut_id=1):
        from django.db import transaction
        if not isinstance(livreur_id, int) or livreur_id <= 0:
            return {"error": "L'ID du livreur doit être un entier positif"}
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"error": "L'ID de la commande doit être un entier positif"}

        try:
            with transaction.atomic():
                # Vérifier si le livreur existe
                if not Livreur.objects.filter(id=livreur_id).exists():
                    return {"error": "Livreur non trouvé"}

                # Vérifier si la commande existe
                if not Commande.objects.filter(id=commande_id).exists():
                    return {"error": "Commande non trouvée"}

                # Vérifier si le statut existe
                if not StatutLivraison.objects.filter(id=initial_statut_id).exists():
                    return {"error": "Statut livraison non trouvé"}

                livraison = Livraison.objects.create(
                    livreur_id=livreur_id,
                    commande_id=commande_id
                )

                historique = HistoriqueStatutLivraison.objects.create(
                    livraison=livraison,
                    statut_id=initial_statut_id
                )

                return {
                    "livraison": {
                        "id": livraison.id,
                        "livreur_id": livraison.livreur_id,
                        "commande_id": livraison.commande_id,
                        "attribue_le": livraison.attribue_le
                    },
                    "historique": {
                        "id": historique.id,
                        "livraison_id": historique.livraison_id,
                        "statut_id": historique.statut_id,
                        "mis_a_jour_le": historique.mis_a_jour_le
                    }
                }
        except Exception as e:
            return {"error": f"Erreur lors de la création de la livraison : {str(e)}"}
