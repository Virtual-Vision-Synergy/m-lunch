from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='backoffice_index'),
    path('restaurant/', views.restaurant, name='backoffice_restaurant'),
]
