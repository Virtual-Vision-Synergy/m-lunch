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
                request.session['client_id'] = client.id  
                return redirect('/')  
            else:
                error_message = "Mot de passe incorrect."
        except Client.DoesNotExist:
            error_message = "Email introuvable."

    return render(request, 'frontoffice/connexion.html', {
        'error_message': error_message
    })

def logout_view(request):
    try:
        del request.session['client_id']  # remove the client_id from the session
    except KeyError:
        pass
    return redirect('/')  # Redirect to the home page after logout