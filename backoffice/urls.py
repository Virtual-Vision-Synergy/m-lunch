from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='backoffice_index'),
    # routes pour les restaurants
    path('restaurants/', views.restaurants_list, name='restaurants_list'),
    path('restaurants/add/', views.restaurant_add, name='restaurant_add'),
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurants/<int:restaurant_id>/edit/', views.restaurant_edit, name='restaurant_edit'),
    path('restaurants/<int:restaurant_id>/delete/', views.restaurant_delete, name='restaurant_delete'),
    path('restaurants/<int:restaurant_id>/orders/', views.restaurant_orders, name='restaurant_orders'),
    path('restaurants/<int:restaurant_id>/financial/', views.restaurant_financial, name='restaurant_financial'),

    # routes pour les livreurs
    path('livreurs/', views.livreurs_list, name='livreurs_list'),
    path('livreurs/add/', views.livreur_add, name='livreur_add'),
    path('livreurs/<int:livreur_id>/', views.livreur_detail, name='livreur_detail'),
    path('livreurs/<int:livreur_id>/edit/', views.livreur_edit, name='livreur_edit'),
    path('livreurs/<int:livreur_id>/delete/', views.livreur_delete, name='livreur_delete'),

    # routes pour les livraisons
    path('livraisons/', views.livraisons_list, name='livraisons_list'),
    path('livraisons/<int:livraison_id>/', views.livraison_detail, name='livraison_detail'),
    path('livraisons/<int:livraison_id>/edit/', views.livraison_edit, name='livraison_edit'),
    path('livraisons/<int:livraison_id>/delete/', views.livraison_delete, name='livraison_delete'),

    path('zones/', views.zones_list, name='zones_list'),
    path('zones/add/', views.zone_add, name='zone_add'),
    path('zones/<int:zone_id>/edit/', views.zone_edit, name='zone_edit'),
    path('zones/<int:zone_id>/delete/', views.zone_delete, name='zone_delete'),
    
    path('', views.test_create_client, name='/aa'),
]