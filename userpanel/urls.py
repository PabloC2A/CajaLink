# userpanel/urls.py

from django.urls import path
from . import views

# Este es el nombre del conjunto de URLs de esta app.
# Nos permitirá referirnos a ellas fácilmente en las plantillas.
app_name = 'userpanel'

urlpatterns = [
    # Cuando alguien visite la URL raíz de este panel (ej. /dashboard/),
    # se ejecutará la vista 'dashboard_view'.
    path('', views.dashboard_view, name='dashboard'),
    path('account/<int:account_id>/', views.account_detail_view, name='account_detail'),
]
