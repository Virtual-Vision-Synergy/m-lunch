from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Q, DecimalField
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from mlunch.core.models import Commande, Restaurant, Client, CommandeRepas
from decimal import Decimal
import json

def stats_dashboard(request):
    """Tableau de bord avec les statistiques principales"""
    # Statistiques générales
    total_commandes = Commande.objects.count()
    total_restaurants = Restaurant.objects.count()
    total_clients = Client.objects.count()

    # Chiffre d'affaires total
    ca_total = CommandeRepas.objects.aggregate(
        total=Sum(F('prix') * F('quantite'), output_field=DecimalField())
    )['total'] or Decimal('0')

    # Commandes par statut
    commandes_par_statut = Commande.objects.values(
        'statut__appellation'
    ).annotate(count=Count('id')).order_by('-count')

    # Top 5 des restaurants par nombre de commandes
    top_restaurants = Restaurant.objects.annotate(
        nb_commandes=Count('commanderepas__commande', distinct=True)
    ).order_by('-nb_commandes')[:5]

    return render(request, 'backoffice/stats_dashboard.html', {
        'total_commandes': total_commandes,
        'total_restaurants': total_restaurants,
        'total_clients': total_clients,
        'ca_total': ca_total,
        'commandes_par_statut': commandes_par_statut,
        'top_restaurants': top_restaurants
    })

def stats_commandes_api(request):
    """API pour les statistiques des commandes par période"""
    periode = request.GET.get('periode', 'jour')

    if periode == 'jour':
        truncate_func = TruncDay
    elif periode == 'mois':
        truncate_func = TruncMonth
    else:
        truncate_func = TruncYear

    stats = Commande.objects.annotate(
        periode=truncate_func('cree_le')
    ).values('periode').annotate(
        count=Count('id'),
        ca=Sum(F('commanderepas__prix') * F('commanderepas__quantite'), output_field=DecimalField())
    ).order_by('periode')

    data = []
    for stat in stats:
        data.append({
            'periode': stat['periode'].strftime('%Y-%m-%d' if periode == 'jour' else '%Y-%m' if periode == 'mois' else '%Y'),
            'count': stat['count'],
            'ca': float(stat['ca'] or 0)
        })

    return JsonResponse(data, safe=False)

def stats_restaurants_api(request):
    """API pour les statistiques des restaurants"""
    stats = Restaurant.objects.annotate(
        nb_commandes=Count('commanderepas__commande', distinct=True),
        ca=Sum(F('commanderepas__prix') * F('commanderepas__quantite'), output_field=DecimalField())
    ).values('id', 'nom', 'nb_commandes', 'ca').order_by('-nb_commandes')

    data = []
    for stat in stats:
        data.append({
            'restaurant_id': stat['id'],
            'nom': stat['nom'],
            'nb_commandes': stat['nb_commandes'],
            'ca': float(stat['ca'] or 0)
        })

    return JsonResponse(data, safe=False)

def stats_zones_api(request):
    """API pour les statistiques par zone"""
    from mlunch.core.models import Zone, ZoneRestaurant

    stats = Zone.objects.annotate(
        nb_restaurants=Count('zonerestaurant__restaurant', distinct=True),
        nb_clients=Count('zoneclient__client', distinct=True),
        nb_commandes=Count('zonerestaurant__restaurant__commanderepas__commande', distinct=True)
    ).values('id', 'nom', 'nb_restaurants', 'nb_clients', 'nb_commandes')

    data = []
    for stat in stats:
        data.append({
            'zone_id': stat['id'],
            'nom': stat['nom'],
            'nb_restaurants': stat['nb_restaurants'],
            'nb_clients': stat['nb_clients'],
            'nb_commandes': stat['nb_commandes']
        })

    return JsonResponse(data, safe=False)
