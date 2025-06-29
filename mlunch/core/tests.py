from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Client, Commande, Restaurant, Repas, Livreur, Zone, Livraison
from .services import ClientService, CommandeService, RestaurantService, RepasService, LivreurService, ZoneService, LivraisonService


class ClientServiceTestCase(TestCase):
    def test_create_client_valid(self):
        """Test de création d'un client valide"""
        result = ClientService.create_client(
            email="test@example.com",
            mot_de_passe="password123",
            prenom="John",
            nom="Doe"
        )
        self.assertIn("client", result)
        self.assertEqual(result["client"]["email"], "test@example.com")

    def test_create_client_invalid_email(self):
        """Test de création d'un client avec email invalide"""
        result = ClientService.create_client(
            email="invalid-email",
            mot_de_passe="password123"
        )
        self.assertIn("error", result)


class CommandeServiceTestCase(TestCase):
    def setUp(self):
        """Mise en place des données de test"""
        from .models import StatutCommande, PointRecup
        self.client = Client.objects.create(
            email="test@example.com",
            mot_de_passe="password123"
        )
        self.point_recup = PointRecup.objects.create(
            nom="Point Test",
            adresse="123 Test Street"
        )
        self.statut = StatutCommande.objects.create(nom="En attente")

    def test_create_commande_valid(self):
        """Test de création d'une commande valide"""
        result = CommandeService.create_commande(
            client_id=self.client.id,
            point_recup_id=self.point_recup.id,
            initial_statut_id=self.statut.id
        )
        self.assertIn("commande", result)
        self.assertEqual(result["commande"]["client_id"], self.client.id)


class RestaurantServiceTestCase(TestCase):
    def setUp(self):
        from .models import StatutRestaurant
        self.statut = StatutRestaurant.objects.create(nom="Ouvert")

    def test_create_restaurant_valid(self):
        """Test de création d'un restaurant valide"""
        result = RestaurantService.create_restaurant(
            nom="Restaurant Test",
            initial_statut_id=self.statut.id,
            adresse="123 Restaurant Street"
        )
        self.assertIn("restaurant", result)
        self.assertEqual(result["restaurant"]["nom"], "Restaurant Test")


class RepasServiceTestCase(TestCase):
    def setUp(self):
        from .models import TypeRepas
        self.type_repas = TypeRepas.objects.create(nom="Plat principal")

    def test_create_repas_valid(self):
        """Test de création d'un repas valide"""
        result = RepasService.create_repas(
            nom="Pizza Margherita",
            type_id=self.type_repas.id,
            prix=1200
        )
        self.assertIn("nom", result)
        self.assertEqual(result["nom"], "Pizza Margherita")


class LivreurServiceTestCase(TestCase):
    def setUp(self):
        from .models import StatutLivreur
        self.statut = StatutLivreur.objects.create(nom="Disponible")

    def test_create_livreur_valid(self):
        """Test de création d'un livreur valide"""
        result = LivreurService.create_livreur(
            nom="Jean Livreur",
            initial_statut_id=self.statut.id,
            contact="0123456789"
        )
        self.assertIn("livreur", result)
        self.assertEqual(result["livreur"]["nom"], "Jean Livreur")


class ZoneServiceTestCase(TestCase):
    def setUp(self):
        from .models import StatutZone
        self.statut = StatutZone.objects.create(nom="Active")

    def test_create_zone_valid(self):
        """Test de création d'une zone valide"""
        coordinates = [[2.3522, 48.8566], [2.3622, 48.8566], [2.3622, 48.8666], [2.3522, 48.8666]]
        result = ZoneService.create_zone(
            nom="Zone Paris Centre",
            description="Zone de livraison Paris centre",
            coordinates=coordinates,
            initial_statut_id=self.statut.id
        )
        self.assertIn("zone", result)
        self.assertEqual(result["zone"]["nom"], "Zone Paris Centre")


class LivraisonServiceTestCase(TestCase):
    def setUp(self):
        from .models import StatutLivraison, StatutLivreur, StatutCommande, PointRecup

        # Créer les statuts nécessaires
        self.statut_livraison = StatutLivraison.objects.create(nom="Attribué")
        self.statut_livreur = StatutLivreur.objects.create(nom="Disponible")
        self.statut_commande = StatutCommande.objects.create(nom="En attente")

        # Créer un client et point de récupération
        self.client = Client.objects.create(email="test@example.com", mot_de_passe="password123")
        self.point_recup = PointRecup.objects.create(nom="Point Test", adresse="123 Test Street")

        # Créer un livreur
        self.livreur = Livreur.objects.create(nom="Jean Livreur")

        # Créer une commande
        self.commande = Commande.objects.create(
            client=self.client,
            point_recup=self.point_recup
        )

    def test_create_livraison_valid(self):
        """Test de création d'une livraison valide"""
        result = LivraisonService.create_livraison(
            livreur_id=self.livreur.id,
            commande_id=self.commande.id,
            initial_statut_id=self.statut_livraison.id
        )
        self.assertIn("livraison", result)
        self.assertEqual(result["livraison"]["livreur_id"], self.livreur.id)
