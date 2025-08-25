# staffpanel/urls.py

from django.urls import path
from . import views

app_name = 'staffpanel'

urlpatterns = [
    path('', views.StaffDashboardView.as_view(), name='dashboard'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('socios/<int:socio_id>/create-user/', views.LinkSocioCreateUserView.as_view(), name='link_socio_create_user'),
    path('users/<int:user_id>/deactivate/', views.DeactivateUserView.as_view(), name='deactivate_user'),
]
