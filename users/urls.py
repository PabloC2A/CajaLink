# users/urls.py

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # URL para nuestra vista de redirección
    path('redirect/', views.redirect_after_login, name='redirect_after_login'),
]
