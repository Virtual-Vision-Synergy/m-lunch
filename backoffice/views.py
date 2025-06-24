from django.shortcuts import render
from django.contrib import messages
from mlunch.core.Client import Client
from mlunch.core.Commande import Commande
from mlunch.core.Livraison import Livraison

def test_create_client(request):

        # Créer le client
        result = Livraison.create(1,1,1)
        
        if 'error' in result:
            messages.error(request, result['error'])
        #else:
            #messages.success(request, f"Client créé avec succès : {result['email']}")

        return render(request, 'backoffice/index.html')
