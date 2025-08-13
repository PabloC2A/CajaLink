# staffpanel/views.py

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, FormView, TemplateView
from django.views import View

from legacy_models.models import Socio, AhorroHistorial
from users.services import create_web_user_for_socio
from .forms import WebUserLinkForm

# Importaciones para el simulador de créditos
from credit_simulator.models import CreditProduct, CreditSimulation


class StaffRequiredMixin(UserPassesTestMixin):
    """
    Mixin que asegura que solo los usuarios marcados como 'staff'
    puedan acceder a la vista.
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

        # Estadísticas existentes
        last_5_transactions = AhorroHistorial.objects.select_related('cuenta')[:5]

        # Estadísticas del simulador de créditos
        today = timezone.now().date()
        simulator_stats = {
            'total_products': CreditProduct.objects.count(),
            'active_products': CreditProduct.objects.filter(is_active=True).count(),
            'total_simulations': CreditSimulation.objects.count(),
            'recent_simulations': CreditSimulation.objects.filter(
                created_at__date=today
            ).count(),
        }

        context.update({
            # Datos existentes
            'total_web_users': User.objects.count(),
            'linked_socios': Socio.objects.filter(usersociolink__isnull=False).count(),
            'last_5_transactions': last_5_transactions,

            # Nuevos datos del simulador
            'simulator_stats': simulator_stats,
        })
        return context


class UserListView(StaffRequiredMixin, ListView):
    """
    Muestra una lista de todos los usuarios web de TIPO SOCIO ya creados.
    """
    template_name = 'staffpanel/user_list.html'
    context_object_name = 'web_users'
    paginate_by = 20

    def get_queryset(self):
        """
        Optimiza la consulta usando select_related para traer el Vínculo y el Socio
        en la misma consulta, evitando múltiples accesos a la BD.
        """
        return User.objects.filter(is_staff=False).select_related('link__socio')


class LinkSocioSearchView(StaffRequiredMixin, ListView):
    """
    Muestra una lista paginada de Socios que AÚN NO tienen una cuenta web vinculada.
    Incluye una funcionalidad de búsqueda.
    """
    model = Socio
    template_name = 'staffpanel/link_socio_search.html'
    context_object_name = 'socios'
    paginate_by = 10

    def get_queryset(self):
        """
        Filtra los socios para mostrar solo aquellos sin un UserSocioLink.
        """
        queryset = Socio.objects.filter(usersociolink__isnull=True)
        query = self.request.GET.get('q', '')
        if query:
            # Búsqueda por nombres, apellidos o cédula
            queryset = queryset.filter(
                Q(nombres__icontains=query) |
                Q(apellidos__icontains=query) |
                Q(cedula__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        """
        Añade el término de búsqueda al contexto para mostrarlo en el input.
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class LinkSocioCreateUserView(StaffRequiredMixin, FormView):
    """
    Maneja el formulario para crear un usuario web y vincularlo a un Socio.
    """
    template_name = 'staffpanel/link_socio_create_user.html'
    form_class = WebUserLinkForm
    success_url = reverse_lazy('staffpanel:user_list')

    def get_initial(self):
        """
        Pre-rellena el formulario con datos del Socio para facilitar la tarea
        al empleado.
        """
        socio = get_object_or_404(Socio, id=self.kwargs.get('socio_id'))
        initial = super().get_initial()
        initial['email'] = socio.email or ''
        # Sugiere un nombre de usuario basado en el email o la cédula
        if socio.email:
            initial['username'] = socio.email.split('@')[0]
        elif socio.cedula:
            initial['username'] = socio.cedula
        return initial

    def get_context_data(self, **kwargs):
        """
        Añade el objeto Socio al contexto para mostrar su nombre en la plantilla.
        """
        context = super().get_context_data(**kwargs)
        context['socio'] = get_object_or_404(Socio, id=self.kwargs.get('socio_id'))
        return context

    def form_valid(self, form):
        """
        Si el formulario es válido, llama al servicio para crear y vincular el usuario.
        """
        socio = get_object_or_404(Socio, id=self.kwargs.get('socio_id'))
        data = form.cleaned_data

        try:
            new_user, temp_password = create_web_user_for_socio(
                socio=socio,
                username=data['username'],
                email=data.get('email') or socio.email,  # Usa el email del form o el del socio
                first_name=socio.nombres,
                last_name=socio.apellidos
            )
            messages.success(
                self.request,
                f"Usuario web '{new_user.username}' creado y vinculado a {socio.nombres} {socio.apellidos}. "
                f"Contraseña temporal: {temp_password}"
            )
        except Exception as e:
            messages.error(
                self.request,
                f"Ocurrió un error inesperado al vincular el usuario: {e}"
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
