from ..models import (
    Repas, DisponibiliteRepas,
    RestaurantRepas
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
                "image": r.image,
                "type": r.type.nom,
                "est_dispo": r.est_dispo
            } for r in repas]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des repas par type : {str(e)}"}

    @staticmethod
    def list_repas_by_restaurant(restaurant_id):
        # pdb.set_trace()
        """Liste les repas proposés par un restaurant spécifique."""
        try:
            # Récupérer les repas via la table de liaison RestaurantRepas
            repas = Repas.objects.filter(
                restaurantrepas__restaurant_id=restaurant_id
            ).select_related('type')

            return [{
                "id": r.id,
                "nom": r.nom,
                "prix": r.prix,
                "description": r.description,
                "image": r.image,
                "type": r.type.nom,
                "est_dispo": r.est_dispo
            } for r in repas]
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des repas du restaurant : {str(e)}"}

    @staticmethod
    def switch_disponibilite(repas_id, restaurant_id):
        """
        Change la disponibilité d'un repas pour un restaurant donné
        En créant une nouvelle entrée à chaque fois au lieu de mettre à jour
        """
        try:
            # Vérifier que le repas appartient au restaurant
            restaurant_repas = RestaurantRepas.objects.get(
                repas_id=repas_id,
                restaurant_id=restaurant_id
            )

            # Récupérer la disponibilité actuelle (dernière entrée uniquement)
            disponibilite_actuelle = DisponibiliteRepas.objects.filter(
                repas=restaurant_repas.repas
            ).order_by('-mis_a_jour_le').first()

            # Définir la nouvelle valeur (inverse de la valeur actuelle ou False par défaut)
            # Nous supposons que si un repas est toggled, il est toggled à False (non disponible)
            if disponibilite_actuelle:
                if disponibilite_actuelle.est_dispo:
                    nouvelle_valeur = False  # Si actuellement disponible, on le rend indisponible
                else:
                    nouvelle_valeur = True   # Si actuellement indisponible, on le rend disponible
            else:
                nouvelle_valeur = False  # Par défaut, quand on toggle pour la première fois, on rend indisponible

            # Créer une nouvelle entrée de disponibilité à chaque fois
            disponibilite = DisponibiliteRepas.objects.create(
                repas=restaurant_repas.repas,
                est_dispo=nouvelle_valeur
            )

            return {
                "success": True,
                "repas_id": repas_id,
                "nouvelle_disponibilite": disponibilite.est_dispo,
                "message": f"Repas {'activé' if disponibilite.est_dispo else 'désactivé'} avec succès"
            }

        except RestaurantRepas.DoesNotExist:
            return {"error": "Ce repas n'appartient pas à votre restaurant"}
        except Exception as e:
            return {"error": f"Erreur lors du changement de disponibilité : {str(e)}"}
