from django.shortcuts import render, redirect
from pyexpat.errors import messages

from mlunch.core.models import HistoriqueStatutCommande, Commande, Admin
from mlunch.core.services.commande_service import CommandeService
from mlunch.core.models import HistoriqueStatutCommande, Commande, StatutCommande

def index(request):
    """Rediriger vers la page de connexion admin"""
    return redirect('admin_login')

from django.shortcuts import render, redirect
from django.contrib import messages  # <-- IMPORT IMPORTANT
from mlunch.core.models import Admin

def connexion_admin(request):
    """Vue pour la connexion de l’admin sans hashage du mot de passe"""

    # Vérifier si l’admin est déjà connecté (session existante)
    if request.session.get('admin_id'):
        return redirect('accueil')

    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        mot_de_passe = request.POST.get('mot_de_passe', '').strip()

        try:
            admin = Admin.objects.get(nom=nom)
            # Comparaison directe des mots de passe en clair
            if mot_de_passe == admin.mot_de_passe:
                request.session['admin_id'] = admin.id
                return redirect('accueil')
            else:
                messages.error(request, "Mot de passe incorrect.")
        except Admin.DoesNotExist:
            messages.error(request, "Nom d'utilisateur inconnu.")

    # GET ou erreurs → afficher formulaire
    return render(request, 'backoffice/connexion_admin.html')


def accueil(request):
    """Page d'accueil du backoffice avec filtre par statut"""

    # Récupérer le statut sélectionné depuis la requête GET
    statut_filtre = request.GET.get('statut', '').strip()

    # Récupérer toutes les commandes
    commandes = Commande.objects.all().select_related('client', 'point_recup', 'mode_paiement')

    commandes_data = []
    for commande in commandes:
        # Récupérer le dernier statut connu pour chaque commande
        dernier_statut = HistoriqueStatutCommande.objects.filter(
            commande=commande
        ).order_by('-mis_a_jour_le').first()

        statut = dernier_statut.statut.appellation if dernier_statut else "Inconnu"

        # ➤ Appliquer le filtre si un statut est sélectionné
        if not statut_filtre or statut == statut_filtre:
            commandes_data.append({
                'id': commande.id,
                'client': str(commande.client),
                'cree_le': commande.cree_le,
                'point_recup': str(commande.point_recup),
                'mode_paiement': str(commande.mode_paiement) if commande.mode_paiement else "N/A",
                'statut': statut,
            })

    # Récupérer tous les statuts disponibles pour remplir le filtre
    statuts = StatutCommande.objects.all().order_by('appellation')

    # Renvoyer le template avec les données
    return render(request, 'backoffice/accueil.html', {
        'commandes': commandes_data,
        'statuts': statuts,
    })
