# staffpanel/views.py
from django.contrib import messages
from django.db import transaction, connection
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from .forms import SqlUploadForm

from banking.models import Transaction


@staff_member_required
def staff_dashboard_view(request):
    # Calcular estadísticas
    total_users = User.objects.count()
    active_socios = User.objects.filter(is_staff=False, is_active=True).count()
    last_5_transactions = Transaction.objects.order_by('-fecha_transferencia', '-hora_transferencia')[:5]

    context = {
        'total_users': total_users,
        'active_socios': active_socios,
        'last_5_transactions': last_5_transactions,
    }
    return render(request, 'staffpanel/dashboard.html', context)


@staff_member_required
def user_list_view(request):
    # Obtenemos todos los usuarios que NO son staff (los socios)
    socios = User.objects.filter(is_staff=False)

    context = {
        'socios': socios
    }
    return render(request, 'staffpanel/user_list.html', context)


@staff_member_required
@require_POST  # Esta vista solo acepta peticiones POST por seguridad
def deactivate_user_view(request, user_id):
    # Buscamos al usuario que se va a desactivar
    user_to_deactivate = get_object_or_404(User, pk=user_id)

    # Cambiamos su estado y guardamos
    user_to_deactivate.is_active = False
    user_to_deactivate.save()

    # Redirigimos de vuelta a la lista de usuarios
    return redirect('staffpanel:user_list')


@staff_member_required
def etl_view(request):
    if request.method == 'POST':
        form = SqlUploadForm(request.POST, request.FILES)
        if form.is_valid():
            sql_file = request.FILES['sql_file']

            # Leer el contenido del archivo
            sql_content = sql_file.read().decode('utf-8')

            try:
                # Ejecutar todo el script SQL dentro de una transacción atómica.
                # Si algo falla, todos los cambios se revierten.
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.executescript(sql_content)

                messages.success(request, 'El script SQL se ha ejecutado exitosamente.')

            except Exception as e:
                messages.error(request, f'Ocurrió un error al ejecutar el script: {e}')

            return redirect('staffpanel:etl')
    else:
        form = SqlUploadForm()

    # La plantilla no necesita cambiar, solo le pasamos el nuevo formulario
    return render(request, 'staffpanel/etl_upload.html', {'form': form})
