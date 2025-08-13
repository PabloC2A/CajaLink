# userpanel/urls.py

from django.urls import path
from . import views

app_name = 'userpanel'

urlpatterns = [
    # Dashboard principal
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Historiales de productos
    path('savings/', views.AhorroHistorialView.as_view(), name='ahorro_historial'),
    path('credit/<int:pk>/', views.CreditoDetailView.as_view(), name='credito_detail'),
    path('creditos/historial/', views.CreditoHistorialView.as_view(), name='credito_historial'),
    path('simulador/', views.SimulatorIntegrationView.as_view(), name='simulator_integration'),
    path('certificados/', views.CertificadoHistorialView.as_view(), name='certificado_historial'),
]
