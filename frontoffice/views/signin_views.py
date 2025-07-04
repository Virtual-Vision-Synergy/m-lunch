import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from shapely import wkt

from mlunch.core.models import Zone, ZoneClient, Client
from mlunch.core.services import ClientService


def signin_view(request):
    return render(request, 'frontoffice/signin.html')
def signin(request):
    """Page d'inscription des nouveaux clients"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            mot_de_passe = request.POST.get('mot_de_passe')
            confirm_password = request.POST.get('confirm_password')
            prenom = request.POST.get('prenom')
            nom = request.POST.get('nom')
            contact = request.POST.get('contact')

            # Validation des mots de passe
            if mot_de_passe != confirm_password:
                messages.error(request, 'Les mots de passe ne correspondent pas')
                return render(request, 'frontoffice/signin.html')

            # Créer le client via le service
            result = ClientService.create_client({
                'email': email,
                'mot_de_passe': mot_de_passe,
                'prenom': prenom,
                'nom': nom,
                'contact': contact
            })

            if 'error' in result:
                messages.error(request, result['error'])
                return render(request, 'frontoffice/signin.html')

            messages.success(request, 'Inscription réussie! Vous pouvez maintenant vous connecter.')
            return redirect('frontoffice:connexion')

        except Exception as e:
            messages.error(request, f'Erreur lors de l\'inscription: {str(e)}')

    return render(request, 'frontoffice/signin.html')

