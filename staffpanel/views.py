# staffpanel/views.py

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.db import connection, transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, TemplateView
from django.views import View

from banking.models import Transaction
from users.services import create_socio_user
from .forms import SocioCreationForm, SqlUploadForm


class StaffRequiredMixin(UserPassesTestMixin):
    """
    Mixin que verifica que el usuario sea parte del personal (staff).
    """

    def test_func(self):
        return self.request.user.is_staff


class StaffDashboardView(StaffRequiredMixin, TemplateView):
    """
    Muestra el dashboard principal del personal con estadísticas clave.
    """
    template_name = 'staffpanel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = User.objects.count()
        context['active_socios'] = User.objects.filter(is_staff=False, is_active=True).count()
        context['last_5_transactions'] = Transaction.objects.all()[:5]
        return context


class UserListView(StaffRequiredMixin, ListView):
    """
    Muestra una lista de todos los socios (usuarios no-staff).
    """
    model = User
    template_name = 'staffpanel/user_list.html'
    context_object_name = 'socios'
    paginate_by = 15  # Opcional: añade paginación para listas largas

    def get_queryset(self):
        """
        Optimiza la consulta usando select_related para traer el perfil
        en la misma consulta y evitar accesos extra a la BD en la plantilla.
        """
        return User.objects.filter(is_staff=False).select_related('profile')


class SocioCreateView(StaffRequiredMixin, FormView):
    """
    Maneja la creación de nuevos socios a través de un formulario.
    """
    template_name = 'staffpanel/create_socio.html'
    form_class = SocioCreationForm
    success_url = reverse_lazy('staffpanel:user_list')

    def form_valid(self, form):
        """
        Si el formulario es válido, llama al servicio para crear el usuario.
        """
        try:
            new_user, temp_password = create_socio_user(**form.cleaned_data)
            messages.success(
                self.request,
                f"Socio '{new_user.username}' creado. Contraseña temporal: {temp_password}"
            )
        except Exception as e:
            messages.error(
                self.request,
                f"Ocurrió un error inesperado al crear el socio: {e}"
            )
        return super().form_valid(form)


class DeactivateUserView(StaffRequiredMixin, View):
    """
    Desactiva una cuenta de socio. Solo responde a peticiones POST.
    """

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        user_to_deactivate = get_object_or_404(User, pk=user_id, is_staff=False)
        user_to_deactivate.is_active = False
        user_to_deactivate.save()
        messages.warning(request, f"El usuario '{user_to_deactivate.username}' ha sido desactivado.")
        return redirect('staffpanel:user_list')


class ETLUploadView(StaffRequiredMixin, FormView):
    """
    Maneja la subida y ejecución de un archivo SQL para el ETL.
    """
    template_name = 'staffpanel/etl_upload.html'
    form_class = SqlUploadForm
    success_url = reverse_lazy('staffpanel:etl')

    def form_valid(self, form):
        sql_file = self.request.FILES['sql_file']
        sql_content = sql_file.read().decode('utf-8')
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.executescript(sql_content)
            messages.success(self.request, 'El script SQL se ha ejecutado exitosamente.')
        except Exception as e:
            messages.error(self.request, f'Ocurrió un error al ejecutar el script: {e}')
        return super().form_valid(form)
