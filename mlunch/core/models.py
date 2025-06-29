from django.db import models
from django.core.validators import validate_email

class Client(models.Model):
    email = models.EmailField(unique=True, validators=[validate_email])
    mot_de_passe = models.CharField(max_length=128)
    contact = models.CharField(max_length=50, blank=True, null=True)
    prenom = models.CharField(max_length=50, blank=True, null=True)
    nom = models.CharField(max_length=50, blank=True, null=True)
    date_inscri = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prenom} {self.nom} <{self.email}>"

class StatutCommande(models.Model):
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom

class ZoneClient(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    zone = models.ForeignKey('Zone', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('client', 'zone')

class PointRecup(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

class Commande(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='commandes')
    point_recup = models.ForeignKey('PointRecup', on_delete=models.CASCADE)
    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande {self.id} - {self.client}"

class HistoriqueStatutCommande(models.Model):
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE, related_name='historiques')
    statut = models.ForeignKey('StatutCommande', on_delete=models.CASCADE)
    mis_a_jour_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commande} - {self.statut} ({self.mis_a_jour_le})"

class StatutRestaurant(models.Model):
    nom = models.CharField(max_length=50)
    def __str__(self):
        return self.nom

class Restaurant(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    geo_position = models.CharField(max_length=100, blank=True, null=True)  # Pour simplifier, sinon utiliser django.contrib.gis
    def __str__(self):
        return self.nom

class HistoriqueStatutRestaurant(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='historiques')
    statut = models.ForeignKey('StatutRestaurant', on_delete=models.CASCADE)
    mis_a_jour_le = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.restaurant} - {self.statut} ({self.mis_a_jour_le})"

class TypeRepas(models.Model):
    nom = models.CharField(max_length=50)
    def __str__(self):
        return self.nom

class Repas(models.Model):
    nom = models.CharField(max_length=100)
    type = models.ForeignKey('TypeRepas', on_delete=models.CASCADE)
    prix = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    est_dispo = models.BooleanField(default=True)
    def __str__(self):
        return self.nom

class StatutLivreur(models.Model):
    nom = models.CharField(max_length=50)
    def __str__(self):
        return self.nom

class Livreur(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    contact = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)  # Pour simplifier, sinon utiliser django.contrib.gis
    date_inscri = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nom

class HistoriqueStatutLivreur(models.Model):
    livreur = models.ForeignKey('Livreur', on_delete=models.CASCADE, related_name='historiques')
    statut = models.ForeignKey('StatutLivreur', on_delete=models.CASCADE)
    mis_a_jour_le = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.livreur} - {self.statut} ({self.mis_a_jour_le})"

class StatutZone(models.Model):
    nom = models.CharField(max_length=50)
    def __str__(self):
        return self.nom

class Zone(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100)
    zone = models.CharField(max_length=500)  # Pour simplifier, sinon utiliser django.contrib.gis
    def __str__(self):
        return self.nom

class HistoriqueStatutZone(models.Model):
    zone = models.ForeignKey('Zone', on_delete=models.CASCADE, related_name='historiques')
    statut = models.ForeignKey('StatutZone', on_delete=models.CASCADE)
    mis_a_jour_le = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.zone} - {self.statut} ({self.mis_a_jour_le})"

class StatutLivraison(models.Model):
    nom = models.CharField(max_length=50)
    def __str__(self):
        return self.nom

class Livraison(models.Model):
    livreur = models.ForeignKey('Livreur', on_delete=models.CASCADE, related_name='livraisons')
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE, related_name='livraisons')
    attribue_le = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Livraison {self.id} - {self.livreur} -> Commande {self.commande.id}"

class HistoriqueStatutLivraison(models.Model):
    livraison = models.ForeignKey('Livraison', on_delete=models.CASCADE, related_name='historiques')
    statut = models.ForeignKey('StatutLivraison', on_delete=models.CASCADE)
    mis_a_jour_le = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.livraison} - {self.statut} ({self.mis_a_jour_le})"

class CommandeRepas(models.Model):
    """Table de liaison entre commandes et repas avec quantité"""
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE, related_name='repas_commandes')
    repas = models.ForeignKey('Repas', on_delete=models.CASCADE, related_name='commandes_repas')
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.PositiveIntegerField()  # Prix au moment de la commande

    class Meta:
        unique_together = ('commande', 'repas')

    def __str__(self):
        return f"{self.commande} - {self.repas} (x{self.quantite})"

class RestaurantRepas(models.Model):
    """Table de liaison entre restaurants et repas"""
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='repas_restaurants')
    repas = models.ForeignKey('Repas', on_delete=models.CASCADE, related_name='restaurants_repas')
    disponible = models.BooleanField(default=True)

    class Meta:
        unique_together = ('restaurant', 'repas')

    def __str__(self):
        return f"{self.restaurant} - {self.repas}"

class ZoneRestaurant(models.Model):
    """Table de liaison entre zones et restaurants"""
    zone = models.ForeignKey('Zone', on_delete=models.CASCADE, related_name='restaurants_zones')
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='zones_restaurants')

    class Meta:
        unique_together = ('zone', 'restaurant')

    def __str__(self):
        return f"{self.zone} - {self.restaurant}"

class Promotion(models.Model):
    """Promotions appliquées aux repas"""
    repas = models.ForeignKey('Repas', on_delete=models.CASCADE, related_name='promotions')
    pourcentage_reduction = models.PositiveIntegerField()  # Pourcentage de réduction
    date_debut = models.DateField()
    date_fin = models.DateField()

    def __str__(self):
        return f"{self.repas} - {self.pourcentage_reduction}% ({self.date_debut} à {self.date_fin})"
