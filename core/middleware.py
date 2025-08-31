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
        """
        Extrae el subdominio del host.

        Args:
            host (str): Host completo (ej: cajacomunalsantiago.refse.org)

        Returns:
            str: Subdominio o None si es el dominio principal
        """
        if not host:
            return None

        # Remover puerto si existe
        host = host.split(':')[0]

        # Separar por puntos
        parts = host.split('.')

        # Si hay 3 o más partes, el primero es el subdominio
        # Ej: cajacomunalsantiago.refse.org -> ['cajacomunalsantiago', 'refse', 'org']
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
