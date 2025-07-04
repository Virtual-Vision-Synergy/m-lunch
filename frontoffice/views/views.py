from django.shortcuts import render, redirect

from mlunch.core.models import Client


def index(request):
    return render(request, 'frontoffice/index.html')

def accueil(request):
    return render(request, 'frontoffice/accueil.html')

def connexion_view(request):
    error_message = None

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        #print(password)
        try:
            client = Client.objects.get(email=email)
            if password == client.mot_de_passe:
                request.session['client_id'] = client.id  # simple session login
                return redirect('restaurant_list')  # change to your home URL name
            else:
                error_message = "Mot de passe incorrect."
        except Client.DoesNotExist:
            error_message = "Email introuvable."

    return render(request, 'frontoffice/connexion.html', {
        'error_message': error_message
    })