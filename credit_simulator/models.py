# credit_simulator/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP
import math


class CreditProductManager(models.Manager):
    """Manager personalizado para productos de crédito."""

    def active(self):
        """Retorna solo los productos activos."""
        return self.filter(is_active=True)

    def for_amount(self, amount):
        """Retorna productos disponibles para un monto específico."""
        return self.active().filter(
            minimum_amount__lte=amount,
            maximum_amount__gte=amount
        )


class CreditProduct(models.Model):
    """
    Modelo que define los diferentes tipos de productos de crédito
    disponibles en la cooperativa.
    """

    AMORTIZATION_CHOICES = [
        ('FRENCH', 'Francesa (Cuota fija)'),
        ('GERMAN', 'Alemana (Capital fijo)'),
    ]

    # Información básica del producto
    commercial_name = models.CharField(
        'Nombre comercial',
        max_length=100,
        help_text='Nombre del producto que verán los usuarios'
    )
    internal_code = models.CharField(
        'Código interno',
        max_length=20,
        unique=True,
        help_text='Código único para identificación interna'
    )
    description = models.TextField(
        'Descripción',
        blank=True,
        help_text='Descripción detallada del producto'
    )

    # Parámetros financieros
    minimum_amount = models.DecimalField(
        'Monto mínimo',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))],
        help_text='Monto mínimo a prestar'
    )
    maximum_amount = models.DecimalField(
        'Monto máximo',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))],
        help_text='Monto máximo a prestar'
    )
    minimum_term_months = models.PositiveSmallIntegerField(
        'Plazo mínimo (meses)',
        validators=[MinValueValidator(1)],
        help_text='Plazo mínimo en meses'
    )
    maximum_term_months = models.PositiveSmallIntegerField(
        'Plazo máximo (meses)',
        validators=[MinValueValidator(1)],
        help_text='Plazo máximo en meses'
    )
    annual_interest_rate = models.DecimalField(
        'Tasa de interés anual (%)',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('99.99'))],
        help_text='Tasa de interés anual en porcentaje'
    )

    # Configuración del crédito
    amortization_type = models.CharField(
        'Tipo de amortización',
        max_length=10,
        choices=AMORTIZATION_CHOICES,
        default='FRENCH',
        help_text='Sistema de amortización del crédito'
    )

    # Seguro de desgravamen
    has_life_insurance = models.BooleanField(
        'Incluye seguro de desgravamen',
        default=True,
        help_text='Si el crédito incluye seguro de desgravamen'
    )
    life_insurance_rate = models.DecimalField(
        'Tasa seguro de desgravamen (%)',
        max_digits=4,
        decimal_places=3,
        default=Decimal('0.500'),
        validators=[MinValueValidator(Decimal('0.000')), MaxValueValidator(Decimal('9.999'))],
        help_text='Tasa mensual del seguro de desgravamen sobre saldo'
    )

    # Control de estado
    is_active = models.BooleanField(
        'Activo',
        default=True,
        help_text='Si el producto está disponible para simulaciones'
    )

    # Metadatos
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='created_credit_products',
        verbose_name='Creado por'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='updated_credit_products',
        verbose_name='Actualizado por',
        null=True,
        blank=True
    )

    objects = CreditProductManager()

    class Meta:
        verbose_name = 'Producto de Crédito'
        verbose_name_plural = 'Productos de Crédito'
        ordering = ['commercial_name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['minimum_amount', 'maximum_amount']),
        ]

    def __str__(self):
        return f"{self.commercial_name} ({self.internal_code})"

    def clean(self):
        """Validaciones personalizadas del modelo."""
        super().clean()

        # Validar que el monto máximo sea mayor al mínimo
        if self.minimum_amount and self.maximum_amount:
            if self.minimum_amount >= self.maximum_amount:
                raise ValidationError({
                    'maximum_amount': 'El monto máximo debe ser mayor al mínimo.'
                })

        # Validar que el plazo máximo sea mayor al mínimo
        if self.minimum_term_months and self.maximum_term_months:
            if self.minimum_term_months >= self.maximum_term_months:
                raise ValidationError({
                    'maximum_term_months': 'El plazo máximo debe ser mayor al mínimo.'
                })

        # Validar seguro de desgravamen
        if self.has_life_insurance and not self.life_insurance_rate:
            raise ValidationError({
                'life_insurance_rate': 'Debe especificar la tasa del seguro de desgravamen.'
            })

    @property
    def monthly_interest_rate(self):
        """Retorna la tasa de interés mensual como decimal."""
        return self.annual_interest_rate / Decimal('1200')  # 12 meses * 100%

    def is_amount_valid(self, amount):
        """Verifica si un monto está dentro del rango permitido."""
        return self.minimum_amount <= amount <= self.maximum_amount

    def is_term_valid(self, term_months):
        """Verifica si un plazo está dentro del rango permitido."""
        return self.minimum_term_months <= term_months <= self.maximum_term_months


class CreditSimulation(models.Model):
    """
    Modelo para almacenar las simulaciones realizadas por los usuarios.
    Permite auditoría y análisis de comportamiento.
    """

    credit_product = models.ForeignKey(
        CreditProduct,
        on_delete=models.CASCADE,
        related_name='simulations',
        verbose_name='Producto de crédito'
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='credit_simulations',
        verbose_name='Usuario',
        null=True,
        blank=True,
        help_text='Usuario que realizó la simulación (puede ser anónimo)'
    )

    # Parámetros de la simulación
    requested_amount = models.DecimalField(
        'Monto solicitado',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))]
    )
    term_months = models.PositiveSmallIntegerField(
        'Plazo en meses',
        validators=[MinValueValidator(1)]
    )

    # Resultados calculados
    monthly_payment = models.DecimalField(
        'Cuota mensual',
        max_digits=10,
        decimal_places=2,
        help_text='Cuota mensual calculada'
    )
    total_interest = models.DecimalField(
        'Total de intereses',
        max_digits=12,
        decimal_places=2,
        help_text='Total de intereses a pagar'
    )
    total_life_insurance = models.DecimalField(
        'Total seguro de desgravamen',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total del seguro de desgravamen'
    )
    total_amount = models.DecimalField(
        'Monto total a pagar',
        max_digits=12,
        decimal_places=2,
        help_text='Monto total incluyendo capital, intereses y seguros'
    )

    # Metadatos
    created_at = models.DateTimeField('Fecha de simulación', auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        'Dirección IP',
        null=True,
        blank=True,
        help_text='IP desde donde se realizó la simulación'
    )

    class Meta:
        verbose_name = 'Simulación de Crédito'
        verbose_name_plural = 'Simulaciones de Crédito'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['credit_product', '-created_at']),
        ]

    def __str__(self):
        user_display = self.user.username if self.user else 'Anónimo'
        return (f"Simulación de {user_display} - "
                f"{self.credit_product.commercial_name} - "
                f"${self.requested_amount}")


class AmortizationScheduleEntry(models.Model):
    """
    Modelo para almacenar las entradas individuales de la tabla de amortización.
    Se genera dinámicamente para cada simulación cuando se requiere el detalle.
    """

    simulation = models.ForeignKey(
        CreditSimulation,
        on_delete=models.CASCADE,
        related_name='amortization_entries',
        verbose_name='Simulación'
    )
    installment_number = models.PositiveSmallIntegerField('Número de cuota')

    # Componentes de la cuota
    principal_payment = models.DecimalField(
        'Pago a capital',
        max_digits=10,
        decimal_places=2
    )
    interest_payment = models.DecimalField(
        'Pago de interés',
        max_digits=10,
        decimal_places=2
    )
    life_insurance_payment = models.DecimalField(
        'Pago seguro de desgravamen',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_payment = models.DecimalField(
        'Pago total',
        max_digits=10,
        decimal_places=2
    )
    remaining_balance = models.DecimalField(
        'Saldo pendiente',
        max_digits=12,
        decimal_places=2
    )

    class Meta:
        verbose_name = 'Entrada de Tabla de Amortización'
        verbose_name_plural = 'Entradas de Tabla de Amortización'
        ordering = ['simulation', 'installment_number']
        unique_together = ['simulation', 'installment_number']
        indexes = [
            models.Index(fields=['simulation', 'installment_number']),
        ]

    def __str__(self):
        return (f"Cuota {self.installment_number} - "
                f"Simulación {self.simulation.id}")
