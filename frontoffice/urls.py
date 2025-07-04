from django.urls import path
from . import views

urlpatterns = [
    path('',views.accueil_view,name='frontoffice_accueil'),
    path('connexion/',views.connexion_view,name='frontoffice_connexion'),

    path('restaurant/', views.restaurant_view, name='frontoffice_restaurant'),
    path('menu/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('mes_commandes/', views.mes_commandes, name='mes_commandes'),
    path('commande/<int:commande_id>/', views.detail_commande, name='detail_commande'),

    path('deconnexion/', views.logout_view, name='frontoffice_logout'),

    path('',views.index,name='frontoffice_index'),
    path('inscription/',views.inscription_page,name='inscription_page'),
    path('recherche/', views.barre_recherche, name='barre_recherche'),

    path('panier/', views.panier_view, name='panier'),

    path('add/', views.add_to_panier, name='add_to_panier'),
    path('update/', views.update_quantity, name='update_quantity'),
    path('remove/', views.remove_from_panier, name='remove_from_panier'),
    path('clear/', views.clear_panier, name='clear_panier'),

    path('validate/', views.validate_commande, name='validate_commande'),


    #Commandes
    path('historique-commandes/', views.historique_commandes, name='historique_commandes'),
    path('commandes-en-cours/', views.commandes_en_cours, name='commandes_en_cours'),
    path('detail-commande/<int:commande_id>/', views.detail_commande, name='detail_commande'),
    path('annuler-commande/<int:commande_id>/', views.annuler_commande, name='annuler_commande'),
    # Utilitaires
    path('count/', views.get_panier_count, name='panier_count'),
    path('api/restaurants/', views.restaurants_geojson, name='restaurants_geojson'),

    path('api/zone-from-coord/', views.api_zone_from_coord, name='api_zone_from_coord'),

]
