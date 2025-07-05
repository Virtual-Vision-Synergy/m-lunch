from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('staff/', include('backoffice.urls')),
    path('', include('frontoffice.urls')),
    path('resto/', include('restaurant.urls')),

]
