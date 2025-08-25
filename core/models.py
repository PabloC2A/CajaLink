# core/models.py

from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class CompanyConfiguration(models.Model):
    """
    Modelo para almacenar configuraciones específicas de empresas por subdominio.
    Permite personalizar títulos, información de contacto, colores y logos.
    """

    # Identificación y configuración básica
    subdomain = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Subdominio sin el dominio principal (ej: cajacomunalsantiago)"
    )
    company_name = models.CharField(
        max_length=200,
        help_text="Nombre completo de la empresa"
    )
    short_name = models.CharField(
        max_length=50,
        help_text="Nombre corto para encabezados y títulos"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indica si la configuración está activa"
    )

    # Información de contacto
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Email principal de contacto"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Teléfono principal"
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Dirección física completa"
    )
    website = models.URLField(
        blank=True,
        null=True,
        help_text="Sitio web oficial de la empresa"
    )

    # Personalización visual
    logo = models.ImageField(
        upload_to='company_logos/',
        blank=True,
        null=True,
        help_text="Logo de la empresa (recomendado: 300x100px)"
    )
    primary_color = models.CharField(
        max_length=7,
        default='#007bff',
        help_text="Color principal en formato HEX (#007bff)"
    )
    secondary_color = models.CharField(
        max_length=7,
        default='#6c757d',
        help_text="Color secundario en formato HEX"
    )

    # Configuración de títulos y textos
    site_title = models.CharField(
        max_length=100,
        help_text="Título que aparece en el navegador"
    )
    welcome_message = models.TextField(
        blank=True,
        null=True,
        help_text="Mensaje de bienvenida personalizado"
    )
    footer_text = models.TextField(
        blank=True,
        null=True,
        help_text="Texto adicional para el pie de página"
    )

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_company_configuration'
        verbose_name = 'Configuración de Empresa'
        verbose_name_plural = 'Configuraciones de Empresas'
        ordering = ['company_name']

    def __str__(self):
        return f"{self.company_name} ({self.subdomain})"

    def clean(self):
        """Validaciones personalizadas."""
        super().clean()

        # Validar formato de color HEX
        if self.primary_color and not self.primary_color.startswith('#'):
            raise ValidationError({'primary_color': 'El color debe empezar con #'})

        if self.secondary_color and not self.secondary_color.startswith('#'):
            raise ValidationError({'secondary_color': 'El color debe empezar con #'})

        # Validar que el subdominio no contenga caracteres especiales
        if not self.subdomain.replace('-', '').replace('_', '').isalnum():
            raise ValidationError(
                {'subdomain': 'El subdominio solo puede contener letras, números, guiones y guiones bajos'})

    def get_logo_url(self):
        """Retorna la URL del logo si existe."""
        return self.logo.url if self.logo else None

    def get_display_name(self):
        """Retorna el nombre corto o completo según disponibilidad."""
        return self.short_name if self.short_name else self.company_name
