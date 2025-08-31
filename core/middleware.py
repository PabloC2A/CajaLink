# core/middleware.py

from django.core.cache import cache
from .models import CompanyConfiguration


class SubdomainDetectionMiddleware:
    """
    Middleware que detecta el subdominio y asigna la configuración
    de empresa correspondiente al request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Procesa el request antes de llegar a las vistas.
        Implementa caching para optimizar rendimiento.
        """
        # Detectar subdominio
        subdomain = self._extract_subdomain(request.get_host())

        # Obtener configuración de empresa
        company_config = self._get_company_configuration(subdomain)

        # Asignar al request para uso en vistas
        request.subdomain = subdomain
        request.company_config = company_config

        response = self.get_response(request)
        return response

    def _extract_subdomain(self, host):
        if not host:
            return None
        host = host.split(':')[0]
        parts = host.split('.')

        # dev: caja.localhost -> 'caja'
        if len(parts) == 2 and parts[1] in ("localhost",):
            return parts[0].lower()

        # dev helpers: lvh.me / nip.io (caja.lvh.me, caja.127.0.0.1.nip.io)
        if host.endswith("lvh.me") or host.endswith("nip.io"):
            return parts[0].lower()

        # prod: 3+ partes
        if len(parts) >= 3:
            return parts[0].lower()

        return None

    def _get_company_configuration(self, subdomain):
        """
        Obtiene la configuración de empresa para el subdominio.
        Utiliza cache para optimizar consultas.

        Args:
            subdomain (str): Subdominio detectado

        Returns:
            CompanyConfiguration or None: Configuración de empresa
        """
        if not subdomain:
            return None

        # Clave de cache única por subdominio
        cache_key = f'company_config:{subdomain}'

        # Intentar obtener desde cache
        company_config = cache.get(cache_key)

        if company_config is None:
            try:
                # Consultar base de datos
                company_config = CompanyConfiguration.objects.get(
                    subdomain=subdomain,
                    is_active=True
                )

                # Guardar en cache por 1 hora
                cache.set(cache_key, company_config, 3600)

            except CompanyConfiguration.DoesNotExist:
                # Guardar resultado negativo en cache por 15 minutos
                cache.set(cache_key, False, 900)
                return None

        # Si el cache devuelve False, significa que no existe
        return company_config if company_config is not False else None
