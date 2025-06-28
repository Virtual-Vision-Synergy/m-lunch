from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='frontoffice_index'),
    path('inscription/',views.inscription_page,name='inscription_page'),
    path('api/zone-from-coord/', views.api_zone_from_coord, name='api_zone_from_coord'),
    path('recherche/', views.barre_recherche, name='barre_recherche'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('panier/', views.panier_view, name='panier'),
    path('historique-commandes/', views.historique_commandes, name='historique_commandes'),
    path('commandes-en-cours/', views.commandes_en_cours, name='commandes_en_cours'),
    path('detail-commande/<int:commande_id>/', views.detail_commande, name='detail_commande'),
    path('annuler-commande/<int:commande_id>/', views.annuler_commande, name='annuler_commande'),
    path('add/', views.add_to_panier, name='add_to_panier'),
    path('update/', views.update_quantity, name='update_quantity'),
    path('remove/', views.remove_from_panier, name='remove_from_panier'),
    path('clear/', views.clear_panier, name='clear_panier'),
    
    # Validation et paiement
    path('checkout/', views.checkout_view, name='checkout'),
    path('validate/', views.validate_commande, name='validate_commande'),
    
    # Utilitaires
    path('count/', views.get_panier_count, name='panier_count'),
    
    # Pour les invités (optionnel)
    path('guest/', views.panier_guest_view, name='panier_guest'),
]
