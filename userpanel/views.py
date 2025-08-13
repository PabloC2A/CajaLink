# userpanel/views.py
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.utils import timezone
from legacy_models.models import Socio, AhorroHistorial, Credito, CreditoCuota, CertificadoHistorial
from credit_simulator.models import CreditProduct, CreditSimulation


class SocioDataMixin(LoginRequiredMixin):
    """
    Mixin reutilizable que obtiene el registro 'Socio' vinculado al
    usuario web autenticado. Lanza un error 404 si un usuario sin un
    vínculo de socio intenta acceder a una vista que lo requiere.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Este metodo se ejecuta antes que cualquier otro en la vista.
        Asegura que el 'socio' esté disponible en 'self.socio'.
        """
        self.socio = get_object_or_404(Socio, usersociolink__user=request.user)
        return super().dispatch(request, *args, **kwargs)


class DashboardView(SocioDataMixin, TemplateView):
    template_name = 'userpanel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        socio_cuenta = self.socio.cuenta

        # Definir criterio consistente para cuotas pendientes
        # Una cuota está pendiente si pagado es False o None (NULL)
        cuotas_pendientes_filter = Q(pagado=False) | Q(pagado__isnull=True)

        # Query optimizado para cuotas pendientes ordenadas por fecha_ven
        cuotas_pendientes_qs = CreditoCuota.objects.filter(
            cuotas_pendientes_filter
        ).select_related('num_paga').order_by('fecha_ven')

        # Obtener créditos activos con prefetch optimizado
        active_credits = Credito.objects.filter(
            cuenta=socio_cuenta
        ).filter(
            Q(pagado=False) | Q(pagado__isnull=True)
        ).prefetch_related(
            Prefetch(
                'cuotas_credito',
                queryset=cuotas_pendientes_qs,
                to_attr='cuotas_pendientes_list'
            )
        ).only('num_paga', 'sal_pre', 'id')

        credits_with_details = []
        now = timezone.localdate()

        for credit in active_credits:
            # Obtener las cuotas pendientes ya filtradas y ordenadas
            cuotas_pendientes = getattr(credit, 'cuotas_pendientes_list', [])

            # Inicializar variables
            cuota_vencida = None
            cuota_proxima = None

            if cuotas_pendientes:
                # Buscar la primera cuota vencida (ordenadas por fecha_ven)
                for cuota in cuotas_pendientes:
                    if cuota.fecha_ven and cuota.fecha_ven < now:
                        cuota_vencida = cuota
                        break

                # Si no hay cuota vencida, la primera es la próxima
                if not cuota_vencida and cuotas_pendientes:
                    cuota_proxima = cuotas_pendientes[0]

            credits_with_details.append({
                'credit': credit,
                'overdue_installment': cuota_vencida,
                'next_installment': cuota_proxima,
            })

        # ===================================================================
        # INTEGRACIÓN DEL SIMULADOR DE CRÉDITOS
        # ===================================================================

        # Obtener productos de crédito disponibles
        available_products = CreditProduct.objects.active().order_by('commercial_name')

        # Obtener estadísticas del usuario en el simulador
        user_simulations_count = CreditSimulation.objects.filter(user=self.request.user).count()

        # Obtener la última simulación del usuario (si existe)
        last_simulation = CreditSimulation.objects.filter(
            user=self.request.user
        ).select_related('credit_product').order_by('-created_at').first()

        context.update({
            'socio': self.socio,
            'credits_with_details': credits_with_details,
            'full_name': self.request.user.get_full_name() or self.request.user.username,

            # Datos del simulador de créditos
            'available_products_count': available_products.count(),
            'recent_products': available_products[:3],  # Primeros 3 productos para mostrar
            'user_simulations_count': user_simulations_count,
            'last_simulation': last_simulation,
        })

        return context


class AhorroHistorialView(SocioDataMixin, ListView):
    """
    Muestra el historial de transacciones de la cuenta de ahorros del socio.
    """
    model = AhorroHistorial
    template_name = 'userpanel/ahorro_historial.html'
    context_object_name = 'transactions'
    paginate_by = 25

    def get_queryset(self):
        """
        Filtra las transacciones para mostrar únicamente las que pertenecen
        a la cuenta del socio logueado.
        """
        return self.socio.ahorros_historial.all().order_by('-fecha_tra', '-id')

    def get_context_data(self, **kwargs):
        """
        Añade el objeto socio al contexto para poder mostrar sus saldos en la plantilla.
        """
        context = super().get_context_data(**kwargs)
        context['socio'] = self.socio
        return context


class CertificadoHistorialView(SocioDataMixin, ListView):
    """
    Muestra el historial de transacciones de los certificados de aportación del socio.
    """
    model = CertificadoHistorial
    template_name = 'userpanel/certificado_historial.html'
    context_object_name = 'transactions'
    paginate_by = 25

    def get_queryset(self):
        """
        Filtra las transacciones para mostrar únicamente las que pertenecen
        a la cuenta del socio logueado.
        """
        return self.socio.certificados_historial.all().order_by('-fecha_tra', '-id')

    def get_context_data(self, **kwargs):
        """
        Añade el objeto socio al contexto para poder mostrar sus saldos en la plantilla.
        """
        context = super().get_context_data(**kwargs)
        context['socio'] = self.socio
        return context


class CreditoDetailView(SocioDataMixin, DetailView):
    model = Credito
    template_name = 'userpanel/credito_detail.html'
    context_object_name = 'credit'

    def get_queryset(self):
        return self.socio.creditos.prefetch_related(
            Prefetch(
                'cuotas_credito',
                queryset=CreditoCuota.objects.order_by('fecha_ven'),
                to_attr='all_cuotas'
            )
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.cuenta.cuenta != self.socio.cuenta:
            raise Http404("No tienes permiso para ver este crédito.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cuotas = getattr(self.object, 'all_cuotas', [])

        # Usar el mismo criterio que en el dashboard
        cuotas_pagadas = []
        cuotas_pendientes = []

        for cuota in cuotas:
            # Una cuota está pagada si pagado es explícitamente True
            if cuota.pagado is True:
                cuotas_pagadas.append(cuota)
            else:
                # Si es False, None o cualquier otro valor falsy, está pendiente
                cuotas_pendientes.append(cuota)

        # Ordenar cuotas pendientes por fecha de vencimiento
        cuotas_pendientes.sort(key=lambda c: c.fecha_ven or timezone.date.max)
        siguiente_cuota = cuotas_pendientes[0] if cuotas_pendientes else None

        # ===================================================================
        # INTEGRACIÓN DEL SIMULADOR DE CRÉDITOS EN DETALLE DE CRÉDITO
        # ===================================================================

        # Obtener productos activos para mostrar opción de nueva simulación
        available_products = CreditProduct.objects.active().order_by('commercial_name')

        # Verificar si el usuario tiene simulaciones relacionadas con montos similares
        current_credit_amount = self.object.val_prest or 0
        related_simulations = CreditSimulation.objects.filter(
            user=self.request.user,
            requested_amount__range=[
                current_credit_amount * Decimal('0.8'),  # 80% del monto actual
                current_credit_amount * Decimal('1.2')  # 120% del monto actual
            ]
        ).select_related('credit_product').order_by('-created_at')[:3]

        context.update({
            'installments_paid': cuotas_pagadas,
            'installments_pending': cuotas_pendientes,
            'next_installment': siguiente_cuota,

            # Datos del simulador para el detalle de crédito
            'available_products_count': available_products.count(),
            'related_simulations': related_simulations,
            'current_credit_amount': current_credit_amount,
        })
        return context


# ===================================================================
# NUEVAS VISTAS PARA INTEGRACIÓN CON SIMULADOR DE CRÉDITOS
# ===================================================================

class CreditoHistorialView(SocioDataMixin, ListView):
    """
    Muestra el historial completo de créditos del socio, incluyendo
    opción de acceder al simulador para nuevos créditos.
    """
    model = Credito
    template_name = 'userpanel/credito_historial.html'
    context_object_name = 'credits'
    paginate_by = 20

    def get_queryset(self):
        """
        Obtiene todos los créditos del socio, activos e inactivos.
        """
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

            # Datos del simulador
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

        # Información del socio
        socio = self.socio

        # Productos de crédito disponibles
        available_products = CreditProduct.objects.active().order_by('commercial_name')

        # Historial de simulaciones del usuario
        user_simulations = CreditSimulation.objects.filter(
            user=self.request.user
        ).select_related('credit_product').order_by('-created_at')

        # Créditos actuales para contexto
        current_credits = socio.creditos.filter(
            Q(pagado=False) | Q(pagado__isnull=True)
        )

        # Calcular monto máximo recomendado basado en historial
        max_recommended_amount = 0
        if current_credits.exists():
            # Si tiene créditos activos, sugerir hasta el 150% del mayor crédito actual
            max_credit = current_credits.order_by('-val_prest').first()
            if max_credit and max_credit.val_prest:
                max_recommended_amount = max_credit.val_prest * Decimal('1.5')
        else:
            # Si no tiene créditos, sugerir un monto inicial conservador
            max_recommended_amount = 1000000  # $1,000,000 COP como ejemplo

        context.update({
            'socio': socio,
            'available_products': available_products,
            'user_simulations': user_simulations[:10],  # Últimas 10 simulaciones
            'user_simulations_count': user_simulations.count(),
            'current_credits': current_credits,
            'max_recommended_amount': max_recommended_amount,
        })

        return context
