# legacy_models/admin.py

from django.contrib import admin
from . import models


@admin.register(models.Socio)
class SocioAdmin(admin.ModelAdmin):
    """
    Interfaz de administración para el modelo Socio.
    """
    list_display = ('cuenta', 'nombres', 'apellidos', 'cedula', 'email', 'estado')
    search_fields = ('cuenta', 'nombres', 'apellidos', 'cedula')
    list_filter = ('estado', 'cerrado', 'moroso')


@admin.register(models.Credito)
class CreditoAdmin(admin.ModelAdmin):
    """
    Interfaz de administración para el modelo Credito.
    """
    list_display = ('num_paga', 'cuenta', 'fech_pres', 'val_prest', 'sal_pre', 'pagado')
    search_fields = ('num_paga', 'cuenta__cuenta', 'cuenta__cedula')
    list_filter = ('pagado', 'judicial', 'castigada')
    raw_id_fields = ('cuenta',)
    date_hierarchy = 'fech_pres'


@admin.register(models.PlazoFijo)
class PlazoFijoAdmin(admin.ModelAdmin):
    """
    Interfaz de administración para el modelo PlazoFijo.
    """
    list_display = ('documento', 'cliente', 'cedula', 'cantidad', 'fechadepos', 'fechavenci', 'pagado')
    search_fields = ('documento', 'cliente', 'cedula', 'cuenta__cuenta')
    list_filter = ('pagado',)
    raw_id_fields = ('cuenta',)
    date_hierarchy = 'fechadepos'


@admin.register(models.AhorroHistorial)
class AhorroHistorialAdmin(admin.ModelAdmin):
    """
    Interfaz de administración para el historial de ahorros.
    """
    list_display = ('fecha_tra', 'hora', 'detalle', 'valor', 'ingre_egre', 'cuenta')
    search_fields = ('detalle', 'cuenta__cuenta')
    list_filter = ('fecha_tra',)
    raw_id_fields = ('cuenta',)
    date_hierarchy = 'fecha_tra'


@admin.register(models.CertificadoHistorial)
class CertificadoHistorialAdmin(admin.ModelAdmin):
    """
    Interfaz de administración para el historial de certificados.
    """
    list_display = ('fecha_tra', 'hora', 'detalle', 'valor', 'ingre_egre', 'cuenta')
    search_fields = ('detalle', 'cuenta__cuenta')
    list_filter = ('fecha_tra',)
    raw_id_fields = ('cuenta',)
    date_hierarchy = 'fecha_tra'


@admin.register(models.CreditoCuota)
class CreditoCuotaAdmin(admin.ModelAdmin):
    """
    Interfaz de administración para las cuotas de crédito.
    """
    list_display = ('num_paga', 'ncuota', 'fecha_ven', 'pagar', 'pagado')
    search_fields = ('num_paga__num_paga',)
    list_filter = ('pagado', 'fecha_ven')
    raw_id_fields = ('num_paga',)


# Se registran los modelos restantes con su configuración por defecto
# para que sean visibles en el admin.
admin.site.register(models.CreditoHistorial)
admin.site.register(models.PlazoFijoPago)
admin.site.register(models.PlazoFijoHistorial)
