# users/signals.py

import logging

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from .email_services import WelcomeEmailService, EmailNotificationService
from .enums import UserType
from .models import UserSocioLink
from .services import UserTypeManager

logger = logging.getLogger(__name__)

# Signal personalizado para casos donde necesitamos pasar información adicional
user_created_with_temp_password = Signal()


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


@receiver(post_save, sender=User)
def send_welcome_email_on_user_creation(sender, instance, created, **kwargs):
    """
    Envía email de bienvenida cuando se crea un nuevo usuario SOCIO.

    Este signal se ejecuta después de que el usuario ha sido creado completamente,
    incluyendo su UserSocioLink si aplica.

    Single Responsibility: Solo maneja el envío de emails de bienvenida.
    Open/Closed: Extensible para diferentes tipos de usuarios sin modificar el código.
    """
    if not created:
        return

    # Solo enviar emails a usuarios tipo SOCIO
    user_type = UserType.get_user_type(instance)
    if user_type != UserType.SOCIO:
        logger.debug(f"Skipping welcome email for user {instance.username} (type: {user_type.value})")
        return

    # Verificar que el usuario tenga email
    if not instance.email:
        logger.warning(f"User {instance.username} has no email. Cannot send welcome email.")
        return

    # Verificar si hay una contraseña temporal almacenada en la metadata del usuario
    # (esto se debe manejar desde el servicio de creación)
    try:
        # Buscar la contraseña temporal en la metadata del usuario o usar una estrategia diferente
        temp_password = getattr(instance, '_temp_password', None)

        if not temp_password:
            logger.warning(f"No temporary password found for user {instance.username}. Cannot send welcome email.")
            return

        # Obtener nombre del socio si está vinculado
        socio_name = None
        try:
            link = instance.link
            if link and link.socio:
                socio_name = f"{link.socio.nombres} {link.socio.apellidos}".strip()
        except UserSocioLink.DoesNotExist:
            pass

        # Usar el nombre completo del usuario si no hay nombre de socio
        if not socio_name:
            socio_name = f"{instance.first_name} {instance.last_name}".strip()
            if not socio_name:
                socio_name = instance.username

        logger.info(f"Sending welcome email to new user: {instance.username}")

        # Enviar email de bienvenida
        success = WelcomeEmailService.send_welcome_email_with_credentials(
            user=instance,
            temporary_password=temp_password,
            socio_name=socio_name
        )

        if success:
            logger.info(f"Welcome email sent successfully to {instance.username}")
        else:
            logger.error(f"Failed to send welcome email to {instance.username}")

    except Exception as e:
        logger.error(f"Error sending welcome email to {instance.username}: {str(e)}")


@receiver(post_save, sender=User)
def notify_staff_of_user_creation(sender, instance, created, **kwargs):
    """
    Notifica al staff cuando se crea un nuevo usuario.

    Single Responsibility: Solo maneja notificaciones al staff.
    Dependency Inversion: Depende de abstracciones del servicio de email.
    """
    if not created:
        return

    # Solo notificar para usuarios tipo SOCIO (los más relevantes para el negocio)
    user_type = UserType.get_user_type(instance)
    if user_type != UserType.SOCIO:
        logger.debug(f"Skipping staff notification for user {instance.username} (type: {user_type.value})")
        return

    try:
        # Obtener información del usuario que creó esta cuenta
        created_by = getattr(instance, '_created_by', None)

        # Obtener nombre del socio si está vinculado
        socio_name = None
        try:
            link = instance.link
            if link and link.socio:
                socio_name = f"{link.socio.nombres} {link.socio.apellidos}".strip()
        except UserSocioLink.DoesNotExist:
            pass

        logger.info(f"Sending staff notification for new user: {instance.username}")

        # Enviar notificación al staff
        success = EmailNotificationService.send_user_creation_notification_to_staff(
            created_user=instance,
            created_by=created_by,
            socio_name=socio_name
        )

        if success:
            logger.info(f"Staff notification sent successfully for user {instance.username}")
        else:
            logger.warning(f"Failed to send staff notification for user {instance.username}")

    except Exception as e:
        logger.error(f"Error sending staff notification for {instance.username}: {str(e)}")


@receiver(user_created_with_temp_password)
def handle_user_creation_with_temp_password(sender, user, temp_password, created_by=None, **kwargs):
    """
    Maneja la creación de usuarios con contraseña temporal.

    Este signal personalizado permite pasar la contraseña temporal y otros datos
    necesarios para el envío del email de bienvenida.

    Args:
        sender: Clase que envía el signal
        user: Usuario creado
        temp_password: Contraseña temporal
        created_by: Usuario que creó la cuenta
        **kwargs: Argumentos adicionales
    """
    logger.info(f"Processing user creation with temp password for: {user.username}")

    try:
        # Almacenar temporalmente la contraseña y información del creador en el objeto usuario
        user._temp_password = temp_password
        user._created_by = created_by

        # Los otros signals se encargarán del resto del procesamiento automáticamente
        logger.debug(f"Temp password and creation info stored for user {user.username}")

    except Exception as e:
        logger.error(f"Error processing user creation signal for {user.username}: {str(e)}")
