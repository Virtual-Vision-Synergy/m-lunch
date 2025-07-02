from django.urls import path
from . import views
from . import CommandeAttente
from . import CommandeRestaurant
from . import LivreurCRUD

urlpatterns = [
    path('', views.index, name='backoffice_index'),
    path('commande_attente_restaurant/', CommandeAttente.GetCommandeAttente, name='GetCommandeAttente'),
    path('restaurant/<int:restaurant_id>/commandes/', CommandeRestaurant.GetCommandeResto, name='GetCommandeResto'),
    path('livreurs/', LivreurCRUD.livreur_list, name='livreur_list'),
    path('livreurs/create/', LivreurCRUD.create_livreur, name='create_livreur'),
    path('livreurs/<int:livreur_id>/update/', LivreurCRUD.update_livreur, name='update_livreur'),
    path('livreurs/<int:livreur_id>/delete/', LivreurCRUD.delete_livreur, name='delete_livreur'),
    path('livreurs/<int:livreur_id>/details/', LivreurCRUD.livreur_details, name='livreur_details'),
    path('livreurs/<int:livreur_id>/assign/', LivreurCRUD.assign_order, name='assign_order'),
]