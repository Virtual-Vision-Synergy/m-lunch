from django.shortcuts import render
from mlunch.core.services.commande_service import CommandeService
from .views.restaurant_views import *
from .views.commande_views import *
from .views.zone_views import *
from .views.stats_views import *
from .views.base_views import *

# Les fonctions sont maintenant importées depuis les modules spécialisés
