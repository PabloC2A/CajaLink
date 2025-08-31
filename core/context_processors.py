# core/context_processors.py

def company_context(request):
    default_config = {
        'company_name': "Entidad",
        'short_name': "Entidad",
        'site_title': "Portal",
        'email': "info@tucaja.com",
        'phone': "0000000000",
        'address': "Loja, Ecuador",
        'website': "",
        'logo_url': None,
        'primary_color': "#007bff",
        'secondary_color': "#6c757d",
        'welcome_message': "",
        'footer_text': "Estamos para servirle.",
    }

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