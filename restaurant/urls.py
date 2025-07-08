from django.urls import path
from .views import auth_views

urlpatterns = [
    # Authentification
    path('', auth_views.login_view, name='restaurant_login'),
    path('connexion/', auth_views.login, name='restaurant_connexion'),
    path('logout/', auth_views.logout, name='restaurant_logout'),
    path('dashboard/', auth_views.dashboard_view, name='restaurant_dashboard'),

    # API pour gestion des repas
    path('api/repas/toggle-disponibilite/', auth_views.toggle_disponibilite_repas, name='toggle_disponibilite_repas'),

    # Gestion des commandes
    path('commande/<int:commande_id>/', auth_views.commande_details_view, name='commande_details'), 
    path('commande/<int:commande_id>/modification/', auth_views.modifier_statut_commande, name='mettre_en_preparation'),
    
    # path('api/commande/modifier-statut/', auth_views.modifier_statut_commande, name='modifier_statut_commande'),
    path('api/commande/modifier-statut/', auth_views.modifier_statut_suivis, name='modifier_statut_suivis'),
    
    #gestion restaurant
    path('modifier-restaurant/', auth_views.form_modif_restaurant, name="modifier_restaurant"),
    path('modification/', auth_views.modifer_restaurant, name="modifier"),
    path('changer-statut/', auth_views.changer_statut_restaurant, name="changer-statut"),

    # Gestion des plats
    path('plats/ajouter/', auth_views.ajouter_plat_form, name="ajouter_plat"),
    path('plats/nouveau/', auth_views.ajouter_plat, name="creer_plat"),
]
