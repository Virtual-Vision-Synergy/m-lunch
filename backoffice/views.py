from django.shortcuts import render
from django.contrib import messages
from mlunch.core.Client import Client

def test_create_client(request):

        # Créer le client
        result = Client.create("axxxa@gghvmail", "hh", 888, "prenom", "nom")
        
        if 'error' in result:
            messages.error(request, result['error'])
        else:
            messages.success(request, f"Client créé avec succès : {result['email']}")

        return render(request, 'backoffice/index.html')
