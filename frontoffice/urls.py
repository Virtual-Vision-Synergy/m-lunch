from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='frontoffice_index'),
    # path('logout/', views.user_logout, name='logout'),
    # path('panier/', views.panier, name='panier'),
    # path('valider_panier/', views.valider_panier, name='valider_panier'),
    path('',views.index,name='frontoffice_index'),
    path('inscription/',views.inscription_page,name='inscription_page'),
    path('api/zone-from-coord/', views.api_zone_from_coord, name='api_zone_from_coord'),

]
