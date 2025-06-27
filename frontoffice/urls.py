from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='frontoffice_index'),
    path('logout/', views.user_logout, name='logout'),
]