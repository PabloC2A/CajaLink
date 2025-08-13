# credit_simulator/urls.py

from django.urls import path
from . import views

app_name = 'credit_simulator'

urlpatterns = [
    # =============================================================================
    # URLs PARA USUARIOS NORMALES - SIMULACIONES
    # =============================================================================

    # Página principal de simulación
    path('',
         views.CreditSimulationView.as_view(),
         name='simulation_form'),

    # Resultado de la simulación
    path('resultado/',
         views.CreditSimulationResultView.as_view(),
         name='simulation_result'),

    # Resultado específico por ID
    path('resultado/<int:pk>/',
         views.CreditSimulationResultView.as_view(),
         name='simulation_result_detail'),

    # Tabla de amortización
    path('amortizacion/<int:pk>/',
         views.AmortizationScheduleView.as_view(),
         name='amortization_schedule'),

    # Historial de simulaciones del usuario
    path('historial/',
         views.UserSimulationHistoryView.as_view(),
         name='user_history'),

    # Eliminar simulación
    path('eliminar/<int:pk>/',
         views.SimulationDeleteView.as_view(),
         name='delete_simulation'),

    # Comparación de productos
    path('comparar/',
         views.ProductComparisonView.as_view(),
         name='product_comparison'),

    # Exportar simulación
    path('exportar/<int:pk>/',
         views.ExportSimulationView.as_view(),
         name='export_simulation'),

    # =============================================================================
    # URLs PARA STAFF - ADMINISTRACIÓN
    # =============================================================================

    # Dashboard principal para staff
    path('admin/',
         views.StaffDashboardView.as_view(),
         name='staff_dashboard'),

    # Gestión de productos de crédito
    path('admin/productos/',
         views.CreditProductListView.as_view(),
         name='staff_product_list'),

    path('admin/productos/crear/',
         views.CreditProductCreateView.as_view(),
         name='staff_product_create'),

    path('admin/productos/<int:pk>/',
         views.CreditProductDetailView.as_view(),
         name='staff_product_detail'),

    path('admin/productos/<int:pk>/editar/',
         views.CreditProductUpdateView.as_view(),
         name='staff_product_update'),

    path('admin/productos/<int:pk>/toggle-status/',
         views.CreditProductToggleStatusView.as_view(),
         name='staff_product_toggle_status'),

    # Reportes para staff
    path('admin/reportes/',
         views.SimulationReportsView.as_view(),
         name='staff_reports'),

    # =============================================================================
    # APIs AJAX Y JSON
    # =============================================================================

    # API para obtener límites de un producto
    path('api/producto/<int:pk>/limites/',
         views.ProductLimitsAPIView.as_view(),
         name='api_product_limits'),

    # API para simulación rápida
    path('api/simulacion-rapida/',
         views.QuickSimulationAPIView.as_view(),
         name='api_quick_simulation'),

    # API para generar tabla de amortización
    path('api/amortizacion/<int:pk>/',
         views.GenerateAmortizationAPIView.as_view(),
         name='api_generate_amortization'),
]
