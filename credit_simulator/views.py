# credit_simulator/views.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count, Avg, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView,
    FormView, TemplateView
)
from django.views import View
from decimal import Decimal
import json

from .models import CreditProduct, CreditSimulation, AmortizationScheduleEntry
from .forms import (
    CreditProductForm, CreditSimulationForm,
    CreditProductFilterForm, AmortizationScheduleForm
)
from .services import CreditSimulationService, CreditProductService
from users.mixins import StaffRequiredMixin


# =============================================================================
# VISTAS PARA USUARIOS STAFF - GESTIÓN DE PRODUCTOS
# =============================================================================

class CreditProductListView(StaffRequiredMixin, ListView):
    """Vista de lista de productos de crédito para staff."""

    model = CreditProduct
    template_name = 'credit_simulator/staff/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        """Aplica filtros de búsqueda si están presentes."""
        queryset = CreditProduct.objects.select_related('created_by', 'updated_by')

        # Obtener parámetros de filtro
        search = self.request.GET.get('search', '').strip()
        amortization_type = self.request.GET.get('amortization_type', '')
        is_active = self.request.GET.get('is_active', '')
        min_amount = self.request.GET.get('min_amount', '')
        max_amount = self.request.GET.get('max_amount', '')

        # Aplicar filtros
        if search:
            queryset = queryset.filter(
                Q(commercial_name__icontains=search) |
                Q(internal_code__icontains=search) |
                Q(description__icontains=search)
            )

        if amortization_type:
            queryset = queryset.filter(amortization_type=amortization_type)

        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)

        if min_amount:
            try:
                queryset = queryset.filter(minimum_amount__gte=Decimal(min_amount))
            except (ValueError, TypeError):
                pass

        if max_amount:
            try:
                queryset = queryset.filter(maximum_amount__lte=Decimal(max_amount))
            except (ValueError, TypeError):
                pass

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregar formulario de filtros
        context['filter_form'] = CreditProductFilterForm(self.request.GET)

        # Estadísticas básicas
        context['stats'] = {
            'total_products': CreditProduct.objects.count(),
            'active_products': CreditProduct.objects.filter(is_active=True).count(),
            'total_simulations': CreditSimulation.objects.count(),
        }

        return context


class CreditProductCreateView(StaffRequiredMixin, CreateView):
    """Vista para crear nuevos productos de crédito."""

    model = CreditProduct
    form_class = CreditProductForm
    template_name = 'credit_simulator/staff/product_form.html'
    success_url = reverse_lazy('credit_simulator:staff_product_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Producto "{form.instance.commercial_name}" creado exitosamente.'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Producto de Crédito'
        context['submit_text'] = 'Crear Producto'
        return context


class CreditProductUpdateView(StaffRequiredMixin, UpdateView):
    """Vista para editar productos de crédito existentes."""

    model = CreditProduct
    form_class = CreditProductForm
    template_name = 'credit_simulator/staff/product_form.html'
    success_url = reverse_lazy('credit_simulator:staff_product_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Producto "{form.instance.commercial_name}" actualizado exitosamente.'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar: {self.object.commercial_name}'
        context['submit_text'] = 'Guardar Cambios'
        return context


class CreditProductDetailView(StaffRequiredMixin, DetailView):
    """Vista detallada de un producto de crédito con estadísticas."""

    model = CreditProduct
    template_name = 'credit_simulator/staff/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas del producto
        simulations = self.object.simulations.all()

        context['product_stats'] = {
            'total_simulations': simulations.count(),
            'avg_amount': simulations.aggregate(Avg('requested_amount'))['requested_amount__avg'] or 0,
            'avg_term': simulations.aggregate(Avg('term_months'))['term_months__avg'] or 0,
            'recent_simulations': simulations.select_related('user')[:10],
        }

        return context


class CreditProductToggleStatusView(StaffRequiredMixin, View):
    """Vista para activar/desactivar productos de crédito."""

    def post(self, request, pk):
        product = get_object_or_404(CreditProduct, pk=pk)

        # Cambiar estado
        product.is_active = not product.is_active
        product.updated_by = request.user
        product.save(update_fields=['is_active', 'updated_by', 'updated_at'])

        status_text = 'activado' if product.is_active else 'desactivado'
        messages.success(
            request,
            f'Producto "{product.commercial_name}" {status_text} exitosamente.'
        )

        return redirect('credit_simulator:staff_product_list')


class StaffDashboardView(StaffRequiredMixin, TemplateView):
    """Dashboard principal para staff con estadísticas del simulador."""

    template_name = 'credit_simulator/staff/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas generales
        total_products = CreditProduct.objects.count()
        active_products = CreditProduct.objects.filter(is_active=True).count()
        total_simulations = CreditSimulation.objects.count()

        # Productos más simulados
        popular_products = (
            CreditProduct.objects
            .annotate(simulation_count=Count('simulations'))
            .filter(simulation_count__gt=0)
            .order_by('-simulation_count')[:5]
        )

        # Simulaciones recientes
        recent_simulations = (
            CreditSimulation.objects
            .select_related('credit_product', 'user')
            .order_by('-created_at')[:10]
        )

        context.update({
            'total_products': total_products,
            'active_products': active_products,
            'inactive_products': total_products - active_products,
            'total_simulations': total_simulations,
            'popular_products': popular_products,
            'recent_simulations': recent_simulations,
        })

        return context


# =============================================================================
# VISTAS PARA USUARIOS NORMALES - SIMULACIONES
# =============================================================================

class CreditSimulationView(LoginRequiredMixin, FormView):
    """Vista principal para realizar simulaciones de crédito."""

    template_name = 'credit_simulator/simulation_form.html'
    form_class = CreditSimulationForm
    success_url = reverse_lazy('credit_simulator:simulation_result')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_products'] = CreditProduct.objects.active().order_by('commercial_name')
        return context

    def form_valid(self, form):
        # Realizar la simulación
        try:
            simulation = CreditSimulationService.calculate_simulation(
                credit_product=form.cleaned_data['credit_product'],
                amount=form.cleaned_data['requested_amount'],
                term_months=form.cleaned_data['term_months'],
                user=self.request.user,
                ip_address=self.get_client_ip()
            )

            # Guardar ID de simulación en sesión
            self.request.session['last_simulation_id'] = simulation.id

            messages.success(
                self.request,
                '¡Simulación realizada exitosamente!'
            )

        except Exception as e:
            messages.error(
                self.request,
                f'Error al realizar la simulación: {str(e)}'
            )
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_client_ip(self):
        """Obtiene la IP del cliente."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class CreditSimulationResultView(LoginRequiredMixin, DetailView):
    """Vista que muestra el resultado de la simulación."""

    model = CreditSimulation
    template_name = 'credit_simulator/simulation_result.html'
    context_object_name = 'simulation'

    def get_object(self, queryset=None):
        # Obtener simulación desde sesión o parámetro
        simulation_id = (
                self.kwargs.get('pk') or
                self.request.session.get('last_simulation_id')
        )

        if not simulation_id:
            raise Http404("No se encontró la simulación.")

        simulation = get_object_or_404(
            CreditSimulation.objects.select_related('credit_product'),
            pk=simulation_id
        )

        # Verificar que el usuario tenga acceso
        if simulation.user != self.request.user:
            raise Http404("No tienes acceso a esta simulación.")

        return simulation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregar formulario para generar tabla de amortización
        context['amortization_form'] = AmortizationScheduleForm(self.object)

        return context


class AmortizationScheduleView(LoginRequiredMixin, DetailView):
    """Vista que muestra la tabla de amortización detallada."""

    model = CreditSimulation
    template_name = 'credit_simulator/amortization_schedule.html'
    context_object_name = 'simulation'

    def get_object(self, queryset=None):
        simulation = get_object_or_404(
            CreditSimulation.objects.select_related('credit_product'),
            pk=self.kwargs['pk']
        )

        # Verificar acceso
        if simulation.user != self.request.user:
            raise Http404("No tienes acceso a esta simulación.")

        return simulation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Generar tabla de amortización si no existe
        schedule_entries = self.object.amortization_entries.all()
        if not schedule_entries:
            schedule_entries = CreditSimulationService.generate_amortization_schedule(self.object)

        context['schedule_entries'] = schedule_entries

        return context


class UserSimulationHistoryView(LoginRequiredMixin, ListView):
    """Vista del historial de simulaciones del usuario."""

    model = CreditSimulation
    template_name = 'credit_simulator/user_history.html'
    context_object_name = 'simulations'
    paginate_by = 20

    def get_queryset(self):
        return (
            self.request.user.credit_simulations
            .select_related('credit_product')
            .order_by('-created_at')
        )


class SimulationDeleteView(LoginRequiredMixin, View):
    """Vista para eliminar simulaciones del usuario."""

    def post(self, request, pk):
        simulation = get_object_or_404(
            CreditSimulation,
            pk=pk,
            user=request.user
        )

        simulation.delete()
        messages.success(request, 'Simulación eliminada exitosamente.')

        return redirect('credit_simulator:user_history')


# =============================================================================
# VISTAS AJAX Y API
# =============================================================================

class ProductLimitsAPIView(View):
    """API para obtener límites de un producto específico."""

    def get(self, request, pk):
        try:
            product = get_object_or_404(CreditProduct, pk=pk, is_active=True)

            data = {
                'success': True,
                'data': {
                    'minimum_amount': float(product.minimum_amount),
                    'maximum_amount': float(product.maximum_amount),
                    'minimum_term_months': product.minimum_term_months,
                    'maximum_term_months': product.maximum_term_months,
                    'annual_interest_rate': float(product.annual_interest_rate),
                    'amortization_type': product.get_amortization_type_display(),
                    'has_life_insurance': product.has_life_insurance,
                    'life_insurance_rate': float(product.life_insurance_rate) if product.has_life_insurance else 0,
                }
            }
        except Exception as e:
            data = {
                'success': False,
                'error': str(e)
            }

        return JsonResponse(data)


class QuickSimulationAPIView(View):
    """API para simulaciones rápidas sin guardar en BD."""

    def post(self, request):
        try:
            data = json.loads(request.body)

            product_id = data.get('product_id')
            amount = Decimal(str(data.get('amount', 0)))
            term_months = int(data.get('term_months', 0))

            product = get_object_or_404(CreditProduct, pk=product_id, is_active=True)

            # Validar parámetros
            CreditSimulationService.validate_simulation_parameters(
                product, amount, term_months
            )

            # Realizar cálculo
            calculator = CreditSimulationService._get_calculator(product.amortization_type)
            result = calculator.calculate(product, amount, term_months)

            response_data = {
                'success': True,
                'data': {
                    'monthly_payment': float(result['monthly_payment']),
                    'total_interest': float(result['total_interest']),
                    'total_life_insurance': float(result['total_life_insurance']),
                    'total_amount': float(result['total_amount']),
                    'product_name': product.commercial_name,
                    'amortization_type': product.get_amortization_type_display(),
                }
            }

        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }

        return JsonResponse(response_data)


class GenerateAmortizationAPIView(LoginRequiredMixin, View):
    """API para generar tabla de amortización de una simulación existente."""

    def post(self, request, pk):
        try:
            simulation = get_object_or_404(
                CreditSimulation,
                pk=pk,
                user=request.user
            )

            # Generar tabla de amortización
            entries = CreditSimulationService.generate_amortization_schedule(simulation)

            # Convertir a formato JSON
            schedule_data = []
            for entry in entries:
                schedule_data.append({
                    'installment_number': entry.installment_number,
                    'principal_payment': float(entry.principal_payment),
                    'interest_payment': float(entry.interest_payment),
                    'life_insurance_payment': float(entry.life_insurance_payment),
                    'total_payment': float(entry.total_payment),
                    'remaining_balance': float(entry.remaining_balance)
                })

            response_data = {
                'success': True,
                'data': {
                    'schedule': schedule_data,
                    'simulation_id': simulation.id
                }
            }

        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }

        return JsonResponse(response_data)


# =============================================================================
# VISTAS DE COMPARACIÓN DE PRODUCTOS
# =============================================================================

class ProductComparisonView(LoginRequiredMixin, TemplateView):
    """Vista para comparar diferentes productos de crédito."""

    template_name = 'credit_simulator/product_comparison.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener parámetros de comparación
        amount = self.request.GET.get('amount')
        term_months = self.request.GET.get('term_months')

        context['comparison_form'] = {
            'amount': amount,
            'term_months': term_months
        }

        if amount and term_months:
            try:
                amount = Decimal(str(amount))
                term_months = int(term_months)

                # Obtener productos disponibles para el monto
                available_products = CreditProductService.get_available_products_for_amount(amount)

                # Realizar simulaciones para cada producto
                comparisons = []
                for product in available_products:
                    if product.is_term_valid(term_months):
                        try:
                            calculator = CreditSimulationService._get_calculator(product.amortization_type)
                            result = calculator.calculate(product, amount, term_months)

                            comparisons.append({
                                'product': product,
                                'result': result
                            })
                        except Exception:
                            continue  # Skip products with calculation errors

                # Ordenar por cuota mensual
                comparisons.sort(key=lambda x: x['result']['monthly_payment'])

                context['comparisons'] = comparisons
                context['amount'] = amount
                context['term_months'] = term_months

            except (ValueError, TypeError):
                messages.error(self.request, 'Los parámetros ingresados no son válidos.')

        context['active_products'] = CreditProduct.objects.active().order_by('commercial_name')

        return context


# =============================================================================
# VISTA PARA EXPORTAR SIMULACIONES
# =============================================================================

class ExportSimulationView(LoginRequiredMixin, View):
    """Vista para exportar simulación a PDF o Excel (implementación básica)."""

    def get(self, request, pk):
        simulation = get_object_or_404(
            CreditSimulation,
            pk=pk,
            user=request.user
        )

        export_format = request.GET.get('format', 'pdf')

        if export_format == 'pdf':
            return self._export_to_pdf(simulation)
        elif export_format == 'excel':
            return self._export_to_excel(simulation)
        else:
            messages.error(request, 'Formato de exportación no válido.')
            return redirect('credit_simulator:simulation_result', pk=pk)

    def _export_to_pdf(self, simulation):
        """Exportar simulación a PDF (implementación simplificada)."""
        # Aquí implementarías la generación del PDF
        # Por ahora retornamos un mensaje
        messages.info(
            self.request,
            'La exportación a PDF estará disponible próximamente.'
        )
        return redirect('credit_simulator:simulation_result', pk=simulation.pk)

    def _export_to_excel(self, simulation):
        """Exportar simulación a Excel (implementación simplificada)."""
        # Aquí implementarías la generación del Excel
        # Por ahora retornamos un mensaje
        messages.info(
            self.request,
            'La exportación a Excel estará disponible próximamente.'
        )
        return redirect('credit_simulator:simulation_result', pk=simulation.pk)


# =============================================================================
# VISTAS DE REPORTES PARA STAFF
# =============================================================================

class SimulationReportsView(StaffRequiredMixin, TemplateView):
    """Vista de reportes de simulaciones para staff."""

    template_name = 'credit_simulator/staff/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas por producto
        product_stats = (
            CreditProduct.objects
            .annotate(
                simulation_count=Count('simulations'),
                avg_amount=Avg('simulations__requested_amount'),
                total_amount=Sum('simulations__requested_amount')
            )
            .filter(simulation_count__gt=0)
            .order_by('-simulation_count')
        )

        # Simulaciones por mes (últimos 12 meses) - Versión corregida
        monthly_simulations = (
            CreditSimulation.objects
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        context.update({
            'product_stats': product_stats,
            'monthly_simulations': monthly_simulations,
            'total_simulations': CreditSimulation.objects.count(),
            'total_users_with_simulations': CreditSimulation.objects.values('user').distinct().count(),
        })

        return context
