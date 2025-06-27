from django.shortcuts import render, redirect
from mlunch.core.Commande import Commande
from mlunch.core.Livraison import Livraison
from database import db
from django.contrib.auth import logout
from django.contrib import messages


def index(request):
    return render(request, 'frontoffice/index.html')

def user_logout(request):
    """Déconnecte l'utilisateur et redirige vers la page de connexion"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('login')  # Remplacer par votre URL de page de login