# users/mixins.py

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from legacy_models.models import Socio
from .enums import UserType
from .services import UserTypeManager

logger = logging.getLogger(__name__)


class StaffRequiredMixin(UserPassesTestMixin):
    """
    Mixin CENTRALIZADO para verificación de permisos staff.

    DRY Principle: Una sola implementación para todas las apps.
    Single Responsibility: Solo verifica permisos de staff.

    Usage:
        class MyStaffView(StaffRequiredMixin, ListView):
            # Solo usuarios staff pueden acceder
    """

    def test_func(self):
        """
        Verifica que el usuario tenga permisos de staff.

        Returns:
            bool: True si es staff, False si no
        """
        has_permission = self.request.user.is_staff

        if not has_permission:
            logger.warning(
                f"Non-staff user {self.request.user.username} attempted to access staff area"
            )

        return has_permission

    def handle_no_permission(self):
        """
        Manejo personalizado cuando no tiene permisos.

        Strategy Pattern: Diferentes responses según el estado del usuario.
        """
        if self.request.user.is_authenticated:
            # Usuario autenticado pero sin permisos staff
            logger.warning(
                f"Authenticated non-staff user {self.request.user.username} "
                f"denied access to {self.request.path}"
            )

            # Redirigir a su panel correspondiente
            user_type = UserType.get_user_type(self.request.user)
            redirect_url = UserTypeManager.get_post_login_redirect_url(self.request.user)

            messages.error(
                self.request,
                f"No tienes permisos para acceder a la sección de personal. "
                f"Has sido redirigido a tu panel de {user_type.display_name}."
            )

            return redirect(redirect_url)
        else:
            # Usuario no autenticado - comportamiento por defecto
            return super().handle_no_permission()


class SocioRequiredMixin(LoginRequiredMixin):
    """
    Mixin que asegura que solo usuarios SOCIO accedan a userpanel.

    Defensive Programming: Validaciones exhaustivas antes de proceder.
    Fail Fast: Detección temprana de problemas de configuración.
    Single Responsibility: Solo maneja acceso de socios.

    Attributes:
        socio: Instancia de Socio vinculada al usuario (disponible en la vista)

    Usage:
        class MySocioView(SocioRequiredMixin, TemplateView):
            def get_context_data(self, **kwargs):
                # self.socio está disponible y validado
                context['socio_name'] = self.socio.nombres
    """

    def dispatch(self, request, *args, **kwargs):
        # Primero hacer todas las validaciones
        user_type = UserType.get_user_type(request.user)
        if user_type != UserType.SOCIO:
            return self._handle_wrong_user_type(request.user, user_type)

        try:
            self.socio = self._get_user_socio(request.user)
        except SocioAccessError as e:
            return self._handle_socio_access_error(request, e)

        return super().dispatch(request, *args, **kwargs)

    def _handle_wrong_user_type(self, user, user_type):
        """
        Maneja el caso cuando un usuario del tipo incorrecto accede.

        Strategy Pattern: Diferentes redirecciones según el tipo.

        Args:
            user: Usuario que intenta acceder
            user_type: Tipo de usuario detectado

        Returns:
            HttpResponseRedirect: Redirect al panel correcto
        """
        redirect_url = UserTypeManager.get_post_login_redirect_url(user)

        logger.warning(
            f"{user_type.value} user {user.username} tried to access socio panel, "
            f"redirecting to {redirect_url}"
        )

        messages.info(
            self.request,
            f"Has sido redirigido a tu panel correspondiente como {user_type.display_name}."
        )

        return redirect(redirect_url)

    def _get_user_socio(self, user):
        """
        Obtiene el socio vinculado al usuario con validaciones exhaustivas.

        Defensive Programming: Valida todos los casos posibles.
        Performance: Una sola query optimizada con select_related.

        Args:
            user: Usuario autenticado

        Returns:
            Socio: Instancia del socio vinculado

        Raises:
            SocioAccessError: Para diferentes tipos de errores de acceso
        """
        try:
            # Optimización: Una sola query con select_related
            user_with_link = User.objects.select_related(
                'link__socio'
            ).get(id=user.id)

        except User.DoesNotExist:
            # Edge case: Usuario fue eliminado durante la sesión
            logger.error(f"User {user.id} not found during socio lookup")
            raise SocioAccessError(
                "Tu sesión es inválida. Por favor, inicia sesión nuevamente.",
                redirect_url='users:login'
            )

        # Verificación: UserSocioLink existe
        if not hasattr(user_with_link, 'link') or not user_with_link.link:
            logger.error(f"User {user.username} has no UserSocioLink")
            raise SocioAccessError(
                "Tu cuenta no está configurada correctamente. "
                "Contacta al administrador del sistema.",
                redirect_url='users:login',
                error_code='NO_LINK'
            )

        # Verificación: Socio está vinculado
        if not user_with_link.link.socio:
            logger.error(f"User {user.username} has UserSocioLink but no linked Socio")
            raise SocioAccessError(
                "Tu cuenta no está vinculada a un socio. "
                "Contacta al administrador del sistema.",
                redirect_url='users:login',
                error_code='NO_SOCIO'
            )

        # Verificación: Socio está activo
        socio = user_with_link.link.socio
        if getattr(socio, 'cerrado', False):
            logger.warning(f"User {user.username} linked to inactive socio {socio.id}")
            raise SocioAccessError(
                "Tu cuenta de socio está inactiva. "
                "Contacta a la cooperativa para más información.",
                redirect_url='homepage',
                error_code='INACTIVE_SOCIO'
            )

        logger.debug(f"Successfully retrieved socio {socio.id} for user {user.username}")
        return socio

    def _handle_socio_access_error(self, request, error):
        """
        Maneja errores de acceso al socio con redirección apropiada.

        Args:
            request: HttpRequest actual
            error: SocioAccessError con detalles del error

        Returns:
            HttpResponseRedirect: Redirect con mensaje de error
        """
        logger.info(f"Handling socio access error for user {request.user.username}: {error.error_code}")

        # Mostrar mensaje de error específico
        messages.error(request, str(error))

        # Redirigir a URL apropiada
        return redirect(error.redirect_url)


class AdminRequiredMixin(UserPassesTestMixin):
    """
    Mixin para vistas que requieren permisos de superusuario.

    Usage:
        class SuperSecretView(AdminRequiredMixin, TemplateView):
            # Solo superusuarios pueden acceder
    """

    def test_func(self):
        """Verifica que el usuario sea superusuario."""
        has_permission = self.request.user.is_superuser

        if not has_permission:
            logger.warning(
                f"Non-admin user {self.request.user.username} "
                f"attempted to access admin-only area"
            )

        return has_permission

    def handle_no_permission(self):
        """Manejo de permisos para superusuarios."""
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                # Staff pero no superusuario
                messages.error(
                    self.request,
                    "Esta sección requiere permisos de administrador."
                )
                return redirect('staffpanel:dashboard')
            else:
                # Usuario regular
                user_type = UserType.get_user_type(self.request.user)
                redirect_url = UserTypeManager.get_post_login_redirect_url(self.request.user)

                messages.error(
                    self.request,
                    "No tienes permisos para acceder a esta sección."
                )
                return redirect(redirect_url)

        return super().handle_no_permission()


class SocioAccessError(Exception):
    """
    Excepción personalizada para errores de acceso de socio.

    Strategy Pattern: Diferentes tipos de error con diferentes strategies de manejo.

    Attributes:
        message: Mensaje de error para el usuario
        redirect_url: URL a la que redirigir
        error_code: Código interno para logging/debugging
    """

    def __init__(self, message, redirect_url='homepage', error_code='GENERIC'):
        """
        Inicializa la excepción con información de contexto.

        Args:
            message: Mensaje amigable para el usuario
            redirect_url: URL para redirigir después del error
            error_code: Código interno para categorizar el error
        """
        self.message = message
        self.redirect_url = redirect_url
        self.error_code = error_code
        super().__init__(message)

    def __str__(self):
        """String representation para mostrar al usuario."""
        return self.message


# ========================================
# UTILITIES Y HELPERS
# ========================================

def get_user_dashboard_url(user):
    """
    Utility function para obtener la URL del dashboard del usuario.

    Args:
        user: Instancia de User

    Returns:
        str: URL del dashboard correspondiente
    """
    redirect_url_name = UserTypeManager.get_post_login_redirect_url(user)
    return reverse(redirect_url_name)


def is_socio_user(user):
    """
    Verifica si un usuario es de tipo socio.

    Args:
        user: Instancia de User

    Returns:
        bool: True si es socio, False si no
    """
    return UserType.get_user_type(user) == UserType.SOCIO


def is_staff_user(user):
    """
    Verifica si un usuario es de tipo staff (no admin).

    Args:
        user: Instancia de User

    Returns:
        bool: True si es staff pero no admin, False si no
    """
    return UserType.get_user_type(user) == UserType.STAFF
