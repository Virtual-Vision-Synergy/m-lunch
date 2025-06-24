from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='frontoffice_index'),
    path('connexion/',views.connexion_view,name='frontoffice_connexion'),
    path('accueil/', views.accueil_view, name='frontoffice_accueil'),
    path('api/restaurants/', views.restaurants_geojson, name='restaurants_geojson'),
    path('menu/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('mes_commandes/', views.mes_commandes, name='mes_commandes'),
    path('commande/<int:commande_id>/', views.detail_commande, name='detail_commande')

]