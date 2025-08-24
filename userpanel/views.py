# userpanel/views.py
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.utils import timezone

from legacy_models.models import Socio, AhorroHistorial, Credito, CreditoCuota, CertificadoHistorial, CreditoHistorial
from credit_simulator.models import CreditProduct, CreditSimulation


class SocioDataMixin(LoginRequiredMixin):
    """
    Mixin reutilizable que obtiene el registro 'Socio' vinculado al
    usuario web autenticado.
    """

    def dispatch(self, request, *args, **kwargs):
        self.socio = get_object_or_404(Socio, usersociolink__user=request.user)
        return super().dispatch(request, *args, **kwargs)


class DashboardView(SocioDataMixin, TemplateView):
    """
    Vista principal del dashboard rediseñado según la imagen.
    """
    template_name = 'userpanel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Datos de Ahorros - mostrar número de cuenta
        ahorros_data = {
            'numero_cuenta': self.socio.cuenta,
            'saldo_disponible': self.socio.efectivo or Decimal('0.00'),
        }

        # Datos de Certificados - mostrar cantidad activa
        certificados_data = {
            'cantidad_activa': self.socio.certifica or Decimal('0.00'),
        }

        # Datos de Créditos - mostrar cuota a pagar y fecha de vencimiento
        creditos_data = self._get_creditos_data()

        # Datos de Plazos Fijos - calcular inversión total
        plazos_data = self._get_plazos_data()

        context.update({
            'socio': self.socio,
            'full_name': self.request.user.get_full_name() or self.request.user.username,
            'ahorros_data': ahorros_data,
            'certificados_data': certificados_data,
            'creditos_data': creditos_data,
            'plazos_data': plazos_data,
        })

        return context

    def _get_creditos_data(self):
        """Obtiene información de créditos: cuota a pagar y fecha de vencimiento."""
        cuotas_pendientes_filter = Q(pagado=False) | Q(pagado__isnull=True)

        # Obtener créditos activos con cuotas pendientes
        active_credits = Credito.objects.filter(
            cuenta=self.socio.cuenta
        ).filter(
            Q(pagado=False) | Q(pagado__isnull=True)
        ).prefetch_related(
            Prefetch(
                'cuotas_credito',
                queryset=CreditoCuota.objects.filter(
                    cuotas_pendientes_filter
                ).order_by('fecha_ven'),
                to_attr='cuotas_pendientes_list'
            )
        )

        total_cuota_pagar = Decimal('0.00')
        fecha_proxima_cuota = None

        for credit in active_credits:
            cuotas_pendientes = getattr(credit, 'cuotas_pendientes_list', [])

            if cuotas_pendientes:
                # Tomar la primera cuota pendiente (más próxima)
                proxima_cuota = cuotas_pendientes[0]

                if proxima_cuota.pagar:
                    total_cuota_pagar += proxima_cuota.pagar

                # Actualizar fecha más próxima
                if not fecha_proxima_cuota or (
                        proxima_cuota.fecha_ven and proxima_cuota.fecha_ven < fecha_proxima_cuota):
                    fecha_proxima_cuota = proxima_cuota.fecha_ven

        return {
            'cuota_pagar': total_cuota_pagar,
            'fecha_vencimiento': fecha_proxima_cuota,
        }

    def _get_plazos_data(self):
        """Calcula el total de inversión en plazos fijos."""
        # Intentar obtener el valor del modelo
        plazos_total = Decimal('0.00')

        # Si el socio tiene relación con plazos fijos, calcular el total
        if hasattr(self.socio, 'plazos_fijos'):
            plazos_activos = self.socio.plazos_fijos.filter(
                Q(pagado=False) | Q(pagado__isnull=True)
            )
            total_result = plazos_activos.aggregate(total=Sum('cantidad'))
            plazos_total = total_result['total'] or Decimal('0.00')

        return {
            'inversion_total': plazos_total,
        }


# Resto de vistas existentes se mantienen igual...

class AhorroHistorialView(SocioDataMixin, ListView):
    model = AhorroHistorial
    template_name = 'userpanel/ahorro_historial.html'
    context_object_name = 'transactions'
    paginate_by = 25

    def get_queryset(self):
        return self.socio.ahorros_historial.all().order_by('-fecha_tra', '-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['socio'] = self.socio
        return context


class CertificadoHistorialView(SocioDataMixin, ListView):
    model = CertificadoHistorial
    template_name = 'userpanel/certificado_historial.html'
    context_object_name = 'transactions'
    paginate_by = 25

    def get_queryset(self):
        return self.socio.certificados_historial.all().order_by('-fecha_tra', '-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['socio'] = self.socio
        return context


class CreditoDetailView(SocioDataMixin, DetailView):
    """
    Vista de detalle de crédito que muestra información completa del crédito.

    Para créditos activos: Muestra cuotas pendientes de CreditoCuota (crecuotaf)
    Para créditos pagados: Muestra transacciones reales de CreditoHistorial (credit_h)
    """
    model = Credito
    template_name = 'userpanel/credito_detail.html'
    context_object_name = 'credit'

    def get_queryset(self):
        """
        Optimiza consultas con prefetch_related para créditos activos.
        Para créditos pagados usaremos CreditoHistorial en lugar de CreditoCuota.
        Principio: Performance - Consultas optimizadas según el tipo de crédito
        """
        return self.socio.creditos.prefetch_related(
            Prefetch(
                'cuotas_credito',
                queryset=CreditoCuota.objects.order_by('fecha_ven'),
                to_attr='all_cuotas'
            ),
            Prefetch(
                'historiales',
                queryset=CreditoHistorial.objects.order_by('fechatran'),
                to_attr='payment_history'
            )
        )

    def get_object(self, queryset=None):
        """
        Verifica permisos y obtiene el objeto crédito.
        """
        obj = super().get_object(queryset)
        if obj.cuenta.cuenta != self.socio.cuenta:
            raise Http404("No tienes permiso para ver este crédito.")
        return obj

    def get_context_data(self, **kwargs):
        """
        Metodo principal que consolida toda la información del contexto.
        Aplica lógica diferente según el estado del crédito:
        - Créditos activos: Solo cuotas pendientes
        - Créditos pagados: Todas las cuotas sin colores de alerta
        """
        context = super().get_context_data(**kwargs)

        # Determinar si el crédito está activo o pagado
        credit_is_active = self._is_credit_active()

        # Obtener cuotas según el estado del crédito
        if credit_is_active:
            cuotas_data = self._get_active_credit_installments()
        else:
            cuotas_data = self._get_paid_credit_installments()

        # Obtener información de la próxima cuota (solo para créditos activos)
        next_installment = None
        if credit_is_active and cuotas_data.get('pending'):
            next_installment = self._get_next_installment(cuotas_data['pending'])

        # Agregar datos al contexto
        context.update({
            'socio': self.socio,
            'installments_paid': cuotas_data.get('paid', []),
            'installments_pending': cuotas_data.get('pending', []),
            'next_installment': next_installment,
            'today': timezone.now().date(),
            'credit_is_active': credit_is_active,
        })

        return context

    def _is_credit_active(self):
        """
        Determina si el crédito está activo o ya fue pagado completamente.

        Returns:
            bool: True si el crédito está activo, False si ya fue pagado
        """
        # Usar el metodo del modelo que ya implementa esta lógica
        return self.object.is_active()

    def _get_active_credit_installments(self):
        """
        Obtiene solo las cuotas pendientes para créditos activos.

        Returns:
            dict: Diccionario con solo 'pending' para créditos activos
        """
        # Obtener todas las cuotas prefetched
        all_cuotas = getattr(self.object, 'all_cuotas', [])

        # Para créditos activos, solo mostrar cuotas pendientes
        pending_installments = [
            cuota for cuota in all_cuotas
            if not cuota.is_paid()
        ]

        return {
            'paid': [],  # No mostrar cuotas pagadas en créditos activos
            'pending': pending_installments
        }

    def _get_paid_credit_installments(self):
        """
        Obtiene transacciones de pago del historial para créditos ya pagados completamente.
        Usa CreditoHistorial (credit_h) en lugar de CreditoCuota (crecuotaf)
        para mostrar solo los pagos que realmente se efectuaron.

        Returns:
            dict: Diccionario con transacciones de pago como "paid"
        """
        # Obtener transacciones del historial de créditos prefetched
        payment_history = getattr(self.object, 'payment_history', [])

        # Filtrar transacciones de pago de socios (ingresos para la entidad financiera)
        # ingre_egre='I' = Ingresos (pagos del socio)
        # ingre_egre='T' = Transferencias/otros tipos de pago
        # Excluir ingre_egre='E' = Egresos (desembolsos del crédito)
        payment_transactions = [
            transaction for transaction in payment_history
            if transaction.ingre_egre in ['I', 'T']
        ]

        return {
            'paid': payment_transactions,  # Transacciones reales de pago
            'pending': []  # No hay cuotas pendientes en créditos pagados
        }

    def _get_next_installment(self, pending_installments):
        """
        Obtiene la próxima cuota a vencer de las cuotas pendientes.

        Args:
            pending_installments (list): Lista de cuotas pendientes

        Returns:
            CreditoCuota|None: Próxima cuota o None si no hay pendientes
        """
        if not pending_installments:
            return None

        # Las cuotas ya están ordenadas por fecha_ven en el queryset
        # Tomar la primera cuota pendiente (más próxima a vencer)
        return pending_installments[0]


class CreditoHistorialView(SocioDataMixin, ListView):
    model = Credito
    template_name = 'userpanel/credito_historial.html'
    context_object_name = 'credits'
    paginate_by = 20

    def get_queryset(self):
        return self.socio.creditos.all().order_by('-fech_pres', '-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas de créditos del socio
        all_credits = self.get_queryset()
        active_credits = all_credits.filter(Q(pagado=False) | Q(pagado__isnull=True))

        # Información del simulador
        available_products = CreditProduct.objects.active()
        user_simulations = CreditSimulation.objects.filter(user=self.request.user)

        context.update({
            'socio': self.socio,
            'total_credits': all_credits.count(),
            'active_credits_count': active_credits.count(),
            'paid_credits_count': all_credits.count() - active_credits.count(),
            'available_products_count': available_products.count(),
            'user_simulations_count': user_simulations.count(),
            'recent_products': available_products[:5],
        })

        return context


class SimulatorIntegrationView(SocioDataMixin, TemplateView):
    """
    Vista que muestra información específica del simulador de créditos
    contextualizada para el socio actual.
    """
    template_name = 'userpanel/simulator_integration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Productos disponibles
        available_products = CreditProduct.objects.active()

        # Simulaciones del usuario
        user_simulations = CreditSimulation.objects.filter(
            user=self.request.user
        ).select_related('credit_product').order_by('-created_at')

        context.update({
            'socio': self.socio,
            'available_products': available_products,
            'user_simulations': user_simulations[:10],
            'products_count': available_products.count(),
            'simulations_count': user_simulations.count(),
        })

        return context
