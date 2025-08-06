# banking/models.py

from django.db import models
from django.conf import settings


class Account(models.Model):
    """
    Representa una cuenta de ahorros de un socio. Un socio puede tener varias.
    """
    # El socio al que pertenece la cuenta.
    socio = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cuentas")

    # Datos de la cuenta según el mapeo
    numero_cuenta = models.CharField(max_length=20, unique=True)
    saldo_efectivo = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    cheques_locales = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    cheques_propios = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    encaje = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Dinero bloqueado por encaje")
    otras_garantias = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f'Cuenta {self.numero_cuenta} ({self.socio.username})'


class Transaction(models.Model):
    """
    Representa un movimiento o transacción individual en una cuenta.
    """

    # Enumeraciones para los campos con opciones fijas
    class Tipo(models.TextChoices):
        INAH = 'INAH', 'INAH'
        ACCI = 'ACCI', 'ACCI'
        DEAH = 'DEAH', 'DEAH'
        AHPA = 'AHPA', 'AHPA'
        NDAH = 'NDAH', 'NDAH'
        AHCE = 'AHCE', 'AHCE'
        REAH = 'REAH', 'REAH'
        DBAH = 'DBAH', 'DBAH'
        NCAH = 'NCAH', 'NCAH'

    class Flujo(models.TextChoices):
        INGRESO = 'I', 'Ingreso'
        EGRESO = 'E', 'Egreso'

    # La cuenta a la que pertenece esta transacción.
    cuenta = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transacciones")

    # Datos de la transacción
    tipo_transferencia = models.CharField(max_length=4, choices=Tipo.choices)
    flujo = models.CharField(max_length=1, choices=Flujo.choices, help_text="Ingreso (I) o Egreso (E)")
    fecha_transferencia = models.DateField()
    hora_transferencia = models.TimeField()
    valor_transferencia = models.DecimalField(max_digits=12, decimal_places=2)
    efectivo_transferencia = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_post_transferencia = models.DecimalField(max_digits=12, decimal_places=2)
    detalle_transferencia = models.CharField(max_length=255)

    def __str__(self):
        return f'Transacción de {self.valor_transferencia} en cuenta {self.cuenta.numero_cuenta}'
