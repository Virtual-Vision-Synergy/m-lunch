import pdb
from django.utils.timezone import now
from datetime import datetime
from django.db import transaction
from ..models import (
    Restaurant, StatutRestaurant, HistoriqueStatutRestaurant, HistoriqueStatutCommande, Commission, Horaire, Zone, ZoneRestaurant, Repas, Commande, StatutCommande
)


class RestaurantService:
    @staticmethod
    def create_restaurant(nom, initial_statut_id, adresse=None, image=None, geo_position=None):
        # pdb.set_trace()
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
        # pdb.set_trace()
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
                        mis_a_jour_le=now()
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
        # pdb.set_trace()
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
        # pdb.set_trace()
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
        # pdb.set_trace()
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
        # pdb.set_trace()
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
        # pdb.set_trace()
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

    @staticmethod
    def list_restaurants_all():
        # pdb.set_trace()
        """
        Retourne la liste de tous les restaurants (sans filtrage de statut).
        """
        try:
            restaurants = Restaurant.objects.all()
            return [{
                "id": r.id,
                "nom": r.nom,
                "adresse": r.adresse,
                "description": r.description,
                "image": r.image,
                "geo_position": r.geo_position
            } for r in restaurants]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération de tous les restaurants : {str(e)}"}

    @staticmethod
    def get_restaurant_details(restaurant_id):
        # pdb.set_trace()
        """
        Retourne les détails d'un restaurant :
        - image, nom, secteur (zones), commission (valeur la plus récente), horaire (liste), statut (dernier)
        """
        try:
            r = Restaurant.objects.get(id=restaurant_id)
            # Image et nom
            image = r.image
            nom = r.nom
            # Secteurs (zones)
            secteurs = list(r.zonerestaurant_set.select_related('zone').values_list('zone__nom', flat=True))
            # Commission la plus récente
            commission_obj = r.commission_set.order_by('-mis_a_jour_le').first()
            commission = commission_obj.valeur if commission_obj else None
            # Horaires
            horaires = list(r.horaire.all().values('le_jour', 'horaire_debut', 'horaire_fin'))
            # Statut (dernier historique)
            historique = r.historiques.order_by('-mis_a_jour_le').first()
            statut = historique.statut.appellation if historique and historique.statut else None

            return {
                "id": r.id,
                "nom": nom,
                "image": image,
                "secteurs": secteurs,
                "commission": commission,
                "horaire": horaires,
                "statut": statut
            }
        except Restaurant.DoesNotExist:
            return {"error": "Restaurant non trouvé"}
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des détails du restaurant : {str(e)}"}

    @staticmethod
    def list_restaurants_all_details():
        # pdb.set_trace()
        """
        Retourne la liste de tous les restaurants avec détails :
        image, nom, secteur, commission, horaire, statut
        """
        try:
            restaurants = Restaurant.objects.all()
            return [RestaurantService.get_restaurant_details(r.id) for r in restaurants]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération de tous les restaurants : {str(e)}"}

    @staticmethod
    def list_restaurant_filtrer(idzone=None, idstatut=None):
        # pdb.set_trace()
        """
        Retourne la liste détaillée des restaurants filtrés par secteur (zone, id) et/ou statut (id).
        Les filtres peuvent être combinés.
        - idzone : id de la zone
        - idstatut : id du statut
        """
        try:
            qs = Restaurant.objects.all()
            # Filtre zone par id
            if idzone:
                qs = qs.filter(zonerestaurant__zone__id=idzone)
            qs = qs.distinct()
            # Filtre statut (dernier historique) par id
            if idstatut:
                ids_statut = []
                for r in qs:
                    dernier_statut = r.historiques.order_by('-mis_a_jour_le').first()
                    if dernier_statut and dernier_statut.statut_id == int(idstatut):
                        ids_statut.append(r.id)
                qs = qs.filter(id__in=ids_statut)
            return [RestaurantService.get_restaurant_details(r.id) for r in qs]
        except Exception as e:
            return {"error": f"Erreur lors du filtrage des restaurants : {str(e)}"}

    @staticmethod
    def get_all_statuts():
        """
        Retourne la liste de tous les statuts de restaurant disponibles.
        """
        try:
            return list(StatutRestaurant.objects.values('id', 'appellation'))
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des statuts : {str(e)}"}