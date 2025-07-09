from django.contrib import messages
from django.shortcuts import render, redirect

from mlunch.core.services import ClientService

def signin_view(request):
    return render(request, 'frontoffice/signin.html')

def signin(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            mot_de_passe = request.POST.get('mot_de_passe')
            confirm_password = request.POST.get('confirm_password')
            prenom = request.POST.get('prenom')
            nom = request.POST.get('nom')
            contact = request.POST.get('telephone')  # Changé de 'contact' à 'telephone'
            zone_id = request.POST.get('secteur')  # Nouveau paramètre

            print(zone_id)

            if mot_de_passe != confirm_password:
                messages.error(request, 'Les mots de passe ne correspondent pas')
                return render(request, 'frontoffice/signin.html')

            result = ClientService.create_client(
                email=email,
                mot_de_passe=mot_de_passe,
                prenom=prenom,
                nom=nom,
                contact=contact,
                zone_id=zone_id  # Ajout du paramètre zone_id
            )

            if 'error' in result:
                print(f"ERREUR SERVICE: {result['error']}")
                messages.error(request, result['error'])
                return render(request, 'frontoffice/signin.html')

            messages.success(request, 'Inscription réussie! Vous pouvez maintenant vous connecter.')
            return redirect('/')

        except Exception as e:
            print(f"EXCEPTION CAPTURÉE: {type(e).__name__}: {str(e)}")
            print(f"TRACEBACK COMPLET:")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Erreur lors de l\'inscription: {str(e)}')

    return render(request, 'frontoffice/signin.html')