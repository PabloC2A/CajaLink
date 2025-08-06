# users/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeDoneView
from .views import CustomPasswordChangeView, redirect_after_login

# El app_name es crucial para que Django sepa que estas URLs pertenecen a 'users'
app_name = 'users'

urlpatterns = [
    # Vista de redirección post-login
    path('redirect/', redirect_after_login, name='redirect_after_login'),

    # Vistas de autenticación
    path(
        'login/',
        LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    path(
        'logout/',
        LogoutView.as_view(),
        name='logout'
    ),
    path(
        'password_change/',
        CustomPasswordChangeView.as_view(template_name='registration/password_change_form.html'),
        name='password_change'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
        name='password_change_done'
    ),
]
