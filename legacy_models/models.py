# legacy_models/models.py

from django.db import models


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
    linlibcert = models.DecimalField("Línea Libreta Certificado", max_digits=10, decimal_places=0, blank=True,null=True)
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

    class Meta:
        managed = False
        db_table = 'socios'
        verbose_name = "Socio (Legacy)"
        verbose_name_plural = "Socios (Legacy)"

    def __str__(self):
        return f"{self.cuenta} - {self.nombres} {self.apellidos}"


class AhorroHistorial(models.Model):
    id = models.AutoField(primary_key=True)
    cuenta = models.ForeignKey(Socio, on_delete=models.DO_NOTHING, to_field='cuenta', db_column='cuenta',related_name='ahorros_historial')
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

    class Meta:
        managed = False
        db_table = 'ahor'
        verbose_name = "Historial Ahorro"
        verbose_name_plural = "Historial Ahorros"

    def __str__(self):
        return f"Transacción {self.num_trans} - Cuenta {self.cuenta.cuenta}"


class CertificadoHistorial(models.Model):
    id = models.AutoField(primary_key=True)
    caja = models.CharField("Caja", max_length=2, blank=True, null=True)
    cuenta = models.ForeignKey(Socio, on_delete=models.DO_NOTHING, to_field='cuenta', db_column='cuenta', related_name='certificados_historial')
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

    class Meta:
        managed = False
        db_table = 'cert'
        verbose_name = "Historial Certificado"
        verbose_name_plural = "Historial Certificados"


class Credito(models.Model):
    id = models.AutoField(primary_key=True)
    caja = models.CharField("Caja", max_length=2, blank=True, null=True)
    cuenta = models.ForeignKey(Socio, on_delete=models.DO_NOTHING, to_field='cuenta', db_column='cuenta',related_name='creditos')
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

    class Meta:
        managed = False
        db_table = 'credito'
        verbose_name = "Crédito"
        verbose_name_plural = "Créditos"

    def __str__(self):
        return f"Crédito {self.num_paga} - Cuenta {self.cuenta.cuenta}"


class CreditoCuota(models.Model):
    id = models.AutoField(primary_key=True)
    num_paga = models.ForeignKey(Credito, on_delete=models.DO_NOTHING, to_field='num_paga', db_column='num_paga', related_name='cuotas_credito')
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

    class Meta:
        managed = False
        db_table = 'crecuotaf'
        verbose_name = "Cuota de Crédito"
        verbose_name_plural = "Cuotas de Crédito"


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
    cuenta = models.ForeignKey(Socio, on_delete=models.DO_NOTHING, to_field='cuenta', db_column='cuenta', related_name='creditos_historial')
    num_paga = models.ForeignKey(Credito, on_delete=models.DO_NOTHING, to_field='num_paga', db_column='num_paga', related_name='historiales')
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
    cuenta = models.ForeignKey(Socio, on_delete=models.DO_NOTHING, to_field='cuenta', db_column='cuenta', blank=True, null=True, related_name='plazos_fijos')
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

    class Meta:
        managed = False
        db_table = 'plazo_fi'
        verbose_name = "Plazo Fijo"
        verbose_name_plural = "Plazos Fijos"


class PlazoFijoPago(models.Model):
    id = models.AutoField(primary_key=True)
    cuota = models.DecimalField("Cuota", max_digits=10, decimal_places=0, blank=True, null=True)
    interes = models.DecimalField("Interés", max_digits=10, decimal_places=2, blank=True, null=True)
    capital = models.DecimalField("Capital", max_digits=12, decimal_places=2, blank=True, null=True)
    fechainici = models.DateField("Fecha Inicio", blank=True, null=True)
    fechapago = models.DateField("Fecha Pago", blank=True, null=True)
    documento = models.ForeignKey(PlazoFijo, on_delete=models.DO_NOTHING, to_field='documento', db_column='documento', blank=True, null=True, related_name='pagos')

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
    documento = models.ForeignKey(PlazoFijo, on_delete=models.DO_NOTHING, to_field='documento', db_column='documento',blank=True, null=True, related_name='historiales')
    efectivo = models.DecimalField("Efectivo", max_digits=10, decimal_places=2, blank=True, null=True)
    cliente = models.CharField("Cliente", max_length=35, blank=True, null=True)
    cuenta = models.ForeignKey(Socio, on_delete=models.DO_NOTHING, to_field='cuenta', db_column='cuenta', blank=True, null=True, related_name='plazos_fijos_historial')
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
