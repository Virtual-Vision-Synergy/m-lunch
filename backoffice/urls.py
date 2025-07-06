from django.urls import path
from . import views
from .views import restaurant_views, commande_views, zone_views, stats_views, livraison_views

urlpatterns = [
    # Dashboard principal
    path('', views.index, name='backoffice_index'),

    # Gestion des restaurants
    path('restaurants/', restaurant_views.restaurant, name='backoffice_restaurant_list'),
    path('restaurants/<int:restaurant_id>/', restaurant_views.restaurant_detail, name='backoffice_restaurant_detail'),
    path('restaurants/<int:restaurant_id>/commandes/', restaurant_views.restaurant_commandes, name='backoffice_restaurant_commandes'),
    path('restaurants/ajouter/', restaurant_views.restaurant_ajouter, name='restaurant_add_form'),
    path('restaurants/nouveau/', restaurant_views.ajouter_restaurant, name='restaurant_create'),
    path('api/restaurants/<int:restaurant_id>/', restaurant_views.get_restaurant_detail, name='restaurant_api_detail'),
    path('api/restaurants/<int:restaurant_id>/statut/', restaurant_views.restaurant_update_statut, name='restaurant_update_statut'),

    # Gestion des commandes
    path('commandes/', commande_views.commande_list, name='commande_list'),
    path('commandes/<int:commande_id>/', commande_views.commande_detail, name='commande_detail'),
    path('commandes/en-attente/', commande_views.commandes_en_attente, name='commandes_en_attente'),
    path('api/commandes/<int:commande_id>/statut/', commande_views.commande_update_statut, name='commande_update_statut'),

    # Gestion des zones
    path('zones/', zone_views.zone_list, name='zone_list'),
    path('zones/<int:zone_id>/', zone_views.zone_detail, name='zone_detail'),
    path('zones/ajouter/', zone_views.zone_add, name='zone_add'),
    path('api/zones/<int:zone_id>/', zone_views.zone_update, name='zone_update'),
    path('api/zones/<int:zone_id>/supprimer/', zone_views.zone_delete, name='zone_delete'),

    # Statistiques et tableaux de bord
    path('stats/', stats_views.stats_dashboard, name='stats_dashboard'),
    path('api/stats/commandes/', stats_views.stats_commandes_api, name='stats_commandes_api'),
    path('api/stats/restaurants/', stats_views.stats_restaurants_api, name='stats_restaurants_api'),
    path('api/stats/zones/', stats_views.stats_zones_api, name='stats_zones_api'),

    #Livraison

    path('livreurs/', livraison_views.livreurs_list, name='livreurs_list'),
    path('livreurs/add/', livraison_views.livreur_add, name='livreur_add'),
    path('livreurs/<int:livreur_id>/', livraison_views.livreur_detail, name='livreur_detail'),

    path('livreurs/<int:livreur_id>/edit/', livraison_views.livreur_edit, name='livreur_edit'),
    path('livreurs/<int:livreur_id>/delete/', livraison_views.livreur_delete, name='livreur_delete'),

    # routes pour les livraisons
    path('livraisons/', livraison_views.livraisons_list, name='livraisons_list'),

    path('livraisons/<int:livraison_id>/', livraison_views.livraison_detail, name='livraison_detail'),

    path('livraisons/<int:livraison_id>/edit/', livraison_views.livraison_edit, name='livraison_edit'),

    path('livraisons/<int:livraison_id>/delete/', livraison_views.livraison_delete, name='livraison_delete'),
]
