# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomePageView
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='homepage'),
    path('dashboard/', include('userpanel.urls')),
    path('simulador/', include('credit_simulator.urls')),
    path('staff/', include('staffpanel.urls')),
    path('accounts/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
