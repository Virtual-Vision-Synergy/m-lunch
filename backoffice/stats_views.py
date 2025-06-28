from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.utils import timezone
import json
from mlunch.core.models import (
    Restaurant, Zone, Commande, Repas, TypeRepas, Client,
    CommandeRepas, RestaurantRepas, ZoneRestaurant, Promotion
)
from django.shortcuts import render

def testchart(request):
    return render(request, 'backoffice/stats_dashboard.html')

@csrf_exempt
def get_stats(request):
    """API pour récupérer les statistiques selon les filtres."""
    if request.method != 'POST':
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    try:
        data = json.loads(request.body)
        base_filter = data.get('base_filter')  # 'zone' ou 'restaurant'
        zone_id = data.get('zone_id')  # Optionnel si base_filter='zone'
        restaurant_id = data.get('restaurant_id')  # Optionnel si base_filter='restaurant'
        temporal_filter = data.get('temporal_filter')  # 'day', 'month', 'year'
        content_filter = data.get('content_filter')  # 'revenue' ou 'orders_by_type'

        # Validation des filtres
        if base_filter not in ['zone', 'restaurant']:
            return JsonResponse({"error": "Filtre de base invalide"}, status=400)
        if temporal_filter not in ['day', 'month', 'year']:
            return JsonResponse({"error": "Filtre temporel invalide"}, status=400)
        if content_filter not in ['revenue', 'orders_by_type']:
            return JsonResponse({"error": "Filtre de contenu invalide"}, status=400)
        if base_filter == 'zone' and (not zone_id or not isinstance(zone_id, int)):
            return JsonResponse({"error": "ID de zone invalide"}, status=400)
        if base_filter == 'restaurant' and (not restaurant_id or not isinstance(restaurant_id, int)):
            return JsonResponse({"error": "ID de restaurant invalide"}, status=400)

        # Vérifier que l'ID existe
        if base_filter == 'zone':
            if not Zone.objects.filter(id=zone_id).exists():
                return JsonResponse({"error": "Zone non trouvée"}, status=404)
        else:
            if not Restaurant.objects.filter(id=restaurant_id).exists():
                return JsonResponse({"error": "Restaurant non trouvé"}, status=404)

        # Déterminer le groupement temporel
        trunc_functions = {
            'day': TruncDay,
            'month': TruncMonth,
            'year': TruncYear
        }
        trunc_func = trunc_functions[temporal_filter]

        # Base queryset des commandes avec filtrage
        if base_filter == 'zone':
            # Filtrer les commandes par zone via les restaurants
            commandes_queryset = Commande.objects.filter(
                repas_commandes__repas__restaurants_repas__restaurant__zones_restaurants__zone_id=zone_id
            ).distinct()
        else:  # restaurant
            # Filtrer les commandes par restaurant
            commandes_queryset = Commande.objects.filter(
                repas_commandes__repas__restaurants_repas__restaurant_id=restaurant_id
            ).distinct()

        if content_filter == 'revenue':
            # Chiffre d'affaires réel basé sur les commandes et les prix des repas
            stats = commandes_queryset.annotate(
                period=trunc_func('cree_le')
            ).values('period').annotate(
                revenue=Sum(F('repas_commandes__quantite') * F('repas_commandes__prix_unitaire'))
            ).order_by('period')

            results = [
                {
                    'period': stat['period'].strftime('%Y-%m-%d' if temporal_filter == 'day'
                                                   else '%Y-%m' if temporal_filter == 'month'
                                                   else '%Y'),
                    'revenue': stat['revenue'] or 0
                }
                for stat in stats
            ]

        else:  # orders_by_type
            # Nombre de commandes par type de repas avec filtrage approprié
            if base_filter == 'zone':
                type_stats = CommandeRepas.objects.filter(
                    repas__restaurants_repas__restaurant__zones_restaurants__zone_id=zone_id
                ).values('repas__type__nom').annotate(
                    order_count=Sum('quantite')
                ).order_by('-order_count')
            else:  # restaurant
                type_stats = CommandeRepas.objects.filter(
                    repas__restaurants_repas__restaurant_id=restaurant_id
                ).values('repas__type__nom').annotate(
                    order_count=Sum('quantite')
                ).order_by('-order_count')

            results = [
                {
                    'type_repas': stat['repas__type__nom'] or "Type non défini",
                    'order_count': stat['order_count']
                }
                for stat in type_stats
            ]

        return JsonResponse({"data": results})

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invalide"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Erreur interne: {str(e)}"}, status=500)

@csrf_exempt
def get_zones(request):
    """API pour récupérer la liste des zones avec le nombre de restaurants."""
    try:
        zones = Zone.objects.annotate(
            restaurant_count=Count('restaurants_zones')
        ).values('id', 'nom', 'description', 'restaurant_count')
        return JsonResponse({"zones": list(zones)})
    except Exception as e:
        return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

@csrf_exempt
def get_restaurants(request):
    """API pour récupérer la liste des restaurants avec informations supplémentaires."""
    try:
        restaurants = Restaurant.objects.annotate(
            zone_count=Count('zones_restaurants'),
            repas_count=Count('repas_restaurants')
        ).values('id', 'nom', 'adresse', 'zone_count', 'repas_count')
        return JsonResponse({"restaurants": list(restaurants)})
    except Exception as e:
        return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

@csrf_exempt
def get_dashboard_summary(request):
    """API pour récupérer un résumé complet pour le dashboard."""
    try:
        # Statistiques générales
        total_clients = Client.objects.count()
        total_commandes = Commande.objects.count()
        total_restaurants = Restaurant.objects.count()
        total_zones = Zone.objects.count()
        total_repas = Repas.objects.count()

        # Commandes récentes (dernières 7 jours)
        from datetime import timedelta
        recent_date = timezone.now() - timedelta(days=7)
        recent_commandes = Commande.objects.filter(cree_le__gte=recent_date).count()

        # Chiffre d'affaires total (si des commandes existent)
        total_revenue = CommandeRepas.objects.aggregate(
            total=Sum(F('quantite') * F('prix_unitaire'))
        )['total'] or 0

        # Top 5 des repas les plus commandés
        top_repas = CommandeRepas.objects.values('repas__nom').annotate(
            total_quantite=Sum('quantite')
        ).order_by('-total_quantite')[:5]

        summary = {
            'total_clients': total_clients,
            'total_commandes': total_commandes,
            'total_restaurants': total_restaurants,
            'total_zones': total_zones,
            'total_repas': total_repas,
            'recent_commandes': recent_commandes,
            'total_revenue': total_revenue,
            'growth_rate': round((recent_commandes / max(total_commandes, 1)) * 100, 2),
            'top_repas': list(top_repas)
        }

        return JsonResponse({"summary": summary})
    except Exception as e:
        return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)
