from django.db import models

class Client(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=255)
    contact = models.TextField(blank=True, null=True)
    prenom = models.CharField(max_length=100, blank=True, null=True)
    nom = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'clients'
        managed = False  # Important! Don't let Django try to create or alter this table.

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"

from django.contrib.gis.db import models  # for PostGIS support

class Zone(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    description = models.CharField(max_length=100, blank=True, null=True)
    zone = models.PolygonField(geography=True, srid=4326)

    class Meta:
        db_table = 'zones'
        managed = False

    def __str__(self):
        return self.nom

class Restaurant(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=150)
    horaire_debut = models.TimeField()
    horaire_fin = models.TimeField()
    adresse = models.TextField()
    image = models.TextField(blank=True, null=True)  # chemin ou URL
    geo_position = models.PointField(geography=True, srid=4326)

    class Meta:
        db_table = 'restaurants'
        managed = False

    def __str__(self):
        return self.nom

class ZoneRestaurant(models.Model):
    id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.DO_NOTHING)  # Define Restaurant model
    zone = models.ForeignKey(Zone, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'zones_restaurant'
        managed = False


class ZoneClient(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey('Client', on_delete=models.DO_NOTHING)  # Reuse your Client model
    zone = models.ForeignKey(Zone, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'zones_clients'
        managed = False

class TypeRepas(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)

    class Meta:
        db_table = 'types_repas'
        managed = False

    def __str__(self):
        return self.nom


class Repas(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    type = models.ForeignKey(TypeRepas, on_delete=models.DO_NOTHING)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'repas'
        managed = False

    def __str__(self):
        return self.nom


class RepasRestaurant(models.Model):
    id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    repas = models.ForeignKey(Repas, on_delete=models.CASCADE)

    class Meta:
        db_table = 'repas_restaurant'
        managed = False
