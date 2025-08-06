# banking/models.py

from django.db import models
from django.conf import settings


class Account(models.Model):
    """
    Representa una cuenta de ahorros de un socio.
    La información de esta tabla es un espejo de los datos del sistema SAC.
    """
    socio = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
        verbose_name="Socio"
    )
    account_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de Cuenta"
    )
    cash_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Saldo en Efectivo"
    )
    local_checks_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Saldo en Cheques Locales"
    )
    internal_checks_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Saldo en Cheques Propios"
    )
    reserve_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Encaje",
        help_text="Dinero bloqueado por encaje."
    )
    other_guarantees_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Otras Garantías"
    )

    class Meta:
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"
        ordering = ['socio', 'account_number']

    def __str__(self):
        return f'Cuenta {self.account_number} ({self.socio.username})'


class Transaction(models.Model):
    """
    Representa un movimiento o transacción individual en una cuenta.
    La información de esta tabla es un espejo de los datos del sistema SAC.
    """

    class TransactionType(models.TextChoices):
        INAH = 'INAH', 'INAH'
        ACCI = 'ACCI', 'ACCI'
        DEAH = 'DEAH', 'DEAH'
        AHPA = 'AHPA', 'AHPA'
        NDAH = 'NDAH', 'NDAH'
        AHCE = 'AHCE', 'AHCE'
        REAH = 'REAH', 'REAH'
        DBAH = 'DBAH', 'DBAH'
        NCAH = 'NCAH', 'NCAH'

    class FlowType(models.TextChoices):
        INCOME = 'I', 'Ingreso'
        OUTCOME = 'E', 'Egreso'

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Cuenta"
    )
    transaction_type = models.CharField(
        max_length=4,
        choices=TransactionType.choices,
        verbose_name="Tipo de Transacción"
    )
    flow = models.CharField(
        max_length=1,
        choices=FlowType.choices,
        verbose_name="Flujo",
        help_text="Ingreso (I) o Egreso (E)"
    )
    transaction_date = models.DateField(verbose_name="Fecha de Transacción")
    transaction_time = models.TimeField(verbose_name="Hora de Transacción")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Monto"
    )
    cash_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Monto en Efectivo"
    )
    balance_after_transaction = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Saldo Post-Transacción"
    )
    description = models.CharField(
        max_length=255,
        verbose_name="Detalle"
    )

    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"
        ordering = ['-transaction_date', '-transaction_time']

    def __str__(self):
        return f'Transacción de {self.amount} en {self.account.account_number}'
