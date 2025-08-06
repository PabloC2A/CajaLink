# staffpanel/urls.py

from django.urls import path
from . import views

app_name = 'staffpanel'

urlpatterns = [
    path('', views.StaffDashboardView.as_view(), name='dashboard'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.SocioCreateView.as_view(), name='create_socio'),
    path('users/<int:user_id>/deactivate/', views.DeactivateUserView.as_view(), name='deactivate_user'),
    path('etl/', views.ETLUploadView.as_view(), name='etl'),
]
