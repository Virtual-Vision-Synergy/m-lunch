from django.urls import path
from . import views

urlpatterns = [
    path('', views.test_create_client, name='/aa'),
    path('Acceuil', views.PageAcceuil, name='/bb'),
   path('restaurants/', views.get_restaurants, name='get_restaurants'),
    path('zones/', views.get_zones, name='get_zones'),
    path('stats/', views.get_stats, name='get_stats'),
    
    
]