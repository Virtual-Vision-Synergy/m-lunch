from django.urls import path
from . import views
from . import stats_views
from . import views, stats_views, liste_zone_views
urlpatterns = [
    path('', views.index, name='/aa'),
    path('api/stats/', stats_views.get_stats, name='get_stats'),
    path('api/restaurants/', stats_views.get_restaurants, name='get_restaurants'),
    path('api/zones/', stats_views.get_zones, name='get_zones'),
    path('stats/',stats_views.testchart, name='stats_dashboard'),
    path('api/zones/<int:zone_id>/', liste_zone_views.get_zone_detail, name='get_zone_detail'),
    path('api/zones/create/', liste_zone_views.create_zone, name='create_zone'),
    path('api/zones/<int:zone_id>/update/', liste_zone_views.update_zone, name='update_zone'),
    path('api/zones/<int:zone_id>/delete/', liste_zone_views.delete_zone, name='delete_zone'),
    path('api/entites/', liste_zone_views.get_entites, name='get_entites'),
    path('zones/', liste_zone_views.zones_management, name='zone_management'),
]
