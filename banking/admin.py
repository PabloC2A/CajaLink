# banking/admin.py

from django.contrib import admin
from .models import Account, Transaction


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """
    Configuración mejorada del panel de administración para el modelo Account.
    """
    # Campos a mostrar en la lista de cuentas
    list_display = ('account_number', 'socio', 'cash_balance', 'get_socio_full_name')

    # Añade filtros útiles
    list_filter = ('socio__is_staff',)

    # Permite buscar por estos campos
    search_fields = ('account_number', 'socio__username', 'socio__first_name', 'socio__last_name')

    # Para mejorar el rendimiento en la carga de datos relacionados
    raw_id_fields = ('socio',)

    @admin.display(description='Nombre del Socio')
    def get_socio_full_name(self, obj):
        return obj.socio.get_full_name()


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Transaction.
    """
    list_display = ('transaction_date', 'description', 'account', 'amount', 'flow')
    list_filter = ('flow', 'transaction_type', 'transaction_date')
    search_fields = ('description', 'account__account_number', 'account__socio__username')
    date_hierarchy = 'transaction_date'
