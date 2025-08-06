# config/urls.py

from django.contrib import admin
from django.urls import path, include

from users.views import CustomPasswordChangeView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rutas de las aplicaciones
    path('dashboard/', include('userpanel.urls')),
    path('staff/', include('staffpanel.urls')),
    path('etl/', include('etl.urls')),

    # Rutas de autenticación y de la app 'users'
    path('accounts/', include('users.urls')),
]
