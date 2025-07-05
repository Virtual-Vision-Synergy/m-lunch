from django.urls import path
from .views import auth_views

urlpatterns = [
    # Authentification
    path('login/', auth_views.login_view, name='restaurant_login'),
    path('connexion/', auth_views.login, name='restaurant_connexion'),
    path('logout/', auth_views.logout, name='restaurant_logout'),
    path('dashboard/', auth_views.dashboard_view, name='restaurant_dashboard'),

    # API pour gestion des repas
    path('api/repas/toggle-disponibilite/', auth_views.toggle_disponibilite_repas, name='toggle_disponibilite_repas'),

    # Gestion des commandes
    path('commande/<int:commande_id>/', auth_views.commande_details_view, name='commande_details'),
    path('api/commande/modifier-statut/', auth_views.modifier_statut_commande, name='modifier_statut_commande'),
]
