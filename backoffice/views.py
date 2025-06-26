from django.shortcuts import render, redirect
from mlunch.core.Restaurant import Restaurant
from mlunch.core.Livreur import Livreur
from database import db
from datetime import datetime, timedelta
from django.shortcuts import render
from django.contrib import messages
from mlunch.core.Client import Client
from mlunch.core.Commande import Commande
from mlunch.core.Livraison import Livraison
from mlunch.core.Livreur import Livreur
from mlunch.core.Repas import Repas
from mlunch.core.Restaurant import Restaurant
from mlunch.core.Zone import Zone

def index(request):
    return render(request, 'backoffice/index.html')

def restaurants_list(request):
    secteur = request.GET.get('secteur')
    horaire = request.GET.get('horaire')
    restaurants = Restaurant.list(secteur, horaire)
    secteurs = db.fetch_query("SELECT nom FROM zones")
    return render(request, 'backoffice/restaurants/restaurants_list.html', {
        'restaurants': restaurants,
        'secteurs': secteurs,
        'selected_secteur': secteur,
        'selected_horaire': horaire,
    })

def restaurant_detail(request, restaurant_id):
    restaurant = Restaurant.detail(restaurant_id)
    return render(request, 'backoffice/restaurants/restaurant_detail.html', {'restaurant': restaurant})

def restaurant_add(request):
    if request.method == 'POST':
        data = {
            'nom': request.POST.get('nom'),
            'secteur': request.POST.get('secteur'),
            'commission': request.POST.get('commission'),
            'horaire_debut': request.POST.get('horaire_debut'),
            'horaire_fin': request.POST.get('horaire_fin'),
            'statut': request.POST.get('statut'),
            'image': request.POST.get('image'),
        }
        Restaurant.add(data)
        return redirect('restaurants_list')
    secteurs = db.fetch_query("SELECT nom FROM zones")
    statuts = db.fetch_query("SELECT appellation FROM statut_restaurant")
    return render(request, 'backoffice/restaurants/restaurant_form.html', {
        'secteurs': secteurs,
        'statuts': statuts,
        'action': 'Ajouter'
    })

def restaurant_edit(request, restaurant_id):
    restaurant = Restaurant.detail(restaurant_id)
    secteurs = db.fetch_query("SELECT nom FROM zones")
    statuts = db.fetch_query("SELECT appellation FROM statut_restaurant")
    if request.method == 'POST':
        data = {
            'nom': request.POST.get('nom'),
            'secteur': request.POST.get('secteur'),
            'commission': request.POST.get('commission'),
            'horaire_debut': request.POST.get('horaire_debut'),
            'horaire_fin': request.POST.get('horaire_fin'),
            'statut': request.POST.get('statut'),
            'image': request.POST.get('image'),
        }
        Restaurant.edit(restaurant_id, data)
        return redirect('restaurants_list')
    return render(request, 'backoffice/restaurants/restaurant_form.html', {
        'restaurant': restaurant,
        'secteurs': secteurs,
        'statuts': statuts,
        'action': 'Modifier'
    })

def restaurant_delete(request, restaurant_id):
    if not Restaurant.can_delete(restaurant_id):
        return render(request, 'backoffice/restaurants/restaurant_delete_error.html', {
            'reason': "Impossible de supprimer ce restaurant : il existe des commandes en cours."
        })
    if Restaurant.is_closed(restaurant_id):
        return redirect('restaurants_list')
    if request.method == 'POST':
        success = Restaurant.close(restaurant_id)
        if success:
            from django.contrib import messages
            messages.success(request, "Le restaurant a été fermé avec succès.")
        return redirect('restaurants_list')
    return render(request, 'backoffice/restaurants/restaurant_delete_confirm.html', {
        'restaurant_id': restaurant_id
    })

def restaurant_orders(request, restaurant_id):
    commandes = Restaurant.orders(restaurant_id)
    return render(request, 'backoffice/restaurants/restaurant_orders.html', {
        'commandes': commandes
    })

def restaurant_financial(request, restaurant_id):
    periode = request.GET.get('periode', 'today')
    date_from = None
    date_to = None
    now = datetime.now()

    if periode == 'today':
        date_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
        date_to = now
    elif periode == 'month':
        date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        date_to = now
    elif periode == 'year':
        date_from = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        date_to = now
    elif periode == 'custom':
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        if date_from:
            date_from = datetime.strptime(date_from, "%Y-%m-%d")
        if date_to:
            date_to = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
        else:
            date_to = now
    else:
        date_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
        date_to = now

    result = Restaurant.financial(restaurant_id, date_from, date_to)
    graph_labels, graph_values = Restaurant.financial_graph(restaurant_id, date_from, date_to, periode)

    periode_label = {
        'today': "Aujourd'hui",
        'month': "Ce mois",
        'year': "Cette année",
        'custom': "Période personnalisée"
    }.get(periode, "Aujourd'hui")

    return render(request, 'backoffice/restaurants/restaurant_financial.html', {
        'restaurant': result['restaurant'],
        'total_brut': result['total_brut'],
        'commission': result['commission'],
        'montant_commission': result['montant_commission'],
        'total_frais': result['total_frais'],
        'benefice_net': result['benefice_net'],
        'periode': periode,
        'periode_label': periode_label,
        'date_from': date_from.strftime("%Y-%m-%d") if isinstance(date_from, datetime) else '',
        'date_to': (date_to - timedelta(days=1)).strftime("%Y-%m-%d") if isinstance(date_to, datetime) else '',
        'graph_labels': graph_labels,
        'graph_values': graph_values,
    })

def test_create_client(request):

        # Créer le client
        result = Zone.delete(1,2)
               
                        
               
        if 'error' in result:
            messages.error(request, result['error'])
        else:
            #messages.success(request, f"Client créé avec succès : {result['email']}")
            print(result)
        return render(request, 'backoffice/index.html')
