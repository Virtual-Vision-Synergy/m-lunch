from django.shortcuts import render
from django.contrib import messages
from mlunch.core.Client import Client
from mlunch.core.Commande import Commande
from mlunch.core.Livraison import Livraison
from mlunch.core.Livreur import Livreur
from mlunch.core.Repas import Repas
from mlunch.core.Restaurant import Restaurant
from mlunch.core.Zone import Zone

def test_create_client(request):

        # Créer le client
        result = Zone.delete(1,2)
               
                        
               
        if 'error' in result:
            messages.error(request, result['error'])
        else:
            #messages.success(request, f"Client créé avec succès : {result['email']}")
            print(result)
        return render(request, 'backoffice/index.html')
