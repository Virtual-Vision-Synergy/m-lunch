from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from shapely import wkt
from shapely.geometry import Point
from django.db import transaction
from django.utils.timezone import now
from datetime import datetime

from .models import (
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

    @staticmethod
    def list_commandes(client_id):
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
    @staticmethod
    def update_restaurant(restaurant_id, data):
        """
        Met à jour un restaurant avec les champs :
        - description
        - commission
        - horaire (update ou insert, sans delete)
        - statut
        - secteurs (zones desservies)
        """

        with transaction.atomic():
            try:
                restaurant = Restaurant.objects.get(id=restaurant_id)

                # 1. Description
                if 'description' in data:
                    restaurant.description = data['description']
                    restaurant.save()

                # 2. Commission
                if 'commission' in data:
                    Commission.objects.create(
                        restaurant=restaurant,
                        valeur=data['commission'],
                        mis_a_jour_le= now()
                    )

                # 3. Horaire (update si existe, insert sinon)
                if 'horaire' in data:
                    for h in data['horaire']:
                        obj, created = Horaire.objects.update_or_create(
                            restaurant=restaurant,
                            le_jour=h['le_jour'],
                            defaults={
                                'horaire_debut': h['horaire_debut'],
                                'horaire_fin': h['horaire_fin'],
                                'mis_a_jour_le': now()
                            }
                        )

                # 4. Statut (historique)
                if 'statut_id' in data:
                    statut = StatutRestaurant.objects.get(id=data['statut_id'])
                    HistoriqueStatutRestaurant.objects.create(
                        restaurant=restaurant,
                        statut=statut,
                        mis_a_jour_le=now()
                    )

                # 5. Secteurs (zones) — suppression puis recréation
                if 'secteurs' in data:
                    ZoneRestaurant.objects.filter(restaurant=restaurant).delete()
                    for zone_id in data['secteurs']:
                        zone = Zone.objects.get(id=zone_id)
                        ZoneRestaurant.objects.create(
                            restaurant=restaurant,
                            zone=zone
                        )

            except Restaurant.DoesNotExist:
                raise ValueError("Restaurant introuvable")
            except StatutRestaurant.DoesNotExist:
                raise ValueError("Statut introuvable")
            except Zone.DoesNotExist:
                raise ValueError("Zone introuvable")

    @staticmethod
    def delete_restaurant(restaurant_id):
        try:
            with transaction.atomic():
                restaurant = Restaurant.objects.get(id=restaurant_id)

                # Récupérer les commandes liées à ce restaurant via ZoneRestaurant et Commande -> PointRecup ?
                # Plus simple : récupérer les commandes qui contiennent des repas du restaurant
                # ou via zones et restaurants liés
                # Selon ta modélisation, il faut récupérer toutes les commandes associées à ce restaurant

                # Une manière efficace (via commandes qui ont au moins un repas de ce restaurant)
                commandes_ids = Commande.objects.filter(
                    repas_commandes__repas__restaurants_repas__restaurant=restaurant
                ).distinct().values_list('id', flat=True)

                # Statut 'Livree' (ou équivalent) => commandes terminées
                statut_livree = StatutCommande.objects.get(nom__iexact='Livree')

                # Vérifier s'il existe des commandes liées qui ne sont pas livrées
                commandes_en_cours = HistoriqueStatutCommande.objects.filter(
                    commande_id__in=commandes_ids
                ).exclude(statut=statut_livree).values('commande').distinct()

                if commandes_en_cours.exists():
                    return "Suppression impossible : des commandes sont encore en cours pour ce restaurant."

                # Pas de commandes en cours, on peut passer le restaurant en 'Inactif'
                statut_inactif = StatutRestaurant.objects.get(nom__iexact="Inactif")

                HistoriqueStatutRestaurant.objects.create(
                    restaurant=restaurant,
                    statut=statut_inactif,
                    mis_a_jour_le=now(),
                )
                return "Restaurant marqué comme inactif."

        except Restaurant.DoesNotExist:
            return "Restaurant non trouvé."
        except StatutCommande.DoesNotExist:
            return "Le statut 'Livree' est manquant en base."
        except StatutRestaurant.DoesNotExist:
            return "Le statut 'Inactif' est manquant en base."
        except Exception as e:
            return f"Erreur : {str(e)}"

    @staticmethod
    def list_restaurants_actifs():
        """Liste tous les restaurants actifs (dernier statut = actif)."""
        try:
            actifs = []
            for r in Restaurant.objects.all():
                dernier_statut = r.historiques.order_by('-mis_a_jour_le').first()
                if dernier_statut and dernier_statut.statut.appellation and dernier_statut.statut.appellation.lower() == "actif":
                    actifs.append({
                        "id": r.id,
                        "nom": r.nom,
                        "adresse": r.adresse,
                        "description": r.description,
                        "image": r.image,
                        "geo_position": r.geo_position
                    })
            return actifs
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des restaurants actifs : {str(e)}"}

    @staticmethod
    def list_repas_by_restaurant(restaurant_id):
        """
        Liste tous les repas proposés par un restaurant donné.
        """
        try:
            repas = Repas.objects.filter(restaurants_repas__restaurant_id=restaurant_id).distinct()
            return [{
                "id": r.id,
                "nom": r.nom,
                "prix": r.prix,
                "type": r.type.nom,
                "description": r.description,
                "image": r.image
            } for r in repas]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des repas du restaurant : {str(e)}"}

    @staticmethod
    def list_restaurants_by_zone(zone_id):
        """
        Liste tous les restaurants desservant une zone donnée.
        """
        try:
            restaurants = Restaurant.objects.filter(zonerestaurant__zone_id=zone_id).distinct()
            return [{
                "id": r.id,
                "nom": r.nom,
                "adresse": r.adresse,
                "description": r.description,
                "image": r.image,
                "geo_position": r.geo_position
            } for r in restaurants]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des restaurants par zone : {str(e)}"}

    @staticmethod
    def list_restaurants_by_horaire(jour=None):
        """
        Liste tous les restaurants ouverts aujourd'hui (ou pour un jour donné).
        jour: int (0=lundi, 6=dimanche). Si None, utilise le jour courant.
        """
        try:
            if jour is None:
                jour = datetime.now().weekday()
            horaires = Horaire.objects.filter(le_jour=jour)
            restaurant_ids = horaires.values_list('restaurant_id', flat=True).distinct()
            restaurants = Restaurant.objects.filter(id__in=restaurant_ids)
            return [{
                "id": r.id,
                "nom": r.nom,
                "adresse": r.adresse,
                "description": r.description,
                "image": r.image,
                "geo_position": r.geo_position
            } for r in restaurants]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des restaurants par horaire : {str(e)}"}


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

    @staticmethod
    def list_repas_disponibles():
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

    @staticmethod
    def list_livreurs_actifs():
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

    @staticmethod
    def list_zones_actives():
        """Liste toutes les zones actives (dernier statut = actif)."""
        try:
            actifs = []
            for z in Zone.objects.all():
                dernier_statut = z.historiques.order_by('-mis_a_jour_le').first()
                if dernier_statut and dernier_statut.statut.appellation and dernier_statut.statut.appellation.lower() == "actif":
                    actifs.append({
                        "id": z.id,
                        "nom": z.nom,
                        "description": z.description,
                        "zone": z.zone
                    })
            return actifs
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des zones actives : {str(e)}"}

