# userpanel/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from banking.models import Account, Transaction


@login_required
def dashboard_view(request):
    # 2. Busca todas las cuentas que pertenecen al usuario logueado.
    # El 'related_name' que definimos como "cuentas" en el modelo nos sirve aquí.
    user_accounts = request.user.cuentas.all()

    # 3. Pasa las cuentas a la plantilla a través de un diccionario de contexto.
    context = {
        'accounts': user_accounts
    }

    return render(request, 'userpanel/dashboard.html', context)


@login_required
def account_detail_view(request, account_id):
    account = get_object_or_404(Account, pk=account_id, socio=request.user)

    # Ordenamos por fecha y luego por hora, ambos descendentes
    transactions = account.transacciones.all().order_by('-fecha_transferencia', '-hora_transferencia')

    context = {
        'account': account,
        'transactions': transactions
    }

    return render(request, 'userpanel/account_detail.html', context)
