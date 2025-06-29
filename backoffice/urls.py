from django.urls import path
from . import views
from . import stats_views
urlpatterns = [
    path('', views.index, name='/aa'),
    path('api/stats/', stats_views.get_stats, name='get_stats'),
    path('api/restaurants/', stats_views.get_restaurants, name='get_restaurants'),
    path('api/zones/', stats_views.get_zones, name='get_zones'),
    path('stats/',stats_views.testchart, name='stats_dashboard'),
]