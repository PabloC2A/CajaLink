# legacy_models/choices.py

from django.db import models


class SocioAreaChoices(models.TextChoices):
    """
    Opciones para el campo 'área' del modelo Socio.
    Basado en datos reales: [1, 2]
    """
    AREA_1 = '1', 'Área 1'
    AREA_2 = '2', 'Área 2'


class SocioTipoChoices(models.TextChoices):
    """
    Opciones para el campo 'tipo' del modelo Socio.
    Basado en datos reales: [1]
    Nota: Solo se encontró valor '1' en los datos actuales.
    """
    TIPO_1 = '1', 'Tipo 1'


class SocioSexoChoices(models.TextChoices):
    """
    Opciones para el campo 'sexo' del modelo Socio.
    Nota: En el modelo legacy es BooleanField, pero se encontró valor '.T.' (True)
    que representa valores booleanos en sistemas legacy.
    """
    MASCULINO = True, 'Masculino'
    FEMENINO = False, 'Femenino'


class EstadoCivilChoices(models.TextChoices):
    """
    Opciones para el campo 'esta_civil' del modelo Socio.
    Basado en datos reales: [Casado, Divorciado, Soltero, Union Libre, Viudo]
    """
    SOLTERO = 'Soltero', 'Soltero'
    CASADO = 'Casado', 'Casado'
    DIVORCIADO = 'Divorciado', 'Divorciado'
    UNION_LIBRE = 'Union Libre', 'Unión Libre'
    VIUDO = 'Viudo', 'Viudo'


class TipoSangreChoices(models.TextChoices):
    """
    Opciones para el campo 'tipo_sang' del modelo Socio.
    Basado en datos reales con normalización de inconsistencias:
    [+, 0+, O+, OH+, OR +, OR H, OR+, ORH*, ORH+, Or +, PRH+, ohr+, or h, orh+]
    Nota: Los datos legacy tienen inconsistencias de formato que se normalizan aquí.
    """
    # Tipos de sangre normalizados
    O_POSITIVO = 'O+', 'O+'
    O_NEGATIVO = 'O-', 'O-'
    A_POSITIVO = 'A+', 'A+'
    A_NEGATIVO = 'A-', 'A-'
    B_POSITIVO = 'B+', 'B+'
    B_NEGATIVO = 'B-', 'B-'
    AB_POSITIVO = 'AB+', 'AB+'
    AB_NEGATIVO = 'AB-', 'AB-'

    # Valores legacy para compatibilidad con datos inconsistentes
    LEGACY_PLUS = '+', '+ (Legacy)'
    LEGACY_0_PLUS = '0+', '0+ (Legacy)'
    LEGACY_OH_PLUS = 'OH+', 'OH+ (Legacy)'
    LEGACY_OR_PLUS = 'OR+', 'OR+ (Legacy)'
    LEGACY_OR_SPACE_PLUS = 'OR +', 'OR + (Legacy)'
    LEGACY_OR_H = 'OR H', 'OR H (Legacy)'
    LEGACY_ORH_ASTERISK = 'ORH*', 'ORH* (Legacy)'
    LEGACY_ORH_PLUS = 'ORH+', 'ORH+ (Legacy)'
    LEGACY_OR_LOWER_PLUS = 'Or +', 'Or + (Legacy)'
    LEGACY_PRH_PLUS = 'PRH+', 'PRH+ (Legacy)'
    LEGACY_OHR_LOWER_PLUS = 'ohr+', 'ohr+ (Legacy)'
    LEGACY_OR_LOWER_H = 'or h', 'or h (Legacy)'
    LEGACY_ORH_LOWER_PLUS = 'orh+', 'orh+ (Legacy)'


class InstruccionChoices(models.TextChoices):
    """
    Opciones para el campo 'instrucc' del modelo Socio.
    Basado en datos reales: [Primaria, Secundaria, Superior, Tecnólogo]
    Nota: 'Tecnólogo' aparece con caracteres especiales en los datos legacy.
    """
    PRIMARIA = 'Primaria', 'Primaria'
    SECUNDARIA = 'Secundaria', 'Secundaria'
    SUPERIOR = 'Superior', 'Superior'
    TECNOLOGO = 'Tecnólogo', 'Tecnólogo'


class SocioEstadoChoices(models.TextChoices):
    """
    Opciones para el campo 'estado' del modelo Socio.
    Basado en datos reales: [.T.] (formato legacy de boolean True)
    Nota: .T. y .F. son valores booleanos en sistemas legacy (dBase/FoxPro)
    """
    ACTIVO = '.T.', 'Activo'
    INACTIVO = '.F.', 'Inactivo'


class SocioCerradoChoices(models.TextChoices):
    """
    Opciones para el campo 'cerrado' del modelo Socio.
    Basado en datos reales: [.T.] (formato legacy de boolean)
    """
    CERRADO = '.T.', 'Cerrado'
    ABIERTO = '.F.', 'Abierto'


# === CHOICES COMUNES PARA HISTORIAL DE TRANSACCIONES ===

class IngresoEgresoChoices(models.TextChoices):
    """
    Opciones para campos 'ingre_egre' en modelos de historial.
    Aplicable a AhorroHistorial, CertificadoHistorial, CreditoHistorial.
    """
    INGRESO = 'I', 'Ingreso'
    EGRESO = 'E', 'Egreso'


class SocioNuevoChoices(models.TextChoices):
    """
    Opciones para el campo 'nuevo' del modelo Socio.
    Nota: En el modelo legacy es BooleanField.
    """
    NUEVO = True, 'Nuevo'
    EXISTENTE = False, 'Existente'


class MorosoChoices(models.TextChoices):
    """
    Opciones para el campo 'moroso' del modelo Socio.
    Nota: En el modelo legacy es BooleanField.
    """
    MOROSO = True, 'Moroso'
    NO_MOROSO = False, 'No Moroso'


class ContabilizadoChoices(models.TextChoices):
    """
    Opciones para el campo 'contabili' en modelos de historial.
    Nota: En el modelo legacy es BooleanField.
    """
    CONTABILIZADO = True, 'Contabilizado'
    NO_CONTABILIZADO = False, 'No Contabilizado'


# === CHOICES PARA OTROS MODELOS ===

class ModalidadCreditoChoices(models.TextChoices):
    """
    Opciones para el campo 'modalidad' en Credito.
    Modalidades comunes de crédito en cooperativas.
    """
    CONSUMO = 'CON', 'Consumo'
    VIVIENDA = 'VIV', 'Vivienda'
    VEHICULO = 'VEH', 'Vehículo'
    EDUCATIVO = 'EDU', 'Educativo'
    COMERCIAL = 'COM', 'Comercial'
    EMERGENCIA = 'EME', 'Emergencia'
    REFINANCIACION = 'REF', 'Refinanciación'
    MICROEMPRESARIAL = 'MIC', 'Microempresarial'


class EstadoCreditoChoices(models.TextChoices):
    """
    Opciones para el campo 'estado' en Credito.
    Estados posibles de un crédito en el ciclo de vida.
    """
    VIGENTE = 'V', 'Vigente'
    CANCELADO = 'C', 'Cancelado'
    VENCIDO = 'X', 'Vencido'
    CASTIGADO = 'K', 'Castigado'
    JUDICIAL = 'J', 'Judicial'
    REESTRUCTURADO = 'R', 'Reestructurado'
    APROBADO = 'A', 'Aprobado'
    DESEMBOLSADO = 'D', 'Desembolsado'


class TipoCreditoChoices(models.TextChoices):
    """
    Opciones para el campo 'tipo_cre' en Credito.
    Tipos de crédito según clasificación interna.
    """
    ORDINARIO = 'ORD', 'Ordinario'
    ESPECIAL = 'ESP', 'Especial'
    EMERGENCIA = 'EME', 'Emergencia'
    CALAMIDAD = 'CAL', 'Calamidad'
    REESTRUCTURADO = 'REE', 'Reestructurado'
    MICROEMPRESARIAL = 'MIC', 'Microempresarial'


class JudicialChoices(models.TextChoices):
    """
    Opciones para el campo 'judicial' en Credito.
    Nota: En el modelo legacy es BooleanField.
    """
    EN_PROCESO_JUDICIAL = True, 'En Proceso Judicial'
    SIN_PROCESO_JUDICIAL = False, 'Sin Proceso Judicial'


class TipoTransaccionChoices(models.TextChoices):
    """
    Opciones para el campo 'tipo_tra' común en todos los modelos de historial legacy.
    Basado en archivo ctacontable.CSV real del sistema.
    Campo unificado usado en: AhorroHistorial, CertificadoHistorial, CreditoHistorial, etc.
    """
    # === AHORROS (AH) ===
    # Depósitos/Ingresos
    DEAH = 'DEAH', 'Depósito de Ahorros Socios'
    DEFM = 'DEFM', 'Depósito Fondo Mortuorio'
    INGR = 'INGR', 'Cuota de Ingreso'
    OING = 'OING', 'Otros Ingresos'
    INAH = 'INAH', 'Pago interés Ahorros'
    INLA = 'INLA', 'Interés Ahorros cierre cuenta'

    # Retiros/Egresos
    REAH = 'REAH', 'Retiro de Ahorros'
    RCHA = 'RCHA', 'Retiro cheque Ahorros Socios'

    # Notas contables
    NCAH = 'NCAH', 'Nota de crédito Ahorros'
    NDAH = 'NDAH', 'Notas de Débito de Ahorros'
    ACCT = 'ACCT', 'N/C por emisión de crédito'

    # Transferencias
    AHCE = 'AHCE', 'Ahorros a Certificados'
    AHPA = 'AHPA', 'Ahorro a pago Créditos'
    AHFM = 'AHFM', 'Ahorros a Fondo Mortuorio'

    # === CERTIFICADOS (CE) ===
    # Depósitos/Ingresos
    DECE = 'DECE', 'Depósitos de Certificados'
    DEED = 'DEED', 'Depósito Certificados Edificio'
    INCE = 'INCE', 'Pago intereses Certificados'
    INLC = 'INLC', 'Interés Certificados liquidación cuenta'

    # Retiros/Egresos
    RECE = 'RECE', 'Retiro de Certificados'

    # Notas contables
    NCCE = 'NCCE', 'Notas de crédito Certificados'
    NDCE = 'NDCE', 'Notas de Débito de C.AP.'

    # Transferencias
    CEHA = 'CEHA', 'Certificados desde Ahorros'
    CEPA = 'CEPA', 'Certificados a Pago de Crédito'

    # === CLIENTES (CL) ===
    # Depósitos/Ingresos
    DECL = 'DECL', 'Deposito Ahorros Cuentas Especiales'
    INCL = 'INCL', 'Pago intereses clientes'

    # Retiros/Egresos
    RECL = 'RECL', 'Retiro ahorros clientes'
    RCHC = 'RCHC', 'Retiro Cheques Cuenta Ahorristas'

    # Notas contables
    NCCL = 'NCCL', 'Notas de crédito a Clientes'
    NDCL = 'NDCL', 'Notas de débito a Clientes'

    # === PLAZO FIJO (PF) ===
    # Depósitos/Ingresos
    DEPF = 'DEPF', 'Depósitos a Plazo Fijo'

    # Pagos/Egresos
    PAPF = 'PAPF', 'Pago Plazo Fijo'
    INPF = 'INPF', 'Interés Plazo Fijo'
    INRF = 'INRF', 'Retención Fuente'

    # === CARTERA/CRÉDITOS (CA) ===
    # Cobros/Ingresos
    PACR = 'PACR', 'Cobros de Créditos'


class GrupoTransaccionChoices(models.TextChoices):
    """
    Opciones para clasificar grupos de transacciones.
    Basado en archivo ctacontable.CSV.
    """
    AHORROS = 'AH', 'Ahorros'
    CERTIFICADOS = 'CE', 'Certificados'
    CLIENTES = 'CL', 'Clientes'
    PLAZO_FIJO = 'PF', 'Plazo Fijo'
    CARTERA_CREDITOS = 'CA', 'Cartera/Créditos'


class FuenteTransaccionChoices(models.TextChoices):
    """
    Opciones para el campo 'fuente' en transacciones.
    Basado en archivo ctacontable.CSV.
    """
    VENTANILLA = 'V', 'Ventanilla'
    TRANSFERENCIA = 'T', 'Transferencia'


class TipoTransaccionGeneralChoices(models.TextChoices):
    """
    Todos los tipos de transacción del sistema legacy.
    Basado en archivo ctacontable.CSV real.
    Para uso general cuando se requiere una lista completa.
    """
    # === AHORROS (AH) ===
    # Ingresos
    DEAH = 'DEAH', 'Depósito de Ahorros Socios'
    DEFM = 'DEFM', 'Depósito Fondo Mortuorio'
    INGR = 'INGR', 'Cuota de Ingreso'
    OING = 'OING', 'Otros Ingresos'
    NCAH = 'NCAH', 'Nota de crédito Ahorros'
    ACCT = 'ACCT', 'N/C por emisión de crédito'
    INAH = 'INAH', 'Pago interés Ahorros'
    INLA = 'INLA', 'Interés Ahorros cierre cuenta'

    # Egresos
    REAH = 'REAH', 'Retiro de Ahorros'
    RCHA = 'RCHA', 'Retiro cheque Ahorros Socios'
    NDAH = 'NDAH', 'Notas de Débito de Ahorros'
    AHCE = 'AHCE', 'Ahorros a Certificados'
    AHPA = 'AHPA', 'Ahorro a pago Créditos'
    AHFM = 'AHFM', 'Ahorros a Fondo Mortuorio'

    # === CERTIFICADOS (CE) ===
    # Ingresos
    DECE = 'DECE', 'Depósitos de Certificados'
    DEED = 'DEED', 'Depósito Certificados Edificio'
    NCCE = 'NCCE', 'Notas de crédito Certificados'
    INCE = 'INCE', 'Pago intereses Certificados'
    INLC = 'INLC', 'Interés Certificados liquidación cuenta'

    # Egresos
    RECE = 'RECE', 'Retiro de Certificados'
    NDCE = 'NDCE', 'Notas de Débito de C.AP.'
    CEHA = 'CEHA', 'Certificados desde Ahorros'
    CEPA = 'CEPA', 'Certificados a Pago de Crédito'

    # === CLIENTES (CL) ===
    # Ingresos
    DECL = 'DECL', 'Deposito Ahorros Cuentas Especiales'
    NCCL = 'NCCL', 'Notas de crédito a Clientes'
    NDCL = 'NDCL', 'Notas de débito a Clientes'
    INCL = 'INCL', 'Pago intereses clientes'

    # Egresos
    RECL = 'RECL', 'Retiro ahorros clientes'
    RCHC = 'RCHC', 'Retiro Cheques Cuenta Ahorristas'

    # === PLAZO FIJO (PF) ===
    # Ingresos
    DEPF = 'DEPF', 'Depósitos a Plazo Fijo'

    # Egresos
    PAPF = 'PAPF', 'Pago Plazo Fijo'
    INPF = 'INPF', 'Interés Plazo Fijo'
    INRF = 'INRF', 'Retención Fuente'

    # === CARTERA/CRÉDITOS (CA) ===
    # Ingresos
    PACR = 'PACR', 'Cobros de Créditos'


# === CHOICES PARA OTROS MODELOS ===

class PagoEstadoChoices(models.TextChoices):
    """
    Opciones para campos 'pagado' en modelos.
    Nota: Para campos BooleanField legacy, estas son las opciones conceptuales.
    """
    PAGADO = True, 'Pagado'
    PENDIENTE = False, 'Pendiente'


class ModalidadCreditoChoices(models.TextChoices):
    """
    Opciones para el campo 'modalidad' en Credito.
    """
    CONSUMO = 'CON', 'Consumo'
    VIVIENDA = 'VIV', 'Vivienda'
    VEHICULO = 'VEH', 'Vehículo'
    EDUCATIVO = 'EDU', 'Educativo'
    COMERCIAL = 'COM', 'Comercial'
    EMERGENCIA = 'EME', 'Emergencia'
    REFINANCIACION = 'REF', 'Refinanciación'


class EstadoCreditoChoices(models.TextChoices):
    """
    Opciones para el campo 'estado' en Credito.
    """
    VIGENTE = 'V', 'Vigente'
    CANCELADO = 'C', 'Cancelado'
    VENCIDO = 'X', 'Vencido'
    CASTIGADO = 'K', 'Castigado'
    JUDICIAL = 'J', 'Judicial'
    REESTRUCTURADO = 'R', 'Reestructurado'


class TipoCreditoChoices(models.TextChoices):
    """
    Opciones para el campo 'tipo_cre' en Credito.
    """
    ORDINARIO = 'ORD', 'Ordinario'
    ESPECIAL = 'ESP', 'Especial'
    EMERGENCIA = 'EME', 'Emergencia'
    CALAMIDAD = 'CAL', 'Calamidad'
    REESTRUCTURADO = 'REE', 'Reestructurado'


class IngresoEgresoChoices(models.TextChoices):
    """
    Opciones para campos 'ingre_egre' en modelos de historial.
    Aplicable a AhorroHistorial, CertificadoHistorial, CreditoHistorial.
    """
    INGRESO = 'I', 'Ingreso'
    EGRESO = 'E', 'Egreso'


class TipoTransaccionAhorroChoices(models.TextChoices):
    """
    Opciones para el campo 'tipo_tra' en AhorroHistorial.
    Tipos comunes de transacciones en ahorros.
    """
    DEPOSITO = 'DEP', 'Depósito'
    RETIRO = 'RET', 'Retiro'
    TRANSFERENCIA = 'TRA', 'Transferencia'
    INTERES = 'INT', 'Interés'
    COMISION = 'COM', 'Comisión'
    AJUSTE = 'AJU', 'Ajuste'
    REVERSION = 'REV', 'Reversión'


class TipoTransaccionCertificadoChoices(models.TextChoices):
    """
    Opciones para el campo 'tipo_tra' en CertificadoHistorial.
    Tipos comunes de transacciones en certificados.
    """
    COMPRA = 'COM', 'Compra'
    VENTA = 'VEN', 'Venta'
    INTERES = 'INT', 'Interés'
    RENOVACION = 'REN', 'Renovación'
    VENCIMIENTO = 'VTO', 'Vencimiento'
    AJUSTE = 'AJU', 'Ajuste'
    REVERSION = 'REV', 'Reversión'


class TipoTransaccionCreditoChoices(models.TextChoices):
    """
    Opciones para el campo 'tipo_tra' en CreditoHistorial.
    Tipos comunes de transacciones en créditos.
    """
    PAGO_CUOTA = 'PCU', 'Pago Cuota'
    PAGO_CAPITAL = 'PCA', 'Pago Capital'
    PAGO_INTERES = 'PIN', 'Pago Interés'
    PAGO_MORA = 'PMO', 'Pago Mora'
    DESEMBOLSO = 'DES', 'Desembolso'
    REFINANCIACION = 'REF', 'Refinanciación'
    CASTIGO = 'CAS', 'Castigo'
    AJUSTE = 'AJU', 'Ajuste'
    REVERSION = 'REV', 'Reversión'


class VentanaChoices(models.TextChoices):
    """
    Opciones para el campo 'ventani' en modelos de historial.
    Representa las ventanillas o puntos de atención.
    """
    VENTANA_1 = '1', 'Ventana 1'
    VENTANA_2 = '2', 'Ventana 2'
    VENTANA_3 = '3', 'Ventana 3'
    VENTANA_4 = '4', 'Ventana 4'
    VENTANA_5 = '5', 'Ventana 5'
    AUTOMATICA = 'A', 'Automática'
    SISTEMA = 'S', 'Sistema'


class CajaChoices(models.TextChoices):
    """
    Opciones para el campo 'caja' en modelos de historial.
    """
    CAJA_1 = '01', 'Caja 1'
    CAJA_2 = '02', 'Caja 2'
    CAJA_3 = '03', 'Caja 3'
    CAJA_4 = '04', 'Caja 4'
    CAJA_5 = '05', 'Caja 5'
    CAJA_PRINCIPAL = '00', 'Caja Principal'
    SISTEMA = 'SY', 'Sistema'


class PagoEstadoChoices(models.TextChoices):
    """
    Opciones para campos 'pagado' en modelos.
    Nota: Para campos BooleanField legacy, estas son las opciones conceptuales.
    """
    PAGADO = True, 'Pagado'
    PENDIENTE = False, 'Pendiente'


class OcupacionChoices(models.TextChoices):
    """
    Opciones para el campo 'ocupa_id' del modelo Socio.
    Códigos de ocupación comunes en instituciones públicas.
    """
    ADMINISTRATIVO = '01', 'Administrativo'
    DOCENTE = '02', 'Docente'
    MEDICO = '03', 'Médico'
    ENFERMERO = '04', 'Enfermero'
    TECNICO = '05', 'Técnico'
    OBRERO = '06', 'Obrero'
    DIRECTIVO = '07', 'Directivo'
    CONTADOR = '08', 'Contador'
    ABOGADO = '09', 'Abogado'
    INGENIERO = '10', 'Ingeniero'
    OTROS = '99', 'Otros'


class DNChoices(models.TextChoices):
    """
    Opciones para el campo 'dnc' del modelo Socio.
    Posibles códigos de clasificación interna.
    """
    NORMAL = '01', 'Normal'
    ESPECIAL = '02', 'Especial'
    VIP = '03', 'VIP'
    PROBLEMÁTICO = '04', 'Problemático'


class FuncionChoices(models.TextChoices):
    """
    Opciones para campos 'funcion1' y 'funcion2' del modelo Socio.
    Funciones o roles dentro de la cooperativa.
    """
    SOCIO = 'SOCIO', 'Socio'
    AVALISTA = 'AVALISTA', 'Avalista'
    CODEUDOR = 'CODEUDOR', 'Codeudor'
    FIADOR = 'FIADOR', 'Fiador'
    GARANTE = 'GARANTE', 'Garante'
    BENEFICIARIO = 'BENEFICIARIO', 'Beneficiario'
    APODERADO = 'APODERADO', 'Apoderado'


# === CHOICES PARA OTROS MODELOS ===

class ModalidadCreditoChoices(models.TextChoices):
    """
    Opciones para el campo 'modalidad' en Credito.
    """
    CONSUMO = 'CON', 'Consumo'
    VIVIENDA = 'VIV', 'Vivienda'
    VEHICULO = 'VEH', 'Vehículo'
    EDUCATIVO = 'EDU', 'Educativo'
    COMERCIAL = 'COM', 'Comercial'
    EMERGENCIA = 'EME', 'Emergencia'
    REFINANCIACION = 'REF', 'Refinanciación'


class EstadoCreditoChoices(models.TextChoices):
    """
    Opciones para el campo 'estado' en Credito.
    """
    VIGENTE = 'V', 'Vigente'
    CANCELADO = 'C', 'Cancelado'
    VENCIDO = 'X', 'Vencido'
    CASTIGADO = 'K', 'Castigado'
    JUDICIAL = 'J', 'Judicial'
    REESTRUCTURADO = 'R', 'Reestructurado'


class TipoCreditoChoices(models.TextChoices):
    """
    Opciones para el campo 'tipo_cre' en Credito.
    """
    ORDINARIO = 'ORD', 'Ordinario'
    ESPECIAL = 'ESP', 'Especial'
    EMERGENCIA = 'EME', 'Emergencia'
    CALAMIDAD = 'CAL', 'Calamidad'
    REESTRUCTURADO = 'REE', 'Reestructurado'
