from django.urls import path
from . import views
from .views import signin_views, commande_views

app_name = 'frontoffice'

urlpatterns = [
    # Pages principales
    path('', views.index, name='index'),
    path('accueil/', views.accueil, name='accueil'),

    # Authentification
    path('connexion/', views.connexion_view, name='connexion'),
    path('inscription/', signin_views.signin, name='signin'),
    path('register/', signin_views.register, name='register'),
    path('register-view/', signin_views.register_view, name='register_view'),
    path('deconnexion/', views.logout_view, name='logout'),
    path('api/check-email/', signin_views.check_email_availability, name='check_email'),

    # Restaurants et recherche
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('recherche/', views.barre_recherche, name='barre_recherche'),
    path('api/restaurants/geojson/', views.restaurants_geojson, name='restaurants_geojson'),
    path('api/restaurants/all/', views.all_restaurants, name='all_restaurants'),

    # Commandes
    path('mes-commandes/', commande_views.mes_commandes, name='mes_commandes'),
    path('commandes/en-cours/', commande_views.commandes_en_cours, name='commandes_en_cours'),
    path('commandes/historique/', commande_views.historique_commandes, name='historique_commandes'),
    path('commandes/<int:commande_id>/', commande_views.detail_commande, name='detail_commande'),
    path('api/commandes/<int:commande_id>/annuler/', commande_views.annuler_commande, name='annuler_commande'),
    path('api/commandes/<int:commande_id>/reorder/', commande_views.reorder_commande, name='reorder_commande'),

    # Panier
    path('panier/', views.panier_view, name='panier'),
    path('api/panier/ajouter/', views.add_to_panier, name='add_to_panier'),
    path('api/panier/update/', views.update_quantity, name='update_quantity'),
    path('api/panier/supprimer/', views.remove_from_panier, name='remove_from_panier'),
    path('api/panier/vider/', views.clear_panier, name='clear_panier'),
    path('api/panier/valider/', views.validate_commande, name='validate_commande'),
    path('api/panier/count/', views.get_panier_count, name='panier_count'),

    # APIs utilitaires
    path('api/points-recuperation/', views.points_de_recuperation, name='points_recuperation'),
    path('api/zone-from-coord/', views.api_zone_from_coord, name='zone_from_coord'),
]
