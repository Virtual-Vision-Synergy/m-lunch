from django.urls import path

from .views import signin_views, views, zone_views, restaurant_views, panier_views,commande_views
    
urlpatterns = [
    # Pages principales
    path('', views.accueil, name='frontoffice_index'),

    # mitia
    # randy
    path('connexion/', views.connexion_view, name='connexion'),
    path('signin/', signin_views.signin, name='signin'),
    path('logout/', views.logout_view, name='frontoffice_logout'),

    # Restaurants et recherche
    path('restaurants/', restaurant_views.restaurant_list, name='restaurant_list'),
    path('restaurants/<int:restaurant_id>/', restaurant_views.restaurant_detail, name='restaurant_detail'),
    path('recherche/', restaurant_views.barre_recherche_view, name='barre_recherche'),
    path('api/restaurants/', restaurant_views.restaurants_geojson, name='restaurants_geojson'),
    path('api/all_restaurants/', restaurant_views.all_restaurants, name='all_restaurants'),
    path('api/points_de_recuperation/', zone_views.points_de_recuperation, name='points_de_recuperation'),
    path('api/zone-from-coord/', restaurant_views.api_zone_from_coord, name='api_zone_from_coord'),
    path('menu/<int:restaurant_id>/', restaurant_views.restaurant_detail, name='restaurant_detail'),
    
    # Commandes
    path('mes-commandes/', commande_views.mes_commandes, name='mes_commandes'),
    path('commandes/en-cours/', commande_views.commandes_en_cours, name='commandes_en_cours'),
    path('commandes/<int:commande_id>/', commande_views.detail_commande, name='detail_commande'),
    path('api/commandes/<int:commande_id>/annuler/', commande_views.annuler_commande, name='annuler_commande'),
    path('api/commandes/<int:commande_id>/reorder/', commande_views.reorder_commande, name='reorder_commande'),

    # Panier
    path('panier/', panier_views.panier_view, name='panier'),
    path('api/panier/ajouter/', panier_views.add_to_panier, name='add_to_panier'),
    path('api/panier/update/<int:item_id>/', panier_views.update_quantity, name='update_quantity'),
    path('api/panier/supprimer/<int:item_id>/', panier_views.remove_from_panier, name='remove_from_panier'),
    path('api/panier/vider/', panier_views.clear_panier, name='clear_panier'),
    path('api/panier/valider/', panier_views.finalize_commande, name='finalize_commande'),
    path('api/panier/count/', panier_views.get_panier_count, name='panier_count'),

    path('api/panier/modes-paiement/', panier_views.get_modes_paiement, name='get_modes_paiement'),
    path('api/points-recuperation/', zone_views.points_de_recuperation, name='points_recuperation'),
    path('api/zone-from-coord/', zone_views.api_zone_from_coord, name='zone_from_coord'),
]
