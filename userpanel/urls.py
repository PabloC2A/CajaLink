# userpanel/urls.py

from django.urls import path
from . import views

app_name = 'userpanel'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('account/<int:pk>/', views.AccountDetailView.as_view(), name='account_detail'),
]
