from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('userpanel.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('staff/', include('staffpanel.urls')),
    path('users/', include('users.urls')),
]
