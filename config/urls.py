# config/urls.py - VERSIÓN ACTUALIZADA

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomePageView
from django.views.generic import TemplateView

urlpatterns = [
    # Ruta para el panel de administración de Django
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='homepage'),

    # ---- Rutas de las Aplicaciones Principales ----

    # Dirige todas las URLs que empiezan con 'dashboard/' a la app 'userpanel'
    path('dashboard/', include('userpanel.urls')),

    # URLs de la aplicación de simulador de créditos
    path('simulador/', include('credit_simulator.urls')),

    # Dirige todas las URLs que empiezan con 'staff/' a la app 'staffpanel'
    path('staff/', include('staffpanel.urls')),

    # Dirige todas las URLs que empiezan con 'accounts/' a la app 'users'
    # Esta única línea maneja: login, logout, cambio de contraseña y la redirección.
    path('accounts/', include('users.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('test-404/', TemplateView.as_view(template_name='404.html')),
        path('test-403/', TemplateView.as_view(template_name='403.html')),
        path('test-500/', TemplateView.as_view(template_name='500.html')),
    ]
