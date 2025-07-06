from django.db import models
from django.core.validators import validate_email
from django.utils.timezone import now

class Client(models.Model):
    email = models.EmailField(unique=True, validators=[validate_email])
    mot_de_passe = models.CharField(max_length=128)
    contact = models.CharField(max_length=50, blank=True, null=True)
    prenom = models.CharField(max_length=100, blank=True, null=True)
    nom = models.CharField(max_length=100, blank=True, null=True)
    date_inscri = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.prenom} {self.nom} <{self.email}>"

class StatutCommande(models.Model):
    appellation = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.appellation or "Sans appellation"

class Zone(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    zone = models.CharField(max_length=500, blank=True, null=True)
    def __str__(self):
        return self.nom

class ZoneClient(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    zone = models.ForeignKey('Zone', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('client', 'zone')

class ZoneLivreur(models.Model):
    zone = models.ForeignKey('Zone', on_delete=models.CASCADE)
    livreur = models.ForeignKey('Livreur', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('zone', 'livreur')

class PointRecup(models.Model):
    nom = models.CharField(max_length=150)
    geo_position = models.CharField(max_length=100, blank=True, null=True, default="0,0")
    def __str__(self):
        return self.nom

class Commande(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='commandes')
    point_recup = models.ForeignKey('PointRecup', on_delete=models.CASCADE)
    cree_le = models.DateTimeField(default=now)
    mode_paiement = models.ForeignKey('ModePaiement', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Commande {self.id} - {self.client}"


class HistoriqueStatutCommande(models.Model):
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE, related_name='historiques')
    statut = models.ForeignKey('StatutCommande', on_delete=models.CASCADE)
    mis_a_jour_le = models.DateTimeField(default=now)
    def __str__(self):
        return f"{self.commande} - {self.statut} ({self.mis_a_jour_le})"

class StatutRestaurant(models.Model):
    appellation = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.appellation or "Sans appellation"

class Restaurant(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    adresse = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    geo_position = models.CharField(max_length=100, blank=True, null=True, default="0,0")
    def __str__(self):
        return self.nom

class HistoriqueStatutRestaurant(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='historiques')
    statut = models.ForeignKey('StatutRestaurant', on_delete=models.CASCADE)
    mis_a_jour_le = models.DateTimeField(default=now)
    def __str__(self):
        return f"{self.restaurant} - {self.statut} ({self.mis_a_jour_le})"

class TypeRepas(models.Model):
    nom = models.CharField(max_length=100)
    def __str__(self):
        return self.nom

class Repas(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    type = models.ForeignKey('TypeRepas', on_delete=models.CASCADE)
    prix = models.IntegerField()
    def __str__(self):
        return self.nom
    
class DisponibiliteRepas(models.Model):
    repas = models.ForeignKey('Repas', on_delete=models.CASCADE, related_name='disponibilites')
    est_dispo = models.BooleanField(default=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.repas} - {'Disponible' if self.est_dispo else 'Indisponible'} ({self.mis_a_jour_le})"
    
class StatutLivreur(models.Model):
    appellation = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.appellation or "Sans appellation"

class Livreur(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    contact = models.TextField(blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    geo_position = models.CharField(max_length=100, blank=True, null=True, default="0,0", help_text="Format: latitude,longitude")
    date_inscri = models.DateTimeField(default=now)
    def __str__(self):
        return self.nom

class HistoriqueStatutLivreur(models.Model):
    livreur = models.ForeignKey('Livreur', on_delete=models.CASCADE, related_name='historiques')
    statut = models.ForeignKey('StatutLivreur', on_delete=models.CASCADE)
    mis_a_jour_le = models.DateTimeField(default=now)
    def __str__(self):
        return f"{self.livreur} - {self.statut} ({self.mis_a_jour_le})"

class StatutZone(models.Model):
    appellation = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.appellation or "Sans appellation"

class HistoriqueStatutZone(models.Model):
    zone = models.ForeignKey('Zone', on_delete=models.CASCADE, related_name='historiques')
    statut = models.ForeignKey('StatutZone', on_delete=models.CASCADE)
    mis_a_jour_le = models.DateTimeField(default=now)
    def __str__(self):
        return f"{self.zone} - {self.statut} ({self.mis_a_jour_le})"

class StatutLivraison(models.Model):
    appellation = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.appellation or "Sans appellation"

class Livraison(models.Model):
    livreur = models.ForeignKey('Livreur', on_delete=models.CASCADE, related_name='livraisons')
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE, related_name='livraisons')
    attribue_le = models.DateTimeField(default=now)
    def __str__(self):
        return f"Livraison {self.id} - {self.livreur} -> Commande {self.commande.id}"

class HistoriqueStatutLivraison(models.Model):
    livraison = models.ForeignKey('Livraison', on_delete=models.CASCADE, related_name='historiques')
    statut = models.ForeignKey('StatutLivraison', on_delete=models.CASCADE)
    mis_a_jour_le = models.DateTimeField(default=now)
    def __str__(self):
        return f"{self.livraison} - {self.statut} ({self.mis_a_jour_le})"

class CommandeRepas(models.Model):
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE, related_name='repas_commandes')
    repas = models.ForeignKey('Repas', on_delete=models.CASCADE, related_name='commandes_repas')
    quantite = models.IntegerField()
    ajoute_le = models.DateTimeField(default=now)
    class Meta:
        unique_together = ('commande', 'repas')
    def __str__(self):
        return f"{self.commande} - {self.repas} (x{self.quantite})"

class RestaurantRepas(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    repas = models.ForeignKey('Repas', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('restaurant', 'repas')

class ZoneRestaurant(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    zone = models.ForeignKey('Zone', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('restaurant', 'zone')

class Commission(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    valeur = models.IntegerField()
    mis_a_jour_le = models.DateTimeField(default=now)

class Horaire(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="horaire")
    le_jour = models.IntegerField()
    horaire_debut = models.TimeField()
    horaire_fin = models.TimeField()
    mis_a_jour_le = models.DateTimeField(auto_now=True)

class HoraireSpecial(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    date_concerne = models.DateField()
    horaire_debut = models.TimeField()
    horaire_fin = models.TimeField()
    mis_a_jour_le = models.DateTimeField(default=now)

class Promotion(models.Model):
    repas = models.ForeignKey('Repas', on_delete=models.CASCADE)
    pourcentage_reduction = models.IntegerField()
    date_concerne = models.DateField()

class LimiteCommandesJournalieres(models.Model):
    nombre_commandes = models.IntegerField()
    date = models.DateField()

class ModePaiement(models.Model):
    nom = models.CharField(max_length=150)
    def __str__(self):
        return self.nom

class StatutEntite(models.Model):
    appellation = models.CharField(max_length=100)
    def __str__(self):
        return self.appellation

class Entite(models.Model):
    nom = models.CharField(max_length=100)
    def __str__(self):
        return self.nom

class HistoriqueStatutEntite(models.Model):
    entite = models.ForeignKey('Entite', on_delete=models.CASCADE, related_name='historiques')
    statut = models.ForeignKey('StatutEntite', on_delete=models.CASCADE)
    mis_a_jour_le = models.DateTimeField(default=now)
    def __str__(self):
        return f"{self.entite} - {self.statut} ({self.mis_a_jour_le})"

class ReferenceZoneEntite(models.Model):
    zone = models.ForeignKey('Zone', on_delete=models.CASCADE)
    entite = models.ForeignKey('Entite', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('zone', 'entite')

class CommandePaiement(models.Model):
    paiement = models.ForeignKey('ModePaiement', on_delete=models.CASCADE)
    ajouter_le = models.DateTimeField(default=now)
    def __str__(self):
        return f"Paiement {self.paiement} - {self.ajouter_le}"

class HistoriqueZonesRecuperation(models.Model):
    zone = models.ForeignKey('Zone', on_delete=models.CASCADE, related_name='historiques_recuperation')
    point_recup = models.ForeignKey('PointRecup', on_delete=models.CASCADE)
    mis_a_jour_le = models.DateTimeField(default=now)
    def __str__(self):
        return f"{self.zone} - {self.point_recup} ({self.mis_a_jour_le})"
