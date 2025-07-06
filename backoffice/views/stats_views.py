from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Q, DecimalField
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.views.decorators.csrf import csrf_exempt
from mlunch.core.models import Commande, Restaurant, Client, CommandeRepas, Zone
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
        total=Sum(F('repas__prix') * F('quantite'), output_field=DecimalField())
    )['total'] or Decimal('0')

    # Commandes par statut - correction de la relation
    commandes_par_statut = Commande.objects.values(
        'historiques__statut__appellation'
    ).annotate(count=Count('id')).order_by('-count')

    # Top 5 des restaurants par nombre de commandes - simplification de la relation
    top_restaurants = Restaurant.objects.annotate(
        nb_commandes=Count('restaurantrepas__repas__commandes_repas__commande', distinct=True)
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
        ca=Sum(F('repas_commandes__repas__prix') * F('repas_commandes__quantite'), output_field=DecimalField())
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
        nb_commandes=Count('restaurantrepas__repas__commandes_repas__commande', distinct=True),
        ca=Sum(F('restaurantrepas__repas__commandes_repas__repas__prix') * F('restaurantrepas__repas__commandes_repas__quantite'), output_field=DecimalField())
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
        nb_commandes=Count('zonerestaurant__restaurant__restaurantrepas__repas__commandes_repas__commande', distinct=True)
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

@csrf_exempt
def stats_api(request):
    """API unifiée pour les statistiques avec tous les filtres"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    try:
        import json
        data = json.loads(request.body)

        base_filter = data.get('base_filter', 'secteur')
        temporal_filter = data.get('temporal_filter', 'day')
        content_filter = data.get('content_filter', 'chiffre_affaires')
        secteur_id = data.get('secteur_id')
        restaurant_id = data.get('restaurant_id')
        section = data.get('section', 'restaurant')

        # Fonction de troncature selon la période
        if temporal_filter == 'day':
            truncate_func = TruncDay
            date_format = '%Y-%m-%d'
        elif temporal_filter == 'month':
            truncate_func = TruncMonth
            date_format = '%Y-%m'
        else:  # year
            truncate_func = TruncYear
            date_format = '%Y'

        # Construction de la requête de base
        from mlunch.core.models import Zone, ZoneRestaurant

        if base_filter == 'secteur':
            # Statistiques par secteur
            if secteur_id:
                # Secteur spécifique
                commandes_query = Commande.objects.filter(
                    repas_commandes__repas__restaurantrepas__restaurant__zonerestaurant__zone_id=secteur_id
                )
            else:
                # Tous les secteurs
                commandes_query = Commande.objects.all()
        else:
            # Statistiques par restaurant
            if restaurant_id:
                commandes_query = Commande.objects.filter(
                    repas_commandes__repas__restaurantrepas__restaurant_id=restaurant_id
                )
            else:
                return JsonResponse({'error': 'Restaurant requis pour ce filtre'}, status=400)

        # Agrégation selon le contenu demandé
        if content_filter == 'chiffre_affaires':
            # Chiffre d'affaires par période
            stats = commandes_query.annotate(
                periode=truncate_func('cree_le')
            ).values('periode').annotate(
                total=Sum(F('repas_commandes__repas__prix') * F('repas_commandes__quantite'), output_field=DecimalField())
            ).order_by('periode')

            labels = []
            values = []
            for stat in stats:
                labels.append(stat['periode'].strftime(date_format))
                values.append(float(stat['total'] or 0))

            main_chart = {
                'title': 'Chiffre d\'affaires',
                'labels': labels,
                'data': values,
                'label': 'Chiffre d\'affaires (ariary)',
                'y_label': 'Montant (ariary)'
            }

            # Pie chart pour répartition CA par restaurant/secteur
            if base_filter == 'secteur' and not secteur_id:
                pie_data = Zone.objects.annotate(
                    ca=Sum(F('zonerestaurant__restaurant__restaurantrepas__repas__commandes_repas__repas__prix') *
                          F('zonerestaurant__restaurant__restaurantrepas__repas__commandes_repas__quantite'),
                          output_field=DecimalField())
                ).values('nom', 'ca').order_by('-ca')[:8]

                pie_chart = {
                    'title': 'CA par secteur',
                    'labels': [item['nom'] for item in pie_data],
                    'data': [float(item['ca'] or 0) for item in pie_data]
                }
            else:
                pie_chart = None

        elif content_filter == 'chiffre_vente':
            # Nombre de commandes par période
            stats = commandes_query.annotate(
                periode=truncate_func('cree_le')
            ).values('periode').annotate(
                count=Count('id')
            ).order_by('periode')

            labels = []
            values = []
            for stat in stats:
                labels.append(stat['periode'].strftime(date_format))
                values.append(stat['count'])

            main_chart = {
                'title': 'Nombre de commandes',
                'labels': labels,
                'data': values,
                'label': 'Nombre de commandes',
                'y_label': 'Nombre'
            }

            # Pie chart pour statuts des commandes
            statut_stats = commandes_query.values(
                'historiques__statut__appellation'
            ).annotate(count=Count('id')).order_by('-count')

            pie_chart = {
                'title': 'Commandes par statut',
                'labels': [item['historiques__statut__appellation'] or 'Inconnu'
                          for item in statut_stats],
                'data': [item['count'] for item in statut_stats]
            }

        else:  # types_repas
            # Types de repas vendus
            from mlunch.core.models import TypeRepas
            type_stats = CommandeRepas.objects.filter(
                commande__in=commandes_query
            ).values(
                'repas__type__nom'
            ).annotate(
                quantite_totale=Sum('quantite')
            ).order_by('-quantite_totale')

            main_chart = {
                'title': 'Types de repas les plus vendus',
                'labels': [item['repas__type__nom'] for item in type_stats],
                'data': [item['quantite_totale'] for item in type_stats],
                'label': 'Quantité vendue',
                'y_label': 'Quantité'
            }

            # Évolution temporelle des types de repas
            temporal_stats = CommandeRepas.objects.filter(
                commande__in=commandes_query
            ).annotate(
                periode=truncate_func('commande__cree_le')
            ).values('periode').annotate(
                total=Sum('quantite')
            ).order_by('periode')

            pie_chart = {
                'title': 'Évolution des ventes',
                'labels': [stat['periode'].strftime(date_format) for stat in temporal_stats],
                'data': [stat['total'] for stat in temporal_stats]
            }

        return JsonResponse({
            'main_chart': main_chart,
            'pie_chart': pie_chart
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def zones_api(request):
    """API pour récupérer la liste des zones"""
    zones = Zone.objects.all().values('id', 'nom')
    return JsonResponse({'zones': list(zones)})

def restaurants_api(request):
    """API pour récupérer la liste des restaurants"""
    restaurants = Restaurant.objects.all().values('id', 'nom')
    return JsonResponse({'restaurants': list(restaurants)})
