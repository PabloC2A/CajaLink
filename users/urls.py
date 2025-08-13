# users/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeDoneView
from .views import CustomPasswordChangeView, redirect_after_login

app_name = 'users'

urlpatterns = [
    path('redirect/', redirect_after_login, name='post_login_redirect'),
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
