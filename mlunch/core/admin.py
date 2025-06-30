from django.contrib import admin
from .models import (
    Client, StatutCommande, PointRecup, Commande, HistoriqueStatutCommande,
    StatutRestaurant, Restaurant, HistoriqueStatutRestaurant,
    TypeRepas, Repas, StatutLivreur, Livreur, HistoriqueStatutLivreur,
    StatutZone, Zone, HistoriqueStatutZone,
    StatutLivraison, Livraison, HistoriqueStatutLivraison
)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'prenom', 'nom', 'contact', 'date_inscri')
    search_fields = ('email', 'prenom', 'nom')
    list_filter = ('date_inscri',)

@admin.register(StatutCommande)
class StatutCommandeAdmin(admin.ModelAdmin):
    list_display = ('nom',)

@admin.register(PointRecup)
class PointRecupAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse')

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'point_recup', 'cree_le')
    list_filter = ('cree_le',)
    search_fields = ('client__email',)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse')
    search_fields = ('nom',)

@admin.register(Repas)
class RepasAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type', 'prix', 'est_dispo')
    list_filter = ('type', 'est_dispo')
    search_fields = ('nom',)

@admin.register(Livreur)
class LivreurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'contact', 'date_inscri')
    search_fields = ('nom',)

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom',)

@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('id', 'livreur', 'commande', 'attribue_le')
    list_filter = ('attribue_le',)

# Enregistrement des modèles de statut
admin.site.register(StatutRestaurant)
admin.site.register(TypeRepas)
admin.site.register(StatutLivreur)
admin.site.register(StatutZone)
admin.site.register(StatutLivraison)

# Enregistrement des modèles d'historique
admin.site.register(HistoriqueStatutCommande)
admin.site.register(HistoriqueStatutRestaurant)
admin.site.register(HistoriqueStatutLivreur)
admin.site.register(HistoriqueStatutZone)
admin.site.register(HistoriqueStatutLivraison)
