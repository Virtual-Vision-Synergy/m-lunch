import math

from django.db.models import Sum, F
from django.utils.timezone import now

from mlunch.core.services.commande_service import CommandeService
from mlunch.core.services.suivisCommande_service import SuivisCommandeService
from ..models import (
    Repas, RestaurantRepas, PointRecup, DisponibiliteRepas,
    Commande, CommandeRepas, HistoriqueStatutCommande, StatutCommande, ModePaiement, ZoneClient,
    HistoriqueZonesRecuperation
)


class PanierService:
    """
    Service pour gérer le panier en utilisant les sessions Django
    """

    @staticmethod
    def get_panier_items(client_id):
        """
        Récupère les articles du panier (commande en cours) depuis la base de données.
        """
        try:
            # Chercher la commande en cours (statut_id=1)
            commande = None
            commandes = Commande.objects.filter(client_id=client_id)
            for c in commandes:
                last_statut = c.historiques.order_by('-mis_a_jour_le').first()
                if last_statut and last_statut.statut_id == 1:
                    commande = c
                    break

            if not commande:
                return []

            items = []
            commande_repas = CommandeRepas.objects.filter(commande=commande).select_related('repas')
            for cr in commande_repas:
                repas = cr.repas
                # On récupère le premier restaurant associé au repas (si plusieurs)
                restaurant_repas = RestaurantRepas.objects.filter(repas=repas).select_related('restaurant').first()
                restaurant_nom = restaurant_repas.restaurant.nom if restaurant_repas else ""
                items.append({
                    'item_id': cr.id,
                    'repas_id': repas.id,
                    'nom': repas.nom,
                    'prix': repas.prix,
                    'quantite': cr.quantite,
                    'restaurant_nom': restaurant_nom,
                    'image': repas.image,
                    'total': cr.quantite * repas.prix
                })

            return items

        except Exception as e:
            return {"error": f"Erreur lors de la récupération du panier : {str(e)}"}

    @staticmethod
    def calculate_totals(client_id):
        """
        Calcule les totaux du panier
        """
        try:
            items = PanierService.get_panier_items(client_id)

            if isinstance(items, dict) and 'error' in items:
                return items

            sous_total = sum(item.get('total', 0) for item in items)
            frais_livraison = 3000  # Frais fixes pour l'exemple
            total = sous_total + frais_livraison

            return {
                'sous_total': sous_total,
                'frais_livraison': frais_livraison,
                'total': total,
                'nb_items': len(items)
            }

        except Exception as e:
            return {"error": f"Erreur lors du calcul des totaux : {str(e)}"}

    @staticmethod
    def add_to_panier(client_id, repas_id, quantite=1):
        """
        Ajoute un repas au panier (à implémenter avec session ou base de données)
        """
        try:
            # Vérifier que le repas existe et est disponible
            repas = Repas.objects.get(id=repas_id)

            # Vérifier la disponibilité
            is_dispo = DisponibiliteRepas.objects.filter(
                repas=repas,
                est_dispo=True
            ).exists()

            # if not is_dispo:
            #   return {"error": "Ce repas n'est pas disponible actuellement"}

            # Récupérer le restaurant qui propose ce repas
            restaurant_repas = RestaurantRepas.objects.filter(repas=repas).first()
            if not restaurant_repas:
                return {"error": "Restaurant non trouvé pour ce repas"}

            restaurant = restaurant_repas.restaurant

            # --- Nouvelle logique pour commande/statut ---
            from django.db import transaction

            with transaction.atomic():
                # Chercher une commande existante avec statut_id=1 (dernier statut)
                commande = None
                commandes = Commande.objects.filter(client_id=client_id)
                for c in commandes:
                    last_statut = c.historiques.order_by('-mis_a_jour_le').first()
                    if last_statut and last_statut.statut_id == 1:
                        commande = c
                        break
                if not commande:
                    commande = Commande.objects.create(client_id=client_id, point_recup_id=None)
                    HistoriqueStatutCommande.objects.create(commande=commande, statut_id=1)
                # Ajouter ou mettre à jour le repas dans commande_repas
                cr, created = CommandeRepas.objects.get_or_create(
                    commande=commande,
                    repas=repas,
                    defaults={'quantite': quantite}
                )
                if not created:
                    cr.quantite += quantite
                    cr.save()

            return {
                "success": True,
                "message": f"{repas.nom} ajouté au panier",
                "repas": {
                    "id": repas.id,
                    "nom": repas.nom,
                    "prix": repas.prix,
                    "restaurant": restaurant.nom
                }
            }

        except Repas.DoesNotExist:
            return {"error": "Repas non trouvé"}
        except Exception as e:
            return {"error": f"Erreur lors de l'ajout au panier : {str(e)}"}

    @staticmethod
    def get_points_recuperation(client_id):
        """
        Récupère les points de récupération dans un rayon de 3.5 km du centre des zones du client.
        """
        try:
            from shapely import wkt
            from shapely.geometry import Point
            import math
            import re

            # 1️⃣ Zones du client
            zones = ZoneClient.objects.filter(client_id=client_id).select_related('zone')
            if not zones:
                return {"error": "Le client n'a aucune zone associée."}

            points_dans_rayon = []
            rayon_km = 2

            # 2️⃣ Pour chaque zone du client
            for zone_client in zones:
                zone = zone_client.zone

                try:
                    # Calculer le centre de la zone (centroïde du polygone)
                    if zone.zone:
                        poly = wkt.loads(zone.zone)
                        centre_zone = poly.centroid
                        centre_lat = centre_zone.y
                        centre_lon = centre_zone.x

                        # 3️⃣ Récupérer tous les points de récupération
                        tous_points = PointRecup.objects.all()

                        for point in tous_points:
                            if point.geo_position and point.geo_position != "0,0":
                                try:
                                    # Extraire les coordonnées du point
                                    point_lat, point_lon = PanierService._parse_geo_position(point.geo_position)

                                    if point_lat is not None and point_lon is not None:
                                        # Calculer la distance en km en utilisant la formule de Haversine
                                        distance_km = PanierService._calculate_distance(
                                            centre_lat, centre_lon, point_lat, point_lon
                                        )

                                        # Si le point est dans le rayon, l'ajouter
                                        if distance_km <= rayon_km:
                                            point_info = {
                                                'id': point.id,
                                                'nom': point.nom,
                                                'geo_position': point.geo_position,
                                                'distance_km': round(distance_km, 2),
                                                'zone_nom': zone.nom
                                            }
                                            # Éviter les doublons
                                            if not any(p['id'] == point.id for p in points_dans_rayon):
                                                points_dans_rayon.append(point_info)
                                except (ValueError, IndexError):
                                    continue
                except Exception as e:
                    print(f"Erreur lors du traitement de la zone {zone.nom}: {str(e)}")
                    continue

            # 4️⃣ Trier par distance
            points_dans_rayon.sort(key=lambda x: x['distance_km'])

            return points_dans_rayon

        except Exception as e:
            return {"error": f"Erreur lors de la récupération des points de récupération : {str(e)}"}

    @staticmethod
    def _parse_geo_position(geo_position):
        """
        Parse les coordonnées géographiques depuis différents formats :
        - Format 1: "lat,lon" (ex: "47.5220,-18.9000")
        - Format 2: "POINT(lon lat)" (ex: "POINT(47.5220 -18.9000)")

        Retourne (lat, lon) ou (None, None) si erreur
        """
        try:
            import re

            # Nettoyer la chaîne
            geo_position = geo_position.strip()

            # Format POINT(lon lat)
            if geo_position.startswith('POINT('):
                # Extraire les coordonnées du format POINT(lon lat)
                match = re.match(r'POINT\(\s*([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s*\)', geo_position)
                if match:
                    lon = float(match.group(1))
                    lat = float(match.group(2))
                    return lat, lon

            # Format lat,lon
            elif ',' in geo_position:
                coords = geo_position.split(',')
                if len(coords) == 2:
                    lat = float(coords[0])
                    lon = float(coords[1])
                    return lat, lon

            # Format lon lat (sans virgule)
            elif ' ' in geo_position:
                coords = geo_position.split()
                if len(coords) == 2:
                    lon = float(coords[0])
                    lat = float(coords[1])
                    return lat, lon

            return None, None

        except (ValueError, AttributeError, IndexError):
            return None, None

    @staticmethod
    def _calculate_distance(lat1, lon1, lat2, lon2):
        """
        Calcule la distance entre deux points géographiques en utilisant la formule de Haversine.
        Retourne la distance en kilomètres.
        """
        # Rayon de la Terre en km
        R = 6371.0

        # Convertir les degrés en radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Différences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Formule de Haversine
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Distance en km
        distance = R * c
        return distance

    @staticmethod
    def remove_from_panier(client_id, item_id):
        """
        Supprime un article du panier (commande en cours) pour le client donné.
        """
        try:
            # Trouver la commande en cours (statut_id=1)
            commande = None
            commandes = Commande.objects.filter(client_id=client_id)
            for c in commandes:
                last_statut = c.historiques.order_by('-mis_a_jour_le').first()
                if last_statut and last_statut.statut_id == 1:
                    commande = c
                    break

            if not commande:
                return {"error": "Aucune commande en cours trouvée."}

            # Supprimer l'article CommandeRepas correspondant
            deleted, _ = CommandeRepas.objects.filter(id=item_id, commande=commande).delete()
            if deleted == 0:
                return {"error": "Article non trouvé dans le panier."}

            return {"success": True, "message": "Article supprimé du panier"}

        except Exception as e:
            return {"error": f"Erreur lors de la suppression : {str(e)}"}

    @staticmethod
    def clear_panier(client_id):
        """
        Vide le panier en supprimant tous les articles de la commande en cours
        """
        try:
            # Trouver la commande en cours (statut_id=1)
            commande = None
            commandes = Commande.objects.filter(client_id=client_id)
            for c in commandes:
                last_statut = c.historiques.order_by('-mis_a_jour_le').first()
                if last_statut and last_statut.statut_id == 1:
                    commande = c
                    break

            if commande:
                # Supprimer tous les articles de la commande
                CommandeRepas.objects.filter(commande=commande).delete()
                print(f"Panier vidé pour le client {client_id}, commande {commande.id}")
            
            return {"success": True, "message": "Panier vidé"}

        except Exception as e:
            return {"error": f"Erreur lors du vidage du panier : {str(e)}"}

    @staticmethod
    def update_quantity(client_id, item_id, nouvelle_quantite):
        """
        Met à jour la quantité d'un article dans le panier
        """
        try:
            if nouvelle_quantite <= 0:
                return PanierService.remove_from_panier(client_id, item_id)

            # Trouver la commande en cours (statut_id=1)
            commande = None
            commandes = Commande.objects.filter(client_id=client_id)
            for c in commandes:
                last_statut = c.historiques.order_by('-mis_a_jour_le').first()
                if last_statut and last_statut.statut_id == 1:
                    commande = c
                    break

            if not commande:
                return {"error": "Aucune commande en cours trouvée."}

            # Trouver l'article à mettre à jour
            try:
                cr = CommandeRepas.objects.get(id=item_id, commande=commande)
            except CommandeRepas.DoesNotExist:
                return {"error": "Article non trouvé dans le panier."}

            cr.quantite = nouvelle_quantite
            cr.save()

            return {"success": True, "message": "Quantité mise à jour"}

        except Exception as e:
            return {"error": f"Erreur lors de la mise à jour : {str(e)}"}

    @staticmethod
    def get_panier_restaurants(client_id):
        """
        Récupère la liste des restaurants présents dans le panier
        """
        try:
            items = PanierService.get_panier_items(client_id)

            if isinstance(items, dict) and 'error' in items:
                return items

            restaurants = list(set(item.get('restaurant_nom', '') for item in items))
            return restaurants

        except Exception as e:
            return {"error": f"Erreur lors de la récupération des restaurants : {str(e)}"}

    @staticmethod
    def validate_panier_for_checkout(client_id):
        """
        Valide le panier avant la commande
        """
        try:
            items = PanierService.get_panier_items(client_id)

            if isinstance(items, dict) and 'error' in items:
                return items

            if not items:
                return {"error": "Le panier est vide"}

            # Vérifier que tous les articles sont encore disponibles
            for item in items:
                repas = Repas.objects.get(id=item['repas_id'])
                is_dispo = DisponibiliteRepas.objects.filter(
                    repas=repas,
                    est_dispo=True
                ).exists()

                if not is_dispo:
                    return {"error": f"Le repas '{item['nom']}' n'est plus disponible"}

            return {"success": True, "message": "Panier valide pour la commande"}

        except Exception as e:
            return {"error": f"Erreur lors de la validation : {str(e)}"}

    @staticmethod
    def validate_commande(client_id, point_recup_id, mode_paiement):
        """
        Valide une commande et la crée en base de données
        """
        try:
            from ..models import Commande, CommandeRepas, PointRecup, ModePaiement, StatutCommande, \
                HistoriqueStatutCommande
            from django.db import transaction

            # Vérifications des paramètres obligatoires
            if not client_id:
                return False, "ID client manquant"
            
            if not point_recup_id:
                return False, "Point de récupération manquant"
            
            if not mode_paiement:
                return False, "Mode de paiement manquant"

            # Vérifier que le panier n'est pas vide
            items = PanierService.get_panier_items(client_id)
            if isinstance(items, dict) and 'error' in items:
                return False, items['error']

            if not items:
                return False, "Votre panier est vide"

            # Valider le panier
            validation_result = PanierService.validate_panier_for_checkout(client_id)
            if isinstance(validation_result, dict) and 'error' in validation_result:
                return False, validation_result['error']

            # Vérifier que le point de récupération existe
            try:
                point_recup = PointRecup.objects.get(id=point_recup_id)
            except PointRecup.DoesNotExist:
                return False, "Point de récupération invalide"

            # Vérifier que le mode de paiement existe
            mode_paiement_obj = None
            if mode_paiement:
                try:
                    mode_paiement_obj = ModePaiement.objects.get(id=mode_paiement)
                except ModePaiement.DoesNotExist:
                    return False, "Mode de paiement invalide"

            # Créer la commande
            with transaction.atomic():
                # Chercher une commande existante avec statut_id=1 (dernier statut)
                commande = None
                commandes = Commande.objects.filter(client_id=client_id)
                for c in commandes:
                    last_statut = c.historiques.order_by('-mis_a_jour_le').first()
                    if last_statut and last_statut.statut_id == 1:
                        commande = c
                        break

                if not commande:
                    return False, "Aucune commande en cours trouvée. Ajoutez d'abord des articles au panier."

                # Vérifier que la commande a un ID valide
                if not commande.id:
                    return False, "Commande invalide (ID manquant)"

                # Mettre à jour le point de récupération et le mode de paiement
                commande.point_recup_id = point_recup_id
                if mode_paiement_obj:
                    commande.mode_paiement = mode_paiement_obj
                commande.save()
                print(f"Commande {commande.id} mise à jour avec point_recup_id={point_recup_id} et mode_paiement_id={mode_paiement}")

                # Les repas sont déjà dans la commande (ajoutés via add_to_panier)
                # On vérifie juste qu'ils sont bien présents
                commande_repas = CommandeRepas.objects.filter(commande=commande)
                repas_ids = [r.repas_id for r in commande_repas]
                print(f"Repas déjà dans la commande : {repas_ids}")

                # Vérifier qu'il y a bien des repas dans la commande
                if not repas_ids:
                    return False, "Aucun repas trouvé dans la commande"

                # Créer l'historique de statut initial
                try:
                    # Passer directement au statut "En cours" (id=2) après validation
                    statut_en_cours = StatutCommande.objects.filter(
                        appellation__icontains='En cours'
                    ).first()
                    
                    if not statut_en_cours:
                        # Fallback : utiliser l'ID 2 si pas trouvé par nom
                        statut_en_cours = StatutCommande.objects.filter(id=2).first()
                    
                    if statut_en_cours:
                        HistoriqueStatutCommande.objects.create(
                            commande=commande,
                            statut=statut_en_cours
                        )
                        print(f"Commande {commande.id} mise à jour au statut 'En cours'")
                except Exception as e:
                    print(f"Erreur lors de la mise à jour du statut : {str(e)}")
                    pass  # Pas critique si l'historique échoue
                
                suivis_list = []
                try:
                    # Debug : vérifier la table RestaurantRepas pour les repas de la commande
                    for repas_id in repas_ids:
                        if not repas_id:
                            print(f"ATTENTION: Repas avec ID null trouvé dans la commande")
                            continue
                        restaurant_repas = RestaurantRepas.objects.filter(repas_id=repas_id).first()
                        if restaurant_repas:
                            if not restaurant_repas.restaurant_id:
                                print(f"ATTENTION: Restaurant ID null pour le repas {repas_id}")
                                continue
                            print(f"Repas {repas_id} -> Restaurant {restaurant_repas.restaurant_id} ({restaurant_repas.restaurant.nom})")
                        else:
                            print(f"ATTENTION: Repas {repas_id} n'a pas de restaurant associé dans RestaurantRepas")
                    
                    restaurant_ids = CommandeService.get_all_id_restaurant_from_commande(commande.id)
                    print(f"Restaurants trouvés pour la commande : {restaurant_ids}")
                    
                    # Filtrer les IDs null ou invalides
                    restaurant_ids = [rid for rid in restaurant_ids if rid is not None and rid > 0]
                    print(f"Restaurants valides après filtrage : {restaurant_ids}")
                    
                    if not restaurant_ids:
                        print("Aucun restaurant valide trouvé pour les repas de la commande. Vérifiez la table RestaurantRepas.")
                        return False, "Aucun restaurant valide trouvé pour les repas de la commande. Impossible de créer les suivis."
                    
                    # Créer un suivi pour chaque restaurant via le service
                    for restaurant_id in restaurant_ids:
                        if not restaurant_id:
                            print(f"ATTENTION: Restaurant ID null ignoré")
                            continue
                        suivi_data = SuivisCommandeService.ajouter_suivi(
                            commande_id=commande.id,
                            restaurant_id=restaurant_id,
                        )
                        print(f"Suivi créé pour restaurant {restaurant_id} : {suivi_data}")
                        
                        # Vérifier que le suivi a été créé avec succès
                        if isinstance(suivi_data, dict) and 'error' in suivi_data:
                            print(f"Erreur lors de la création du suivi pour restaurant {restaurant_id}: {suivi_data['error']}")
                            return False, f"Erreur lors de la création du suivi: {suivi_data['error']}"
                        
                        suivis_list.append(suivi_data)
                except Exception as e:
                    print(f"Erreur lors de la création des suivis : {str(e)}")
                    return False, f"Erreur lors de la création des suivis : {str(e)}"
                # Vider le panier après création de la commande
                PanierService.clear_panier(client_id)
                return True, f"Commande #{commande.id} créée avec succès"

        except Exception as e:
            return False, f"Erreur lors de la validation de la commande : {str(e)}"

    @staticmethod
    def get_all_modes_paiement():
        """
        Récupère tous les modes de paiement disponibles.
        """
        try:
            modes = ModePaiement.objects.all().values('id', 'nom')
            return list(modes)
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des modes de paiement : {str(e)}"}

    @staticmethod
    def finalize_commande(client_id, point_recup_id, mode_paiement):
        """
        Finalise une commande et retourne un dictionnaire avec le résultat
        """
        try:
            success, message = PanierService.validate_commande(client_id, point_recup_id, mode_paiement)
            
            if success:
                # Vider le panier après finalisation réussie
                PanierService.clear_panier(client_id)
                return {
                    "success": True,
                    "message": message
                }
            else:
                return {
                    "error": message
                }
        except Exception as e:
            return {
                "error": f"Erreur lors de la finalisation de la commande : {str(e)}"
            }
