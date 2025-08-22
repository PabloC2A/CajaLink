# legacy_models/managers.py
from decimal import Decimal
from datetime import date, timedelta
from typing import Optional
from django.db import models
from django.db.models import Q, Sum, Count, Max, Min, Avg, F, Case, When, Value
from django.db.models.functions import Coalesce
from django.utils import timezone


class SocioQuerySet(models.QuerySet):
    """
    QuerySet personalizado para Socio que encapsula consultas complejas.
    Principio: Separation of Concerns
    """

    def with_web_user(self):
        """Filtra socios que tienen usuario web vinculado"""
        return self.filter(usersociolink__isnull=False)

    def without_web_user(self):
        """Filtra socios que NO tienen usuario web vinculado"""
        return self.filter(usersociolink__isnull=True)

    def active(self):
        """Filtra socios activos"""
        return self.filter(estado='A', cerrado=False)

    def inactive(self):
        """Filtra socios inactivos"""
        return self.filter(Q(estado__ne='A') | Q(cerrado=True))

    def morosos(self):
        """Filtra socios morosos"""
        return self.filter(moroso=True)

    def non_morosos(self):
        """Filtra socios sin morosidad"""
        return self.filter(Q(moroso=False) | Q(moroso__isnull=True))

    def with_savings(self, min_amount: Decimal = Decimal('0')):
        """Filtra socios con ahorros mayor al mínimo especificado"""
        return self.filter(efectivo__gt=min_amount)

    def with_certificates(self, min_amount: Decimal = Decimal('0')):
        """Filtra socios con certificados mayor al mínimo especificado"""
        return self.filter(certifica__gt=min_amount)

    def with_financial_activity(self):
        """Filtra socios con actividad financiera (ahorros, certificados o créditos)"""
        return self.filter(
            Q(efectivo__gt=0) |
            Q(certifica__gt=0) |
            Q(creditos__isnull=False)
        ).distinct()

    def by_cedula(self, cedula: str):
        """Busca socio por cédula"""
        return self.filter(cedula=cedula)

    def by_name_contains(self, name: str):
        """Busca socios que contengan el nombre especificado"""
        return self.filter(
            Q(nombres__icontains=name) |
            Q(apellidos__icontains=name)
        )


class SocioManager(models.Manager):
    """
    Manager personalizado para Socio.
    Principio: Single Responsibility Principle
    """

    def get_queryset(self):
        return SocioQuerySet(self.model, using=self._db)

    def with_web_user(self):
        return self.get_queryset().with_web_user()

    def without_web_user(self):
        return self.get_queryset().without_web_user()

    def active(self):
        return self.get_queryset().active()

    def inactive(self):
        return self.get_queryset().inactive()

    def morosos(self):
        return self.get_queryset().morosos()

    def non_morosos(self):
        return self.get_queryset().non_morosos()

    def with_savings(self, min_amount: Decimal = Decimal('0')):
        return self.get_queryset().with_savings(min_amount)

    def with_certificates(self, min_amount: Decimal = Decimal('0')):
        return self.get_queryset().with_certificates(min_amount)

    def with_financial_activity(self):
        return self.get_queryset().with_financial_activity()

    def by_cedula(self, cedula: str):
        return self.get_queryset().by_cedula(cedula)

    def by_name_contains(self, name: str):
        return self.get_queryset().by_name_contains(name)

    def get_with_financial_summary(self, cuenta: str):
        """
        Obtiene un socio con resumen financiero calculado.
        Optimiza consultas mediante anotaciones.
        """
        try:
            return self.get_queryset().select_related().prefetch_related(
                'creditos',
                'plazos_fijos',
                'ahorros_historial',
                'certificados_historial'
            ).annotate(
                total_creditos=Count('creditos'),
                saldo_total_creditos=Coalesce(Sum('creditos__sal_pre'), Decimal('0.00')),
                total_plazos=Count('plazos_fijos'),
                inversion_total_plazos=Coalesce(Sum('plazos_fijos__cantidad'), Decimal('0.00'))
            ).get(cuenta=cuenta)
        except self.model.DoesNotExist:
            return None


class CreditoQuerySet(models.QuerySet):
    """QuerySet para consultas específicas de Crédito"""

    def active(self):
        """Créditos activos (no pagados completamente y con saldo pendiente)"""
        return self.filter(
            Q(pagado=False) | Q(pagado__isnull=True)
        ).exclude(sal_pre=0)

    def paid(self):
        """Créditos pagados completamente"""
        return self.filter(pagado=True)

    def with_pending_payments(self):
        """Créditos con pagos pendientes"""
        return self.active().filter(sal_pre__gt=0)

    def overdue(self):
        """Créditos con cuotas vencidas"""
        today = timezone.now().date()
        return self.filter(
            cuotas_credito__fecha_ven__lt=today,
            cuotas_credito__pagado=False
        ).distinct()

    def by_date_range(self, start_date: date, end_date: date):
        """Filtra créditos por rango de fecha de préstamo"""
        return self.filter(fech_pres__gte=start_date, fech_pres__lte=end_date)

    def by_amount_range(self, min_amount: Decimal, max_amount: Decimal):
        """Filtra créditos por rango de valor"""
        return self.filter(val_prest__gte=min_amount, val_prest__lte=max_amount)

    def with_balance_greater_than(self, amount: Decimal):
        """Filtra créditos con saldo mayor al especificado"""
        return self.filter(sal_pre__gt=amount)

    def judicial(self):
        """Filtra créditos en proceso judicial"""
        return self.filter(judicial=True)

    def castigados(self):
        """Filtra créditos castigados"""
        return self.filter(castigada=True)

    def with_payment_summary(self):
        """Anota información de resumen de pagos"""
        return self.annotate(
            cuotas_totales=Count('cuotas_credito'),
            cuotas_pagadas=Count('cuotas_credito', filter=Q(cuotas_credito__pagado=True)),
            cuotas_pendientes=Count(
                'cuotas_credito',
                filter=Q(cuotas_credito__pagado=False) | Q(cuotas_credito__pagado__isnull=True)
            ),
            proxima_cuota_fecha=Min(
                'cuotas_credito__fecha_ven',
                filter=Q(cuotas_credito__pagado=False) | Q(cuotas_credito__pagado__isnull=True)
            ),
            total_pendiente_cuotas=Sum(
                'cuotas_credito__pagar',
                filter=Q(cuotas_credito__pagado=False) | Q(cuotas_credito__pagado__isnull=True)
            )
        )


class CreditoManager(models.Manager):
    """Manager para Credito"""

    def get_queryset(self):
        return CreditoQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def paid(self):
        return self.get_queryset().paid()

    def with_pending_payments(self):
        return self.get_queryset().with_pending_payments()

    def overdue(self):
        return self.get_queryset().overdue()

    def by_date_range(self, start_date: date, end_date: date):
        return self.get_queryset().by_date_range(start_date, end_date)

    def by_amount_range(self, min_amount: Decimal, max_amount: Decimal):
        return self.get_queryset().by_amount_range(min_amount, max_amount)

    def with_balance_greater_than(self, amount: Decimal):
        return self.get_queryset().with_balance_greater_than(amount)

    def judicial(self):
        return self.get_queryset().judicial()

    def castigados(self):
        return self.get_queryset().castigados()

    def with_payment_summary(self):
        return self.get_queryset().with_payment_summary()

    def get_monthly_disbursements(self, year: int, month: int):
        """Obtiene los desembolsos del mes especificado"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        return self.by_date_range(start_date, end_date)


class CreditoCuotaQuerySet(models.QuerySet):
    """QuerySet para cuotas de crédito"""

    def pending(self):
        """Cuotas pendientes de pago"""
        return self.filter(Q(pagado=False) | Q(pagado__isnull=True))

    def paid(self):
        """Cuotas pagadas"""
        return self.filter(pagado=True)

    def overdue(self):
        """Cuotas vencidas"""
        today = timezone.now().date()
        return self.pending().filter(fecha_ven__lt=today)

    def due_soon(self, days: int = 7):
        """Cuotas que vencen pronto"""
        future_date = timezone.now().date() + timedelta(days=days)
        return self.pending().filter(fecha_ven__lte=future_date)

    def by_credit(self, credit):
        """Filtra cuotas por crédito"""
        return self.filter(num_paga=credit)

    def by_socio(self, socio):
        """Filtra cuotas por socio"""
        return self.filter(num_paga__cuenta=socio)


class CreditoCuotaManager(models.Manager):
    """Manager para CreditoCuota"""

    def get_queryset(self):
        return CreditoCuotaQuerySet(self.model, using=self._db)

    def pending(self):
        return self.get_queryset().pending()

    def paid(self):
        return self.get_queryset().paid()

    def overdue(self):
        return self.get_queryset().overdue()

    def due_soon(self, days: int = 7):
        return self.get_queryset().due_soon(days)

    def by_credit(self, credit):
        return self.get_queryset().by_credit(credit)

    def by_socio(self, socio):
        return self.get_queryset().by_socio(socio)


class PlazoFijoQuerySet(models.QuerySet):
    """QuerySet para consultas específicas de PlazoFijo"""

    def active(self):
        """Plazos fijos activos (no pagados)"""
        return self.filter(Q(pagado=False) | Q(pagado__isnull=True))

    def paid(self):
        """Plazos fijos pagados/vencidos"""
        return self.filter(pagado=True)

    def matured(self):
        """Plazos fijos vencidos"""
        today = timezone.now().date()
        return self.filter(fechavenci__lt=today)

    def maturing_soon(self, days: int = 30):
        """Plazos fijos que vencen en los próximos N días"""
        future_date = timezone.now().date() + timedelta(days=days)
        today = timezone.now().date()
        return self.active().filter(
            fechavenci__gte=today,
            fechavenci__lte=future_date
        )

    def by_amount_range(self, min_amount: Decimal, max_amount: Decimal):
        """Filtra por rango de cantidad"""
        return self.filter(cantidad__gte=min_amount, cantidad__lte=max_amount)

    def by_deposit_date_range(self, start_date: date, end_date: date):
        """Filtra por rango de fecha de depósito"""
        return self.filter(fechadepos__gte=start_date, fechadepos__lte=end_date)

    def by_maturity_date_range(self, start_date: date, end_date: date):
        """Filtra por rango de fecha de vencimiento"""
        return self.filter(fechavenci__gte=start_date, fechavenci__lte=end_date)

    def with_maturity_analysis(self):
        """Anota análisis de vencimiento"""
        today = timezone.now().date()
        return self.annotate(
            dias_hasta_vencimiento=Case(
                When(
                    fechavenci__isnull=False,
                    then=F('fechavenci') - Value(today)
                ),
                default=Value(0)
            ),
            estado_vencimiento=Case(
                When(fechavenci__lt=today, then=Value('vencido')),
                When(fechavenci__lte=today + timedelta(days=30), then=Value('proximo_vencer')),
                When(fechavenci__gt=today + timedelta(days=30), then=Value('vigente')),
                default=Value('sin_fecha'),
                output_field=models.CharField()
            )
        )


class PlazoFijoManager(models.Manager):
    """Manager para PlazoFijo"""

    def get_queryset(self):
        return PlazoFijoQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def paid(self):
        return self.get_queryset().paid()

    def matured(self):
        return self.get_queryset().matured()

    def maturing_soon(self, days: int = 30):
        return self.get_queryset().maturing_soon(days)

    def by_amount_range(self, min_amount: Decimal, max_amount: Decimal):
        return self.get_queryset().by_amount_range(min_amount, max_amount)

    def by_deposit_date_range(self, start_date: date, end_date: date):
        return self.get_queryset().by_deposit_date_range(start_date, end_date)

    def by_maturity_date_range(self, start_date: date, end_date: date):
        return self.get_queryset().by_maturity_date_range(start_date, end_date)

    def with_maturity_analysis(self):
        return self.get_queryset().with_maturity_analysis()

    def get_portfolio_metrics(self, socio):
        """Obtiene métricas del portafolio de un socio"""
        plazos = self.filter(cuenta=socio).active()

        if not plazos.exists():
            return {
                'total_inversiones': 0,
                'monto_total': Decimal('0.00'),
                'inversion_promedio': Decimal('0.00'),
                'inversion_mayor': Decimal('0.00'),
                'inversion_menor': Decimal('0.00'),
            }

        return plazos.aggregate(
            total_inversiones=Count('id'),
            monto_total=Coalesce(Sum('cantidad'), Decimal('0.00')),
            inversion_promedio=Coalesce(Avg('cantidad'), Decimal('0.00')),
            inversion_mayor=Coalesce(Max('cantidad'), Decimal('0.00')),
            inversion_menor=Coalesce(Min('cantidad'), Decimal('0.00'))
        )


class TransactionQuerySet(models.QuerySet):
    """QuerySet base para transacciones (AhorroHistorial y CertificadoHistorial)"""

    def ingresos(self):
        """Filtra solo ingresos"""
        return self.filter(ingre_egre='I')

    def egresos(self):
        """Filtra solo egresos"""
        return self.filter(ingre_egre='E')

    def by_date_range(self, start_date: date, end_date: date):
        """Filtra por rango de fechas"""
        return self.filter(fecha_tra__gte=start_date, fecha_tra__lte=end_date)

    def by_amount_range(self, min_amount: Decimal, max_amount: Decimal):
        """Filtra por rango de valores"""
        return self.filter(valor__gte=min_amount, valor__lte=max_amount)

    def recent(self, days: int = 30):
        """Transacciones recientes"""
        start_date = timezone.now().date() - timedelta(days=days)
        return self.filter(fecha_tra__gte=start_date)

    def by_transaction_type(self, tipo: str):
        """Filtra por tipo de transacción"""
        return self.filter(tipo_tra=tipo)

    def with_summary(self):
        """Anota resumen de transacciones"""
        return self.aggregate(
            total_transacciones=Count('id'),
            total_ingresos=Coalesce(Sum('valor', filter=Q(ingre_egre='I')), Decimal('0.00')),
            total_egresos=Coalesce(Sum('valor', filter=Q(ingre_egre='E')), Decimal('0.00')),
            balance_neto=Coalesce(Sum('valor', filter=Q(ingre_egre='I')), Decimal('0.00')) -
                         Coalesce(Sum('valor', filter=Q(ingre_egre='E')), Decimal('0.00')),
            promedio_transaccion=Coalesce(Avg('valor'), Decimal('0.00')),
            monto_mayor=Coalesce(Max('valor'), Decimal('0.00')),
            monto_menor=Coalesce(Min('valor'), Decimal('0.00'))
        )


class AhorroHistorialManager(models.Manager):
    """Manager para AhorroHistorial"""

    def get_queryset(self):
        return TransactionQuerySet(self.model, using=self._db)

    def ingresos(self):
        return self.get_queryset().ingresos()

    def egresos(self):
        return self.get_queryset().egresos()

    def by_date_range(self, start_date: date, end_date: date):
        return self.get_queryset().by_date_range(start_date, end_date)

    def by_amount_range(self, min_amount: Decimal, max_amount: Decimal):
        return self.get_queryset().by_amount_range(min_amount, max_amount)

    def recent(self, days: int = 30):
        return self.get_queryset().recent(days)

    def by_transaction_type(self, tipo: str):
        return self.get_queryset().by_transaction_type(tipo)


class CertificadoHistorialManager(models.Manager):
    """Manager para CertificadoHistorial"""

    def get_queryset(self):
        return TransactionQuerySet(self.model, using=self._db)

    def ingresos(self):
        return self.get_queryset().ingresos()

    def egresos(self):
        return self.get_queryset().egresos()

    def by_date_range(self, start_date: date, end_date: date):
        return self.get_queryset().by_date_range(start_date, end_date)

    def by_amount_range(self, min_amount: Decimal, max_amount: Decimal):
        return self.get_queryset().by_amount_range(min_amount, max_amount)

    def recent(self, days: int = 30):
        return self.get_queryset().recent(days)

    def by_transaction_type(self, tipo: str):
        return self.get_queryset().by_transaction_type(tipo)
