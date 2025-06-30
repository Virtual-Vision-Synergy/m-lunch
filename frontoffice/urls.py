from django.urls import path
from . import views

urlpatterns = [
    path('',views.accueil_view,name='frontoffice_accueil'),
    path('connexion/',views.connexion_view,name='frontoffice_connexion'),
    path('restaurant/', views.restaurant_view, name='frontoffice_restaurant'),
    path('api/restaurants/', views.restaurants_geojson, name='restaurants_geojson'),
    path('menu/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('mes_commandes/', views.mes_commandes, name='mes_commandes'),
    path('commande/<int:commande_id>/', views.detail_commande, name='detail_commande'),
    path('api/points_de_recuperation/', views.points_de_recuperation, name='points_de_recuperation'),
    path('api/all_restaurants/', views.all_restaurants, name='all_restaurants'),
    path('deconnexion/', views.logout_view, name='frontoffice_logout'),

    path('',views.index,name='frontoffice_index'),
    path('inscription/',views.inscription_page,name='inscription_page'),
    path('api/zone-from-coord/', views.api_zone_from_coord, name='api_zone_from_coord'),

]
