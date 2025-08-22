# legacy_models/models.py

from decimal import Decimal
from typing import Dict, Optional

from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone

from .managers import (
    SocioManager,
    CreditoManager,
    CreditoCuotaManager,
    PlazoFijoManager,
    AhorroHistorialManager,
    CertificadoHistorialManager
)


class Socio(models.Model):
    id = models.AutoField(primary_key=True)
    area = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    cuenta = models.CharField("Cuenta", max_length=8, unique=True)
    tipo = models.CharField("Tipo", max_length=1, blank=True, null=True)
    nuevo = models.BooleanField("Nuevo", blank=True, null=True)
    ingreso = models.DecimalField("Ingreso", max_digits=10, decimal_places=0, blank=True, null=True)
    cedula = models.CharField("Cédula", max_length=13, blank=True, null=True)
    apellidos = models.CharField("Apellidos", max_length=25, blank=True, null=True)
    nombres = models.CharField("Nombres", max_length=25, blank=True, null=True)
    sexo = models.BooleanField("Sexo", blank=True, null=True)
    esta_civil = models.CharField("Estado Civil", max_length=15, blank=True, null=True)
    tipo_sang = models.CharField("Tipo Sangre", max_length=4, blank=True, null=True)
    fecha_naci = models.DateField("Fecha Nacimiento", blank=True, null=True)
    fech_ing = models.DateField("Fecha Ingreso", blank=True, null=True)
    ocupa_id = models.CharField("Ocupación ID", max_length=2, blank=True, null=True)
    instrucc = models.CharField("Instrucción", max_length=15, blank=True, null=True)
    conyuge = models.CharField("Cónyuge", max_length=30, blank=True, null=True)
    f_na_cony = models.DateField("Fecha Nac. Cónyuge", blank=True, null=True)
    ced_cony = models.CharField("Cédula Cónyuge", max_length=10, blank=True, null=True)
    beneficia = models.CharField("Beneficiario", max_length=35, blank=True, null=True)
    direccion = models.CharField("Dirección", max_length=80, blank=True, null=True)
    direcctrab = models.CharField("Dirección Trabajo", max_length=80, blank=True, null=True)
    parroquia = models.CharField("Parroquia", max_length=3, blank=True, null=True)
    barrio = models.CharField("Barrio", max_length=3, blank=True, null=True)
    sector = models.CharField("Sector", max_length=3, blank=True, null=True)
    telefono = models.CharField("Teléfono", max_length=20, blank=True, null=True)
    telefono1 = models.CharField("Teléfono 1", max_length=10, blank=True, null=True)
    email = models.CharField("Email", max_length=50, blank=True, null=True)
    efectivo = models.DecimalField("Efectivo", max_digits=10, decimal_places=2, blank=True, null=True)
    chequesloc = models.DecimalField("Cheques Locales", max_digits=10, decimal_places=2, blank=True, null=True)
    chequespro = models.DecimalField("Cheques en Proceso", max_digits=10, decimal_places=2, blank=True, null=True)
    int_ahor = models.DecimalField("Interés Ahorros", max_digits=10, decimal_places=4, blank=True, null=True)
    certifica = models.DecimalField("Certificados", max_digits=10, decimal_places=2, blank=True, null=True)
    int_cert = models.DecimalField("Interés Certificados", max_digits=10, decimal_places=4, blank=True, null=True)
    certi_edif = models.DecimalField("Certificado Edificio", max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_ut = models.DateField("Fecha Última Transacción", blank=True, null=True)
    encaje = models.DecimalField("Encaje", max_digits=10, decimal_places=2, blank=True, null=True)
    otrasgaran = models.DecimalField("Otras Garantías", max_digits=10, decimal_places=2, blank=True, null=True)
    fondo_mor = models.DecimalField("Fondo Moroso", max_digits=10, decimal_places=2, blank=True, null=True)
    pagadofm = models.BooleanField("Pagado Fondo Moroso", blank=True, null=True)
    totaldepos = models.DecimalField("Total Depósitos", max_digits=10, decimal_places=2, blank=True, null=True)
    totalretir = models.DecimalField("Total Retiros", max_digits=10, decimal_places=2, blank=True, null=True)
    bloqueo = models.BooleanField("Bloqueo", blank=True, null=True)
    cerrado = models.BooleanField("Cerrado", blank=True, null=True)
    estado = models.BooleanField("Estado", blank=True, null=True)
    fechacierr = models.DateField("Fecha Cierre", blank=True, null=True)
    linlibreta = models.DecimalField("Línea Libreta", max_digits=10, decimal_places=0, blank=True, null=True)
    linlibcert = models.DecimalField("Línea Libreta Certificado", max_digits=10, decimal_places=0, blank=True,
                                     null=True)
    linfonmort = models.DecimalField("Línea Fondo Moroso", max_digits=10, decimal_places=0, blank=True, null=True)
    tipofirma = models.CharField("Tipo Firma", max_length=10, blank=True, null=True)
    firma_uno = models.TextField("Firma Uno", blank=True, null=True)
    firma_file = models.TextField("Archivo Firma", blank=True, null=True)
    foto = models.TextField("Foto", blank=True, null=True)
    comentar = models.TextField("Comentario", blank=True, null=True)
    fecha_ing_extra = models.DateField("Fecha Ingreso Extra", db_column='fecha_ing_', blank=True, null=True)
    respon_det = models.CharField("Responsable Detalle", max_length=40, blank=True, null=True)
    detalle = models.TextField("Detalle", blank=True, null=True)
    prome30 = models.DecimalField("Promedio 30", max_digits=10, decimal_places=2, blank=True, null=True)
    prome60 = models.DecimalField("Promedio 60", max_digits=10, decimal_places=2, blank=True, null=True)
    prome90 = models.DecimalField("Promedio 90", max_digits=10, decimal_places=2, blank=True, null=True)
    aho0 = models.DecimalField("Aho0", max_digits=10, decimal_places=2, blank=True, null=True)
    aho1 = models.DecimalField("Aho1", max_digits=10, decimal_places=2, blank=True, null=True)
    aho2 = models.DecimalField("Aho2", max_digits=10, decimal_places=2, blank=True, null=True)
    aho3 = models.DecimalField("Aho3", max_digits=10, decimal_places=2, blank=True, null=True)
    aho4 = models.DecimalField("Aho4", max_digits=10, decimal_places=2, blank=True, null=True)
    aho5 = models.DecimalField("Aho5", max_digits=10, decimal_places=2, blank=True, null=True)
    aho6 = models.DecimalField("Aho6", max_digits=10, decimal_places=2, blank=True, null=True)
    aho7 = models.DecimalField("Aho7", max_digits=10, decimal_places=2, blank=True, null=True)
    aho8 = models.DecimalField("Aho8", max_digits=10, decimal_places=2, blank=True, null=True)
    aho9 = models.DecimalField("Aho9", max_digits=10, decimal_places=2, blank=True, null=True)
    aho10 = models.DecimalField("Aho10", max_digits=10, decimal_places=2, blank=True, null=True)
    aho11 = models.DecimalField("Aho11", max_digits=10, decimal_places=2, blank=True, null=True)
    aho12 = models.DecimalField("Aho12", max_digits=10, decimal_places=2, blank=True, null=True)
    cer0 = models.DecimalField("Cer0", max_digits=10, decimal_places=2, blank=True, null=True)
    cer1 = models.DecimalField("Cer1", max_digits=10, decimal_places=2, blank=True, null=True)
    cer2 = models.DecimalField("Cer2", max_digits=10, decimal_places=2, blank=True, null=True)
    cer3 = models.DecimalField("Cer3", max_digits=10, decimal_places=2, blank=True, null=True)
    cer4 = models.DecimalField("Cer4", max_digits=10, decimal_places=2, blank=True, null=True)
    cer5 = models.DecimalField("Cer5", max_digits=10, decimal_places=2, blank=True, null=True)
    cer6 = models.DecimalField("Cer6", max_digits=10, decimal_places=2, blank=True, null=True)
    cer7 = models.DecimalField("Cer7", max_digits=10, decimal_places=2, blank=True, null=True)
    cer8 = models.DecimalField("Cer8", max_digits=10, decimal_places=2, blank=True, null=True)
    cer9 = models.DecimalField("Cer9", max_digits=10, decimal_places=2, blank=True, null=True)
    cer10 = models.DecimalField("Cer10", max_digits=10, decimal_places=2, blank=True, null=True)
    cer11 = models.DecimalField("Cer11", max_digits=10, decimal_places=2, blank=True, null=True)
    cer12 = models.DecimalField("Cer12", max_digits=10, decimal_places=2, blank=True, null=True)
    dnc = models.CharField("DNC", max_length=2, blank=True, null=True)
    fecha_moro = models.DateField("Fecha Morosidad", blank=True, null=True)
    responsabl = models.CharField("Responsable", max_length=30, blank=True, null=True)
    moroso = models.BooleanField("Moroso", blank=True, null=True)
    clave = models.CharField("Clave", max_length=6, blank=True, null=True)
    nombre1 = models.CharField("Nombre 1", max_length=40, blank=True, null=True)
    nombre2 = models.CharField("Nombre 2", max_length=40, blank=True, null=True)
    cedula1 = models.CharField("Cédula 1", max_length=10, blank=True, null=True)
    cedula2 = models.CharField("Cédula 2", max_length=10, blank=True, null=True)
    funcion1 = models.CharField("Función 1", max_length=20, blank=True, null=True)
    funcion2 = models.CharField("Función 2", max_length=20, blank=True, null=True)
    numlibreta = models.CharField("Número Libreta", max_length=8, blank=True, null=True)

    objects = SocioManager()

    class Meta:
        managed = False
        db_table = 'socios'
        verbose_name = "Socio (Legacy)"
        verbose_name_plural = "Socios (Legacy)"

    def __str__(self):
        return f"{self.cuenta} - {self.nombres} {self.apellidos}"

    # === MÉTODOS DE NEGOCIO PARA AHORROS ===

    def get_saldo_ahorros(self) -> Decimal:
        """
        Retorna el saldo disponible en ahorros.
        Principio: Encapsulación - La lógica del saldo está en el modelo
        """
        return self.efectivo or Decimal('0.00')

    def get_ahorros_data(self) -> Dict[str, Decimal]:
        """
        Retorna información consolidada de ahorros.
        Principio: Single Responsibility - Un metodo, una responsabilidad
        """
        return {
            'numero_cuenta': self.cuenta,
            'saldo_disponible': self.get_saldo_ahorros(),
        }

    # === MÉTODOS DE NEGOCIO PARA CERTIFICADOS ===

    def get_certificados_activos(self) -> Decimal:
        """
        Retorna la cantidad activa de certificados.
        """
        return self.certifica or Decimal('0.00')

    def get_certificados_data(self) -> Dict[str, Decimal]:
        """
        Retorna información consolidada de certificados.
        """
        return {
            'cantidad_activa': self.get_certificados_activos(),
        }

    # === MÉTODOS DE NEGOCIO PARA CRÉDITOS ===

    def get_creditos_activos(self):
        """
        Retorna QuerySet de créditos activos del socio.
        Principio: Law of Demeter - No acceder directamente a objetos relacionados desde la vista
        """
        return self.creditos.active()

    def get_proxima_cuota_info(self) -> Optional[Dict]:
        """
        Obtiene información de la próxima cuota a pagar.
        Retorna None si no hay cuotas pendientes.
        Principio: Encapsulación - La lógica compleja se maneja en el modelo
        """
        # Obtener la cuota más próxima no pagada usando el manager
        proxima_cuota = CreditoCuota.objects.by_socio(self).pending().order_by('fecha_ven').first()

        if not proxima_cuota:
            return None

        return {
            'monto': proxima_cuota.pagar or Decimal('0.00'),
            'fecha_vencimiento': proxima_cuota.fecha_ven,
            'credito': proxima_cuota.num_paga,
        }

    def get_creditos_data(self) -> Dict:
        """
        Retorna información consolidada de créditos.
        Principio: Single Responsibility
        """
        proxima_cuota = self.get_proxima_cuota_info()
        creditos_activos = self.get_creditos_activos()

        return {
            'creditos_activos_count': creditos_activos.count(),
            'saldo_total': creditos_activos.aggregate(
                total=Sum('sal_pre')
            )['total'] or Decimal('0.00'),
            'proxima_cuota': proxima_cuota,
        }

    def has_overdue_payments(self) -> bool:
        """
        Verifica si el socio tiene pagos vencidos.
        """
        return CreditoCuota.objects.by_socio(self).overdue().exists()

    def get_credit_payment_compliance(self) -> Decimal:
        """
        Calcula el porcentaje de cumplimiento en pagos.
        Retorna valor entre 0 y 100.
        """
        total_cuotas = CreditoCuota.objects.by_socio(self).count()
        if total_cuotas == 0:
            return Decimal('100.00')  # Sin créditos = 100% cumplimiento

        cuotas_pagadas = CreditoCuota.objects.by_socio(self).paid().count()
        return (Decimal(str(cuotas_pagadas)) / Decimal(str(total_cuotas))) * Decimal('100')

    # === MÉTODOS DE NEGOCIO PARA PLAZOS FIJOS ===

    def get_plazos_fijos_activos(self):
        """
        Retorna QuerySet de plazos fijos activos del socio.
        """
        return self.plazos_fijos.active()

    def get_inversion_total_plazos(self) -> Decimal:
        """
        Calcula la inversión total en plazos fijos activos.
        Principio: DRY - Esta lógica estaba duplicada en la vista
        """
        total_result = self.get_plazos_fijos_activos().aggregate(total=Sum('cantidad'))
        return total_result['total'] or Decimal('0.00')

    def get_plazos_data(self) -> Dict[str, Decimal]:
        """
        Retorna información consolidada de plazos fijos.
        """
        return {
            'inversion_total': self.get_inversion_total_plazos(),
            'plazos_activos_count': self.get_plazos_fijos_activos().count(),
        }

    def get_plazos_maturing_soon(self, days: int = 30):
        """
        Obtiene plazos fijos que vencen pronto.
        """
        return self.plazos_fijos.maturing_soon(days)

    # === METODO PRINCIPAL PARA DASHBOARD ===

    def get_dashboard_data(self) -> Dict:
        """
        Metodo principal que consolida toda la información del dashboard.
        Principio: Facade Pattern - Simplifica el acceso a múltiples subsistemas
        Principio: Single Responsibility - Cada submetodo maneja su dominio
        """
        return {
            'ahorros_data': self.get_ahorros_data(),
            'certificados_data': self.get_certificados_data(),
            'creditos_data': self.get_creditos_data(),
            'plazos_data': self.get_plazos_data(),
        }

    # === MÉTODOS DE ESTADO Y VALIDACIÓN ===

    def is_active(self) -> bool:
        """Verifica si el socio está activo"""
        return self.estado == 'A' and not self.cerrado

    def is_moroso(self) -> bool:
        """Verifica si el socio está en mora"""
        return self.moroso or self.has_overdue_payments()

    def get_full_name(self) -> str:
        """Retorna el nombre completo del socio"""
        nombres = self.nombres or ""
        apellidos = self.apellidos or ""
        return f"{nombres} {apellidos}".strip()

    def has_web_user(self) -> bool:
        """Verifica si el socio tiene usuario web vinculado"""
        return hasattr(self, 'usersociolink') and self.usersociolink is not None

    # === MÉTODOS DE ANÁLISIS FINANCIERO ===

    def get_patrimonio_total(self) -> Decimal:
        """Calcula el patrimonio total del socio"""
        return (
                self.get_saldo_ahorros() +
                self.get_certificados_activos() +
                self.get_inversion_total_plazos()
        )

    def get_obligaciones_totales(self) -> Decimal:
        """Calcula las obligaciones totales del socio"""
        creditos_data = self.get_creditos_data()
        return creditos_data.get('saldo_total', Decimal('0.00'))

    def get_patrimonio_neto(self) -> Decimal:
        """Calcula el patrimonio neto (patrimonio - obligaciones)"""
        return self.get_patrimonio_total() - self.get_obligaciones_totales()

    def get_ratio_endeudamiento(self) -> Decimal:
        """
        Calcula el ratio de endeudamiento como porcentaje.
        Retorna 0 si no hay patrimonio.
        """
        patrimonio = self.get_patrimonio_total()
        obligaciones = self.get_obligaciones_totales()

        if patrimonio == 0:
            return Decimal('0.00')

        return (obligaciones / patrimonio) * Decimal('100')


class AhorroHistorial(models.Model):
    id = models.AutoField(primary_key=True)
    cuenta = models.ForeignKey(Socio, on_delete=models.DO_NOTHING, to_field='cuenta', db_column='cuenta',
                               related_name='ahorros_historial')
    caja = models.CharField("Caja", max_length=2, blank=True, null=True)
    tipo_tra = models.CharField("Tipo Transacción", max_length=4, blank=True, null=True)
    num_trans = models.CharField("Número Transacción", max_length=8, blank=True, null=True)
    ingre_egre = models.CharField("Ingreso/Egreso", max_length=1, blank=True, null=True)
    ventani = models.CharField("Ventana", max_length=1, blank=True, null=True)
    fecha_tra = models.DateField("Fecha Transacción", blank=True, null=True)
    hora = models.CharField("Hora", max_length=5, blank=True, null=True)
    num_doc = models.CharField("Número Documento", max_length=11, blank=True, null=True)
    valor = models.DecimalField("Valor", max_digits=12, decimal_places=2, blank=True, null=True)
    efectivo = models.DecimalField("Efectivo", max_digits=12, decimal_places=2, blank=True, null=True)
    chequesloc = models.DecimalField("Cheques Locales", max_digits=12, decimal_places=2, blank=True, null=True)
    chequespro = models.DecimalField("Cheques en Proceso", max_digits=12, decimal_places=2, blank=True, null=True)
    saldo = models.DecimalField("Saldo", max_digits=12, decimal_places=2, blank=True, null=True)
    detalle = models.CharField("Detalle", max_length=30, blank=True, null=True)
    tipo_socio = models.CharField("Tipo Socio", max_length=1, blank=True, null=True)
    contabili = models.BooleanField("Contabilizado", blank=True, null=True)
    codigocont = models.CharField("Código Contable", max_length=15, blank=True, null=True)

    objects = AhorroHistorialManager()

    class Meta:
        managed = False
        db_table = 'ahor'
        verbose_name = "Historial de Ahorro"
        verbose_name_plural = "Historiales de Ahorro"

    def __str__(self):
        return f"{self.detalle} - {self.valor} ({self.fecha_tra})"

    def is_ingreso(self) -> bool:
        """Verifica si la transacción es un ingreso"""
        return self.ingre_egre == 'I'

    def is_egreso(self) -> bool:
        """Verifica si la transacción es un egreso"""
        return self.ingre_egre == 'E'

    def get_valor_absoluto(self) -> Decimal:
        """Retorna el valor absoluto de la transacción"""
        return abs(self.valor) if self.valor else Decimal('0.00')

    def get_valor_con_signo(self) -> Decimal:
        """
        Retorna el valor con signo según el tipo de transacción.
        Positivo para ingresos, negativo para egresos.
        """
        valor = self.valor or Decimal('0.00')
        return valor if self.is_ingreso() else -valor


class CertificadoHistorial(models.Model):
    id = models.AutoField(primary_key=True)
    caja = models.CharField("Caja", max_length=2, blank=True, null=True)
    cuenta = models.ForeignKey(Socio, on_delete=models.DO_NOTHING, to_field='cuenta', db_column='cuenta',
                               related_name='certificados_historial')
    fecha_tra = models.DateField("Fecha Transacción", blank=True, null=True)
    hora = models.CharField("Hora", max_length=5, blank=True, null=True)
    num_doc = models.CharField("Número Documento", max_length=11, blank=True, null=True)
    tipo_tra = models.CharField("Tipo Transacción", max_length=4, blank=True, null=True)
    ventani = models.CharField("Ventana", max_length=1, blank=True, null=True)
    valor = models.DecimalField("Valor", max_digits=12, decimal_places=2, blank=True, null=True)
    efectivo = models.DecimalField("Efectivo", max_digits=12, decimal_places=2, blank=True, null=True)
    chequesloc = models.DecimalField("Cheques Locales", max_digits=12, decimal_places=2, blank=True, null=True)
    chequespro = models.DecimalField("Cheques en Proceso", max_digits=12, decimal_places=2, blank=True, null=True)
    saldo = models.DecimalField("Saldo", max_digits=12, decimal_places=2, blank=True, null=True)
    ingre_egre = models.CharField("Ingreso/Egreso", max_length=1, blank=True, null=True)
    detalle = models.CharField("Detalle", max_length=30, blank=True, null=True)
    tipo_socio = models.CharField("Tipo Socio", max_length=1, blank=True, null=True)
    contabili = models.BooleanField("Contabilizado", blank=True, null=True)
    codigocont = models.CharField("Código Contable", max_length=15, blank=True, null=True)

    objects = CertificadoHistorialManager()

    class Meta:
        managed = False
        db_table = 'cert'
        verbose_name = "Historial Certificado"
        verbose_name_plural = "Historial Certificados"

    def __str__(self):
        return f"{self.detalle} - {self.valor} ({self.fecha_tra})"

    def is_ingreso(self) -> bool:
        """Verifica si la transacción es un ingreso"""
        return self.ingre_egre == 'I'

    def is_egreso(self) -> bool:
        """Verifica si la transacción es un egreso"""
        return self.ingre_egre == 'E'

    def get_valor_absoluto(self) -> Decimal:
        """Retorna el valor absoluto de la transacción"""
        return abs(self.valor) if self.valor else Decimal('0.00')

    def get_valor_con_signo(self) -> Decimal:
        """
        Retorna el valor con signo según el tipo de transacción.
        Positivo para ingresos, negativo para egresos.
        """
        valor = self.valor or Decimal('0.00')
        return valor if self.is_ingreso() else -valor


class Credito(models.Model):
    id = models.AutoField(primary_key=True)
    caja = models.CharField("Caja", max_length=2, blank=True, null=True)
    cuenta = models.ForeignKey(Socio, on_delete=models.DO_NOTHING, to_field='cuenta', db_column='cuenta',
                               related_name='creditos')
    num_paga = models.CharField("Número Pago", max_length=8, unique=True)
    num_reci = models.CharField("Número Recibo", max_length=8, blank=True, null=True)
    fech_pres = models.DateField("Fecha Préstamo", blank=True, null=True)
    fechaup = models.DateField("Fecha Actualización", blank=True, null=True)
    cupomaximo = models.DecimalField("Cupo Máximo", max_digits=10, decimal_places=2, blank=True, null=True)
    val_prest = models.DecimalField("Valor Préstamo", max_digits=10, decimal_places=2, blank=True, null=True)
    sal_pre = models.DecimalField("Saldo Préstamo", max_digits=10, decimal_places=2, blank=True, null=True)
    tasa = models.DecimalField("Tasa", max_digits=4, decimal_places=2, blank=True, null=True)
    dias_pla = models.DecimalField("Días Plazo", max_digits=10, decimal_places=0, blank=True, null=True)
    amortiza = models.DecimalField("Amortización", max_digits=10, decimal_places=0, blank=True, null=True)
    cuotas = models.DecimalField("Cuotas", max_digits=10, decimal_places=0, blank=True, null=True)
    cuotaspag = models.DecimalField("Cuotas Pagadas", max_digits=10, decimal_places=0, blank=True, null=True)
    interescp = models.DecimalField("Interés Cuota Pendiente", max_digits=10, decimal_places=2, blank=True, null=True)
    interesmp = models.DecimalField("Interés Mora Pendiente", max_digits=10, decimal_places=2, blank=True, null=True)
    multacrep = models.DecimalField("Multa Crédito", max_digits=10, decimal_places=2, blank=True, null=True)
    interesmor = models.DecimalField("Interés Mora", max_digits=10, decimal_places=4, blank=True, null=True)
    gcobrop = models.DecimalField("Gastos Cobro", max_digits=10, decimal_places=2, blank=True, null=True)
    ahorros = models.DecimalField("Ahorros", max_digits=10, decimal_places=2, blank=True, null=True)
    codigog = models.CharField("Código Grupo", max_length=3, blank=True, null=True)
    codigot = models.CharField("Código Tipo", max_length=3, blank=True, null=True)
    grupo_id = models.CharField("Grupo ID", max_length=3, blank=True, null=True)
    codigod = models.CharField("Código Detalle", max_length=3, blank=True, null=True)
    garante1 = models.CharField("Garante 1", max_length=8, blank=True, null=True)
    garante2 = models.CharField("Garante 2", max_length=8, blank=True, null=True)
    garante3 = models.CharField("Garante 3", max_length=8, blank=True, null=True)
    cedula_ns = models.CharField("Cédula NS 1", max_length=10, blank=True, null=True)
    cedula_ns2 = models.CharField("Cédula NS 2", max_length=10, blank=True, null=True)
    fondomor = models.DecimalField("Fondo Moroso", max_digits=8, decimal_places=2, blank=True, null=True)
    encaje = models.DecimalField("Encaje", max_digits=8, decimal_places=2, blank=True, null=True)
    ahorromes = models.DecimalField("Ahorros Morosos", max_digits=8, decimal_places=2, blank=True, null=True)
    certifica = models.DecimalField("Certificados", max_digits=8, decimal_places=2, blank=True, null=True)
    notificaci = models.IntegerField("Notificaciones", blank=True, null=True)
    linlibreta = models.DecimalField("Línea Libreta", max_digits=10, decimal_places=0, blank=True, null=True)
    detalle = models.TextField("Detalle", blank=True, null=True)
    formapago = models.IntegerField("Forma de Pago", blank=True, null=True)
    procesado = models.BooleanField("Procesado", blank=True, null=True)
    for_entre = models.CharField("For Entrega", max_length=1, blank=True, null=True)
    ctacorrien = models.CharField("Cuenta Corriente", max_length=15, blank=True, null=True)
    chequenum = models.DecimalField("Número Cheque", max_digits=10, decimal_places=0, blank=True, null=True)
    valorchequ = models.DecimalField("Valor Cheque", max_digits=10, decimal_places=2, blank=True, null=True)
    pagado = models.BooleanField("Pagado", blank=True, null=True)
    valornoti = models.DecimalField("Valor Notificación", max_digits=10, decimal_places=2, blank=True, null=True)
    fechaunoti = models.DateField("Fecha Notificación", blank=True, null=True)
    fechajudi = models.DateField("Fecha Judicial", blank=True, null=True)
    fechacasti = models.DateField("Fecha Castigo", blank=True, null=True)
    abogado_id = models.CharField("Abogado ID", max_length=2, blank=True, null=True)
    oficredito = models.CharField("Oficina Crédito", max_length=2, blank=True, null=True)
    judicial = models.BooleanField("Judicial", blank=True, null=True)
    castigada = models.BooleanField("Castigada", blank=True, null=True)
    prorrogado = models.BooleanField("Prorrogado", blank=True, null=True)
    nprorroga = models.DecimalField("Número Prórroga", max_digits=10, decimal_places=0, blank=True, null=True)
    esperadfij = models.DecimalField("Esperar Días Fijos", max_digits=10, decimal_places=0, blank=True, null=True)
    diasespera = models.DecimalField("Días Espera", max_digits=10, decimal_places=0, blank=True, null=True)
    fechainipr = models.DateField("Fecha Inicio Prórroga", blank=True, null=True)
    fechafinpr = models.DateField("Fecha Fin Prórroga", blank=True, null=True)
    causa = models.CharField("Causa", max_length=20, blank=True, null=True)
    acantiguo = models.BooleanField("Antiguo", blank=True, null=True)
    automatico = models.BooleanField("Automático", blank=True, null=True)
    diafijo = models.BooleanField("Día Fijo", blank=True, null=True)
    diapago = models.DecimalField("Día Pago", max_digits=10, decimal_places=0, blank=True, null=True)
    cap_entre = models.DecimalField("Capital Entregado", max_digits=12, decimal_places=2, blank=True, null=True)
    capcomple = models.BooleanField("Capital Completo", blank=True, null=True)
    asegurado = models.BooleanField("Asegurado", blank=True, null=True)
    valseguro = models.DecimalField("Valor Seguro", max_digits=10, decimal_places=2, blank=True, null=True)
    _nullflags = models.TextField(blank=True, null=True)

    objects = CreditoManager()

    class Meta:
        managed = False
        db_table = 'credito'
        verbose_name = "Crédito"
        verbose_name_plural = "Créditos"

    def __str__(self):
        return f"Crédito {self.num_paga} - {self.cuenta}"

    def get_saldo_pendiente(self) -> Decimal:
        """Retorna el saldo pendiente del crédito"""
        return self.sal_pre or Decimal('0.00')

    def get_valor_original(self) -> Decimal:
        """Retorna el valor original del préstamo"""
        return self.val_prest or Decimal('0.00')

    def get_porcentaje_pagado(self) -> Decimal:
        """
        Calcula el porcentaje pagado del crédito.
        Retorna valor entre 0 y 100.
        """
        valor_original = self.get_valor_original()
        if valor_original == 0:
            return Decimal('100.00')

        saldo_pendiente = self.get_saldo_pendiente()
        valor_pagado = valor_original - saldo_pendiente

        return (valor_pagado / valor_original) * Decimal('100')

    def is_active(self) -> bool:
        """Verifica si el crédito está activo"""
        return not self.pagado and self.get_saldo_pendiente() > 0

    def is_overdue(self) -> bool:
        """Verifica si el crédito tiene cuotas vencidas"""
        return self.cuotas_credito.filter(
            Q(pagado=False) | Q(pagado__isnull=True),
            fecha_ven__lt=timezone.now().date()
        ).exists()

    def get_cuotas_pendientes(self):
        """Retorna las cuotas pendientes de pago ordenadas por fecha"""
        return self.cuotas_credito.filter(
            Q(pagado=False) | Q(pagado__isnull=True)
        ).order_by('fecha_ven')

    def get_cuotas_vencidas(self):
        """Retorna las cuotas vencidas"""
        return CreditoCuota.objects.by_credit(self).overdue()

    def get_proxima_cuota(self):
        """Retorna la próxima cuota a vencer"""
        return self.get_cuotas_pendientes().first()

    def get_total_cuotas_pendientes(self) -> Decimal:
        """Calcula el monto total de cuotas pendientes"""
        total = self.get_cuotas_pendientes().aggregate(
            total=Sum('pagar')
        )['total']
        return total or Decimal('0.00')

    def get_dias_mora_maximo(self) -> int:
        """Obtiene los días de mora máximos del crédito"""
        cuota_mas_vencida = self.get_cuotas_vencidas().order_by('fecha_ven').first()
        if not cuota_mas_vencida or not cuota_mas_vencida.fecha_ven:
            return 0

        dias_mora = (timezone.now().date() - cuota_mas_vencida.fecha_ven).days
        return max(0, dias_mora)


class CreditoCuota(models.Model):
    id = models.AutoField(primary_key=True)
    num_paga = models.ForeignKey(Credito, on_delete=models.DO_NOTHING, to_field='num_paga', db_column='num_paga',
                                 related_name='cuotas_credito')
    documento = models.CharField("Documento", max_length=8, blank=True, null=True)
    capital = models.DecimalField("Capital", max_digits=10, decimal_places=2, blank=True, null=True)
    ncuota = models.IntegerField("Número Cuota", blank=True, null=True)
    fecha_ini = models.DateField("Fecha Inicio", blank=True, null=True)
    fecha_ven = models.DateField("Fecha Vencimiento", blank=True, null=True)
    pagar = models.DecimalField("Pagar", max_digits=10, decimal_places=2, blank=True, null=True)
    interes = models.DecimalField("Interés", max_digits=10, decimal_places=2, blank=True, null=True)
    mora = models.DecimalField("Mora", max_digits=10, decimal_places=4, blank=True, null=True)
    ahorros = models.DecimalField("Ahorros", max_digits=10, decimal_places=2, blank=True, null=True)
    certifica = models.DecimalField("Certificados", max_digits=10, decimal_places=2, blank=True, null=True)
    val_notif = models.DecimalField("Valor Notificación", max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_pag = models.DateField("Fecha Pago", blank=True, null=True)
    pagado = models.BooleanField("Pagado", blank=True, null=True)
    gcobro = models.DecimalField("Gastos Cobro", max_digits=10, decimal_places=2, blank=True, null=True)

    objects = CreditoCuotaManager()

    class Meta:
        managed = False
        db_table = 'crecuotaf'
        verbose_name = "Cuota de Crédito"
        verbose_name_plural = "Cuotas de Crédito"

    def __str__(self):
        return f"Cuota {self.ncuota} - Crédito {self.num_paga}"

    def get_monto_cuota(self) -> Decimal:
        """Retorna el monto de la cuota"""
        return self.pagar or Decimal('0.00')

    def is_paid(self) -> bool:
        """Verifica si la cuota está pagada"""
        return self.pagado or False

    def is_overdue(self) -> bool:
        """Verifica si la cuota está vencida"""
        if not self.fecha_ven or self.is_paid():
            return False
        return self.fecha_ven < timezone.now().date()

    def get_days_until_due(self) -> int:
        """
        Obtiene los días hasta el vencimiento.
        Retorna número negativo si ya venció.
        """
        if not self.fecha_ven:
            return 0

        delta = self.fecha_ven - timezone.now().date()
        return delta.days

    def get_days_overdue(self) -> int:
        """
        Obtiene los días de mora.
        Retorna 0 si no está vencida o está pagada.
        """
        if not self.is_overdue():
            return 0

        return abs(self.get_days_until_due())

    def get_status_display(self) -> str:
        """Retorna el estado de la cuota en formato legible"""
        if self.is_paid():
            return "Pagada"
        elif self.is_overdue():
            return f"Vencida ({self.get_days_overdue()} días)"
        else:
            days_until = self.get_days_until_due()
            if days_until <= 7:
                return f"Próxima a vencer ({days_until} días)"
            else:
                return "Vigente"


class CreditoHistorial(models.Model):
    id = models.AutoField(primary_key=True)
    fechatran = models.DateField("Fecha Transacción", blank=True, null=True)
    valor = models.DecimalField("Valor", max_digits=10, decimal_places=2, blank=True, null=True)
    capital = models.DecimalField("Capital", max_digits=10, decimal_places=2, blank=True, null=True)
    interes = models.DecimalField("Interés", max_digits=10, decimal_places=2, blank=True, null=True)
    mora = models.DecimalField("Mora", max_digits=10, decimal_places=2, blank=True, null=True)
    ahorromes = models.DecimalField("Ahorros Morosos", max_digits=8, decimal_places=2, blank=True, null=True)
    certimes = models.DecimalField("Certificados Morosos", max_digits=8, decimal_places=2, blank=True, null=True)
    valornoti = models.DecimalField("Valor Notificación", max_digits=10, decimal_places=2, blank=True, null=True)
    sal_pre = models.DecimalField("Saldo Préstamo", max_digits=10, decimal_places=2, blank=True, null=True)
    num_reci = models.CharField("Número Recibo", max_length=8, blank=True, null=True)
    ingre_egre = models.CharField("Ingreso/Egreso", max_length=1, blank=True, null=True)
    tipo_tra = models.CharField("Tipo Transacción", max_length=4, blank=True, null=True)
    asistencre = models.DecimalField("Asistencia Crédito", max_digits=10, decimal_places=2, blank=True, null=True)
    cuenta = models.ForeignKey(Socio, on_delete=models.DO_NOTHING, to_field='cuenta', db_column='cuenta',
                               related_name='creditos_historial')
    num_paga = models.ForeignKey(Credito, on_delete=models.DO_NOTHING, to_field='num_paga', db_column='num_paga',
                                 related_name='historiales')
    fecha_ini = models.DateField("Fecha Inicio", blank=True, null=True)
    fecha_fin = models.DateField("Fecha Fin", blank=True, null=True)
    efectivo = models.DecimalField("Efectivo", max_digits=10, decimal_places=2, blank=True, null=True)
    bancos = models.DecimalField("Bancos", max_digits=10, decimal_places=2, blank=True, null=True)
    saldo_ante = models.DecimalField("Saldo Anterior", max_digits=10, decimal_places=2, blank=True, null=True)
    int_moraa = models.DecimalField("Interés Mora Antiguo", max_digits=8, decimal_places=2, blank=True, null=True)
    int_corra = models.DecimalField("Interés Corriente", max_digits=8, decimal_places=2, blank=True, null=True)
    ahorros = models.DecimalField("Ahorros", max_digits=8, decimal_places=2, blank=True, null=True)
    certifica = models.DecimalField("Certificados", max_digits=8, decimal_places=2, blank=True, null=True)
    diasmora = models.DecimalField("Días Mora", max_digits=10, decimal_places=0, blank=True, null=True)
    diascobra = models.DecimalField("Días Cobro", max_digits=10, decimal_places=0, blank=True, null=True)
    interescp = models.DecimalField("Interés Cuota Pendiente", max_digits=10, decimal_places=2, blank=True, null=True)
    interesmp = models.DecimalField("Interés Mora Pendiente", max_digits=10, decimal_places=2, blank=True, null=True)
    codigot = models.CharField("Código Tipo", max_length=3, blank=True, null=True)
    codigog = models.CharField("Código Grupo", max_length=3, blank=True, null=True)
    codigod = models.CharField("Código Detalle", max_length=3, blank=True, null=True)
    horatran = models.CharField("Hora Transacción", max_length=5, blank=True, null=True)
    tasa = models.DecimalField("Tasa", max_digits=4, decimal_places=2, blank=True, null=True)
    gcobrop = models.DecimalField("Gastos Cobro", max_digits=4, decimal_places=2, blank=True, null=True)
    encaje = models.DecimalField("Encaje", max_digits=8, decimal_places=2, blank=True, null=True)
    dctoley1 = models.DecimalField("Descuento Ley 1", max_digits=5, decimal_places=2, blank=True, null=True)
    dctoley2 = models.DecimalField("Descuento Ley 2", max_digits=5, decimal_places=2, blank=True, null=True)
    dctoley3 = models.DecimalField("Descuento Ley 3", max_digits=5, decimal_places=2, blank=True, null=True)
    dctoley4 = models.DecimalField("Descuento Ley 4", max_digits=5, decimal_places=2, blank=True, null=True)
    linea = models.DecimalField("Línea", max_digits=10, decimal_places=0, blank=True, null=True)
    caja = models.CharField("Caja", max_length=2, blank=True, null=True)
    contabili = models.BooleanField("Contabilizado", blank=True, null=True)
    multacremo = models.DecimalField("Multa Crédito Moroso", max_digits=10, decimal_places=2, blank=True, null=True)
    ncuotas = models.DecimalField("Número Cuotas", max_digits=10, decimal_places=0, blank=True, null=True)
    coficina_i = models.CharField("Oficina", max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'credit_h'
        verbose_name = "Historial de Crédito"
        verbose_name_plural = "Historiales de Crédito"


class PlazoFijo(models.Model):
    id = models.AutoField(primary_key=True)
    caja = models.CharField("Caja", max_length=2, blank=True, null=True)
    documento = models.CharField("Documento", max_length=8, unique=True)
    fechadepos = models.DateField("Fecha Depósito", blank=True, null=True)
    fechavenci = models.DateField("Fecha Vencimiento", blank=True, null=True)
    cantidad = models.DecimalField("Cantidad", max_digits=12, decimal_places=2, blank=True, null=True)
    tasa_inter = models.DecimalField("Tasa Interés", max_digits=5, decimal_places=3, blank=True, null=True)
    cedula = models.CharField("Cédula", max_length=10, blank=True, null=True)
    cliente = models.CharField("Cliente", max_length=30, blank=True, null=True)
    beneficia = models.CharField("Beneficiario", max_length=40, blank=True, null=True)
    cuenta = models.ForeignKey(Socio, on_delete=models.DO_NOTHING, to_field='cuenta', db_column='cuenta', blank=True,
                               null=True, related_name='plazos_fijos')
    direccion = models.CharField("Dirección", max_length=40, blank=True, null=True)
    parroquia = models.CharField("Parroquia", max_length=3, blank=True, null=True)
    barrio_id = models.CharField("Barrio ID", max_length=3, blank=True, null=True)
    sector_id = models.CharField("Sector ID", max_length=3, blank=True, null=True)
    fecha_naci = models.DateField("Fecha Nacimiento", blank=True, null=True)
    sexo = models.BooleanField("Sexo", blank=True, null=True)
    telefono = models.CharField("Teléfono", max_length=8, blank=True, null=True)
    efectivo = models.DecimalField("Efectivo", max_digits=10, decimal_places=2, blank=True, null=True)
    cheques = models.DecimalField("Cheques", max_digits=10, decimal_places=2, blank=True, null=True)
    plazo = models.DecimalField("Plazo", max_digits=10, decimal_places=0, blank=True, null=True)
    cuotas = models.DecimalField("Cuotas", max_digits=10, decimal_places=0, blank=True, null=True)
    diasintere = models.DecimalField("Días Interés", max_digits=10, decimal_places=0, blank=True, null=True)
    retencion = models.DecimalField("Retención", max_digits=4, decimal_places=2, blank=True, null=True)
    fechaup = models.DateField("Fecha Actualización", blank=True, null=True)
    procesado = models.BooleanField("Procesado", blank=True, null=True)
    pagado = models.BooleanField("Pagado", blank=True, null=True)
    preimpreso = models.BooleanField("Preimpreso", blank=True, null=True)

    objects = PlazoFijoManager()

    class Meta:
        managed = False
        db_table = 'plazo_fi'
        verbose_name = "Plazo Fijo"
        verbose_name_plural = "Plazos Fijos"

    def __str__(self):
        return f"Plazo Fijo {self.documento} - {self.cliente}"

    def get_monto_inversion(self) -> Decimal:
        """Retorna el monto de la inversión"""
        return self.cantidad or Decimal('0.00')

    def is_active(self) -> bool:
        """Verifica si el plazo fijo está activo"""
        return not self.pagado

    def is_matured(self) -> bool:
        """Verifica si el plazo fijo ha vencido"""
        if not self.fechavenci:
            return False
        return self.fechavenci < timezone.now().date()

    def days_to_maturity(self) -> Optional[int]:
        """
        Retorna los días hasta el vencimiento.
        Retorna None si no hay fecha de vencimiento.
        Retorna número negativo si ya venció.
        """
        if not self.fechavenci:
            return None

        today = timezone.now().date()
        delta = self.fechavenci - today
        return delta.days

    def is_maturing_soon(self, days: int = 30) -> bool:
        """Verifica si el plazo fijo vence pronto"""
        days_left = self.days_to_maturity()
        if days_left is None:
            return False
        return 0 <= days_left <= days

    def get_maturity_status(self) -> str:
        """Retorna el estado de vencimiento en formato legible"""
        if not self.is_active():
            return "Pagado"

        days_left = self.days_to_maturity()
        if days_left is None:
            return "Sin fecha de vencimiento"
        elif days_left < 0:
            return f"Vencido ({abs(days_left)} días)"
        elif days_left <= 30:
            return f"Próximo a vencer ({days_left} días)"
        else:
            return "Vigente"

    def calculate_projected_value(self, annual_rate: Decimal) -> Decimal:
        """
        Calcula el valor proyectado al vencimiento.
        Usa interés simple para el cálculo.
        """
        if not self.fechavenci or not self.fechadepos:
            return self.get_monto_inversion()

        principal = self.get_monto_inversion()
        days = (self.fechavenci - self.fechadepos).days

        if days <= 0:
            return principal

        # Interés simple: I = P * r * t
        daily_rate = annual_rate / Decimal('100') / Decimal('365')
        interest = principal * daily_rate * Decimal(str(days))

        return principal + interest


class PlazoFijoPago(models.Model):
    id = models.AutoField(primary_key=True)
    cuota = models.DecimalField("Cuota", max_digits=10, decimal_places=0, blank=True, null=True)
    interes = models.DecimalField("Interés", max_digits=10, decimal_places=2, blank=True, null=True)
    capital = models.DecimalField("Capital", max_digits=12, decimal_places=2, blank=True, null=True)
    fechainici = models.DateField("Fecha Inicio", blank=True, null=True)
    fechapago = models.DateField("Fecha Pago", blank=True, null=True)
    documento = models.ForeignKey(PlazoFijo, on_delete=models.DO_NOTHING, to_field='documento', db_column='documento',
                                  blank=True, null=True, related_name='pagos')

    class Meta:
        managed = False
        db_table = 'pagospf'
        verbose_name = "Pago Plazo Fijo"
        verbose_name_plural = "Pagos Plazo Fijo"


class PlazoFijoHistorial(models.Model):
    id = models.AutoField(primary_key=True)
    fechadepos = models.DateField("Fecha Depósito", blank=True, null=True)
    cuota = models.DecimalField("Cuota", max_digits=10, decimal_places=0, blank=True, null=True)
    cantidad = models.DecimalField("Cantidad", max_digits=12, decimal_places=2, blank=True, null=True)
    interes = models.DecimalField("Interés", max_digits=8, decimal_places=2, blank=True, null=True)
    impuesto = models.DecimalField("Impuesto", max_digits=10, decimal_places=2, blank=True, null=True)
    tipo_tra = models.CharField("Tipo Transacción", max_length=4, blank=True, null=True)
    caja = models.CharField("Caja", max_length=2, blank=True, null=True)
    documento = models.ForeignKey(PlazoFijo, on_delete=models.DO_NOTHING, to_field='documento', db_column='documento',
                                  blank=True, null=True, related_name='historiales')
    efectivo = models.DecimalField("Efectivo", max_digits=10, decimal_places=2, blank=True, null=True)
    cliente = models.CharField("Cliente", max_length=35, blank=True, null=True)
    cuenta = models.ForeignKey(Socio, on_delete=models.DO_NOTHING, to_field='cuenta', db_column='cuenta', blank=True,
                               null=True, related_name='plazos_fijos_historial')
    cheques = models.DecimalField("Cheques", max_digits=10, decimal_places=2, blank=True, null=True)
    hora = models.CharField("Hora", max_length=10, blank=True, null=True)
    contabili = models.BooleanField("Contabilizado", blank=True, null=True)
    estable = models.CharField("Establecimiento", max_length=3, blank=True, null=True)
    ptoventa = models.CharField("Punto de Venta", max_length=3, blank=True, null=True)
    nretencion = models.CharField("Número Retención", max_length=7, blank=True, null=True)
    autoriza = models.CharField("Autoriza", max_length=10, blank=True, null=True)
    capital = models.DecimalField("Capital", max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plazo_h'
        verbose_name = "Historial Plazo Fijo"
        verbose_name_plural = "Historiales Plazo Fijo"
