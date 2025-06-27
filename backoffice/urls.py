from django.urls import path
from . import views

urlpatterns = [
    path('', views.test_get_repas_from_id, name='/aa'),
   
    
]