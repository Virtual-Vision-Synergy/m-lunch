from django.urls import path
from . import views
from .views import restaurant_views, commande_views, zone_views, stats_views, livraison_views, livreur_views

urlpatterns = [
    # Dashboard principal
    path('', views.index, name='index'),

    # Gestion des restaurants
    path('restaurants/', restaurant_views.restaurant, name='restaurant_list'),
    path('restaurants/<int:restaurant_id>/', restaurant_views.restaurant_detail, name='restaurant_detail'),
    path('restaurants/<int:restaurant_id>/commandes/', restaurant_views.restaurant_commandes, name='restaurant_commandes'),
    path('restaurants/ajouter/', restaurant_views.restaurant_ajouter, name='restaurant_add_form'),
    path('restaurants/nouveau/', restaurant_views.ajouter_restaurant, name='restaurant_create'),
    path('api/restaurants/<int:restaurant_id>/', restaurant_views.get_restaurant_detail, name='restaurant_api_detail'),
    path('api/restaurants/<int:restaurant_id>/statut/', restaurant_views.restaurant_update_statut, name='restaurant_update_statut'),

    # Gestion des commandes
    path('commandes/', commande_views.commande_list, name='commande_list'),
    path('commandes/<int:commande_id>/', commande_views.commande_detail, name='commande_detail'),
    path('commandes/en-attente/', commande_views.commandes_en_attente, name='commandes_en_attente'),
    path('commandes/<int:commande_id>/attribuer/', commande_views.commande_attribuer, name='commande_attribuer'),
    path('commandes/<int:commande_id>/attribuer/confirmer/', commande_views.commande_attribuer_confirmer, name='commande_attribuer_confirmer'),
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

    # Nouvelles APIs pour le dashboard unifié
    path('api/stats/', stats_views.stats_api, name='stats_api'),
    path('api/zones/', stats_views.zones_api, name='zones_api'),
    path('api/restaurants/', stats_views.restaurants_api, name='restaurants_api'),

    # Gestion des livreurs
    path('livreurs/', livreur_views.livreurs_list, name='livreurs_list'),
    path('livreurs/add/', livreur_views.livreur_add, name='livreur_add'),
    path('livreurs/<int:livreur_id>/', livreur_views.livreur_detail, name='livreur_detail'),
    path('livreurs/<int:livreur_id>/edit/', livreur_views.livreur_edit, name='livreur_edit'),
    path('livreurs/<int:livreur_id>/delete/', livreur_views.livreur_delete, name='livreur_delete'),
    path('livreurs/<int:livreur_id>/assigner-commande/', livreur_views.livreur_assigner_commande, name='livreur_assigner_commande'),
    path('livreurs/<int:livreur_id>/assigner-commande/confirmer/', livreur_views.livreur_assigner_commande_confirmer, name='livreur_assigner_commande_confirmer'),
]
