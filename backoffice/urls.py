from django.urls import path
from . import views

urlpatterns = [
    path('', views.test_create_client, name='/aa'),
]