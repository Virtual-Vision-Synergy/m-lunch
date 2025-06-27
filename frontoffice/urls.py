from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='frontoffice_index'),
    path('logout/', views.user_logout, name='logout'),
    path('panier/', views.panier, name='panier'),
    path('valider_panier/', views.valider_panier, name='valider_panier'),
]