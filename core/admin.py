# core/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.core.cache import cache
from .models import CompanyConfiguration


@admin.register(CompanyConfiguration)
class CompanyConfigurationAdmin(admin.ModelAdmin):
    """
    Administración de configuraciones de empresa.
    Implementa una interfaz clara y funcional para gestionar subdominios.
    """

    list_display = [
        'company_name', 'subdomain', 'is_active',
        'logo_preview', 'color_preview', 'updated_at'
    ]
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['company_name', 'subdomain', 'email']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']

    fieldsets = (
        ('Información Básica', {
            'fields': ('subdomain', 'company_name', 'short_name', 'is_active')
        }),
        ('Configuración Visual', {
            'fields': ('logo', 'primary_color', 'secondary_color'),
            'classes': ('collapse',)
        }),
        ('Información de Contacto', {
            'fields': ('email', 'phone', 'address', 'website'),
            'classes': ('collapse',)
        }),
        ('Textos Personalizados', {
            'fields': ('site_title', 'welcome_message', 'footer_text'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def logo_preview(self, obj):
        """Muestra una vista previa del logo en la lista."""
        if obj.logo:
            return format_html(
                '<img src="{}" width="50" height="30" style="object-fit: contain;" />',
                obj.logo.url
            )
        return "Sin logo"

    logo_preview.short_description = "Logo"

    def color_preview(self, obj):
        """Muestra una vista previa de los colores."""
        return format_html(
            '<div style="display: flex; gap: 5px;">'
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>'
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>'
            '</div>',
            obj.primary_color,
            obj.secondary_color
        )

    color_preview.short_description = "Colores"

    def save_model(self, request, obj, form, change):
        """
        Sobrescribe el guardado para limpiar cache cuando se modifica una configuración.
        """
        super().save_model(request, obj, form, change)

        # Limpiar cache de la configuración modificada
        cache_key = f'company_config:{obj.subdomain}'
        cache.delete(cache_key)

        # Mensaje de éxito personalizado
        if change:
            self.message_user(request, f'Configuración para {obj.company_name} actualizada. Cache limpiado.')
        else:
            self.message_user(request, f'Nueva configuración para {obj.company_name} creada.')

    def delete_model(self, request, obj):
        """Limpia cache al eliminar una configuración."""
        cache_key = f'company_config:{obj.subdomain}'
        cache.delete(cache_key)
        super().delete_model(request, obj)

    def get_queryset(self, request):
        """Optimiza consultas añadiendo select_related si fuera necesario."""
        return super().get_queryset(request).order_by('-updated_at')

    class Media:
        """Añade estilos CSS personalizados al admin."""
        css = {
            'all': ('admin/css/company_config.css',)
        }
        js = ('admin/js/color_picker.js',)
