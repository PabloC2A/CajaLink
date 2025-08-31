# core/context_processors.py

from django.conf import settings


def company_context(request):
    """
    Context processor que añade información de la empresa al contexto
    de todos los templates.

    Args:
        request: HttpRequest con subdomain y company_config añadidos por middleware

    Returns:
        dict: Contexto con información de la empresa
    """

    # Configuración por defecto (dominio principal)
    default_config = {}

    # Si hay configuración de empresa específica, usarla
    company_config = getattr(request, 'company_config', None)

    if company_config:
        config_data = {
            'company_name': company_config.company_name,
            'short_name': company_config.short_name,
            'site_title': company_config.site_title,
            'email': company_config.email,
            'phone': company_config.phone,
            'address': company_config.address,
            'website': company_config.website,
            'logo_url': company_config.get_logo_url(),
            'primary_color': company_config.primary_color,
            'secondary_color': company_config.secondary_color,
            'welcome_message': company_config.welcome_message,
            'footer_text': company_config.footer_text,
        }
    else:
        config_data = default_config

    return {
        'company': config_data,
        'is_subdomain': hasattr(request, 'subdomain') and request.subdomain is not None,
        'current_subdomain': getattr(request, 'subdomain', None),
    }
