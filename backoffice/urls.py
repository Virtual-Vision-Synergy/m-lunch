from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='backoffice_index'),
    path('restaurants/', views.restaurants_list, name='restaurants_list'),
    path('restaurants/add/', views.restaurant_add, name='restaurant_add'),
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurants/<int:restaurant_id>/edit/', views.restaurant_edit, name='restaurant_edit'),
    path('restaurants/<int:restaurant_id>/delete/', views.restaurant_delete, name='restaurant_delete'),
    path('restaurants/<int:restaurant_id>/orders/', views.restaurant_orders, name='restaurant_orders'),
    path('restaurants/<int:restaurant_id>/financial/', views.restaurant_financial, name='restaurant_financial'),
]