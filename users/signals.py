# users/signals.py

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserSocioLink
from .enums import UserType
from .email_services import WelcomeEmailService

logger = logging.getLogger(__name__)

# Importar signal desde services para evitar importación circular
from .services import user_created_with_temp_password, UserTypeManager


@receiver(post_save, sender=User)
def create_empty_link_for_socio_users(sender, instance, created, **kwargs):
    """
    Crea UserSocioLink vacío SOLO para usuarios tipo SOCIO.

    IMPORTANTE: Solo crea link vacío como fallback.
    La vinculación real debe hacerse explícitamente en services.
    """
    if not created:
        return

    # Solo crear para usuarios que necesitan link
    if UserTypeManager.should_create_socio_link(instance):
        # Verificar que no existe ya (por si services ya lo creó)
        if not UserSocioLink.objects.filter(user=instance).exists():
            UserSocioLink.objects.create(
                user=instance,
                must_change_password=False  # services lo activará si es necesario
            )
            logger.debug(f"Fallback empty UserSocioLink created for user {instance.username}")


@receiver(user_created_with_temp_password)
def send_welcome_email_only(sender, user, temp_password, created_by=None, **kwargs):
    """
    Envía ÚNICAMENTE email de bienvenida cuando se crea un usuario SOCIO.

    SIMPLIFICADO: Solo welcome email. No envía notificaciones al staff.

    Args:
        sender: Clase que envía el signal
        user: Usuario creado
        temp_password: Contraseña temporal (MISMA que generó el servicio)
        created_by: Usuario que creó la cuenta
        **kwargs: Argumentos adicionales
    """
    logger.info(f"🔄 Processing welcome email for user: {user.username}")

    try:
        # Verificar que sea usuario SOCIO
        user_type = UserType.get_user_type(user)
        if user_type != UserType.SOCIO:
            logger.debug(f"⏭️ Skipping welcome email for non-SOCIO user {user.username} (type: {user_type.value})")
            return

        # Verificar que el usuario tenga email
        if not user.email:
            logger.warning(f"⚠️ User {user.username} has no email. Cannot send welcome email.")
            return

        # Log de la contraseña para verificar coincidencia
        logger.info(f"🔑 Temp password for {user.username}: {temp_password[:3]}***")

        # Obtener nombre del socio si está vinculado
        socio_name = _get_socio_display_name(user)

        logger.info(f"📧 Sending welcome email to: {user.username} ({user.email})")

        # Enviar ÚNICAMENTE email de bienvenida
        welcome_success = WelcomeEmailService.send_welcome_email_with_credentials(
            user=user,
            temporary_password=temp_password,  # ← MISMA contraseña del servicio
            socio_name=socio_name
        )

        if welcome_success:
            logger.info(f"✅ Welcome email sent successfully to {user.username}")
        else:
            logger.error(f"❌ Failed to send welcome email to {user.username}")

    except Exception as e:
        logger.error(f"❌ Error sending welcome email to {user.username}: {str(e)}", exc_info=True)


def _get_socio_display_name(user: User) -> str:
    """
    Helper function para obtener el nombre de display del socio.

    Returns:
        str: Nombre del socio o fallback al nombre del usuario
    """
    try:
        link = user.link
        if link and link.socio:
            return f"{link.socio.nombres} {link.socio.apellidos}".strip()
    except UserSocioLink.DoesNotExist:
        pass

    # Fallback al nombre completo del usuario
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name if full_name else user.username
