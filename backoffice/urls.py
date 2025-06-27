from django.urls import path
from . import views

urlpatterns = [
    # path('', views.test_create_client, name='/aa'),
    path('', views.PageAcceuil, name='accueil-backoffice'),
   path('restaurants/', views.get_restaurants, name='section-restaurant'),
    path('zones/', views.get_zones, name='section-zone'),
    path('stats/', views.get_stats, name='section-stat'),
    
    
]