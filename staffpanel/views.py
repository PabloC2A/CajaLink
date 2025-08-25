# staffpanel/views.py

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, FormView, TemplateView

from credit_simulator.models import CreditProduct, CreditSimulation
from legacy_models.models import Socio, AhorroHistorial
from users.services import create_web_user_for_socio
from users.mixins import StaffRequiredMixin, logger
from .forms import WebUserLinkForm
from .selectors import get_unified_socio_list


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
    Vista unificada que muestra tanto usuarios como socios disponibles para vincular en una sola lista.
    """
    template_name = 'staffpanel/user_list.html'
    context_object_name = 'unified_list'
    paginate_by = 20

    def get_queryset(self):
        """
        Delega la construcción del queryset al selector.
        """
        search_query = self.request.GET.get('q', '').strip()
        return get_unified_socio_list(search_query)

    def get_context_data(self, **kwargs):
        """
        Añade información adicional al contexto manteniendo alta cohesión.
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
        Pre-rellena el formulario con datos del Socio.
        Aplica principio DRY reutilizando lógica de sugerencias.
        """
        socio = self._get_socio()
        initial = super().get_initial()
        initial['email'] = socio.email or ''

        # Factory pattern para generar username sugerido
        initial['username'] = self._generate_suggested_username(socio)
        return initial

    def get_context_data(self, **kwargs):
        """
        Añade el objeto Socio al contexto.
        """
        context = super().get_context_data(**kwargs)
        context['socio'] = self._get_socio()
        return context

    def form_valid(self, form):
        """
        Procesa el formulario con manejo robusto de errores.

        Mejora: Manejo específico de diferentes tipos de errores.
        """
        socio = get_object_or_404(Socio, id=self.kwargs.get('socio_id'))
        data = form.cleaned_data

        try:
            new_user, temp_password = create_web_user_for_socio(
                socio=socio,
                username=data['username'],
                email=data.get('email') or socio.email,
                first_name=socio.nombres,
                last_name=socio.apellidos
            )

            messages.success(
                self.request,
                f"✅ Usuario web '{new_user.username}' creado exitosamente para "
                f"{socio.nombres} {socio.apellidos}. Contraseña temporal: {temp_password}"
            )

        except ValidationError as e:
            # Error de validación específico
            messages.error(self.request, f"Error de validación: {e}")
            logger.warning(f"Validation error creating user for socio {socio.id}: {e}")
            return self.form_invalid(form)

        except IntegrityError as e:
            # Error de integridad de BD (username duplicado, etc.)
            messages.error(self.request, "El nombre de usuario ya existe en el sistema.")
            logger.warning(f"Integrity error creating user for socio {socio.id}: {e}")
            return self.form_invalid(form)

        except Exception as e:
            # Error inesperado
            messages.error(self.request, "Error del sistema. Contacte al administrador.")
            logger.error(f"Unexpected error creating user for socio {socio.id}: {e}", exc_info=True)
            return self.form_invalid(form)

        return super().form_valid(form)

    def _get_socio(self):
        """
        Metodo helper que encapsula la obtención del Socio.
        """
        return get_object_or_404(Socio, id=self.kwargs.get('socio_id'))

    def _generate_suggested_username(self, socio):
        """
        Genera un username sugerido basado en los datos del socio.
        """
        if socio.email:
            return socio.email.split('@')[0]
        elif socio.cedula:
            return socio.cedula
        return f"socio_{socio.id}"


class DeactivateUserView(StaffRequiredMixin, View):
    """
    Desactiva una cuenta de socio y redirige con mensaje.
    """

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        user_to_deactivate = get_object_or_404(User, pk=user_id, is_staff=False)

        user_to_deactivate.is_active = False
        user_to_deactivate.save()

        messages.warning(
            request,
            f"El usuario '{user_to_deactivate.username}' ha sido desactivado."
        )
        return redirect('staffpanel:user_list')
