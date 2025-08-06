# staffpanel/urls.py

from django.urls import path
from . import views

app_name = 'staffpanel'

urlpatterns = [
    path('', views.staff_dashboard_view, name='dashboard'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/<int:user_id>/deactivate/', views.deactivate_user_view, name='deactivate_user'),
    path('etl/', views.etl_view, name='etl'),
]
