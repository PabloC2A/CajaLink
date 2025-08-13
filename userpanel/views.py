# userpanel/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.utils import timezone
from legacy_models.models import Socio, AhorroHistorial, Credito, CreditoCuota, CertificadoHistorial


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

        context.update({
            'socio': self.socio,
            'credits_with_details': credits_with_details,
            'full_name': self.request.user.get_full_name() or self.request.user.username,
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

        context.update({
            'installments_paid': cuotas_pagadas,
            'installments_pending': cuotas_pendientes,
            'next_installment': siguiente_cuota,
        })
        return context
