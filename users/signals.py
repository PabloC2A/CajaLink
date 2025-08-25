# users/signals.py

import logging
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .email_services import WelcomeEmailService, EmailNotificationService
from .enums import UserType
from .models import UserSocioLink
from .services import user_created_with_temp_password, UserTypeManager

logger = logging.getLogger(__name__)


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
def handle_user_creation_with_temp_password(sender, user, temp_password, created_by=None, **kwargs):
    """
    Maneja la creación de usuarios con contraseña temporal.

    Este signal personalizado permite pasar la contraseña temporal y otros datos
    necesarios para el envío del email de bienvenida.

    CORREGIDO: Ahora maneja tanto el email de bienvenida como la notificación al staff.

    Args:
        sender: Clase que envía el signal
        user: Usuario creado
        temp_password: Contraseña temporal
        created_by: Usuario que creó la cuenta
        **kwargs: Argumentos adicionales
    """
    logger.info(f"Processing user creation with temp password for: {user.username}")

    try:
        # Verificar que sea usuario SOCIO
        user_type = UserType.get_user_type(user)
        if user_type != UserType.SOCIO:
            logger.debug(f"Skipping email processing for non-SOCIO user {user.username}")
            return

        # 1. ENVIAR EMAIL DE BIENVENIDA
        if user.email:
            # Obtener nombre del socio si está vinculado
            socio_name = None
            try:
                link = user.link
                if link and link.socio:
                    socio_name = f"{link.socio.nombres} {link.socio.apellidos}".strip()
            except UserSocioLink.DoesNotExist:
                pass

            # Usar el nombre completo del usuario si no hay nombre de socio
            if not socio_name:
                socio_name = f"{user.first_name} {user.last_name}".strip()
                if not socio_name:
                    socio_name = user.username

            logger.info(f"Sending welcome email to new user: {user.username}")

            # Enviar email de bienvenida
            welcome_success = WelcomeEmailService.send_welcome_email_with_credentials(
                user=user,
                temporary_password=temp_password,
                socio_name=socio_name
            )

            if welcome_success:
                logger.info(f"Welcome email sent successfully to {user.username}")
            else:
                logger.error(f"Failed to send welcome email to {user.username}")
        else:
            logger.warning(f"User {user.username} has no email. Cannot send welcome email.")

        # 2. ENVIAR NOTIFICACIÓN AL STAFF
        try:
            # Obtener nombre del socio para la notificación
            socio_name_for_staff = None
            try:
                link = user.link
                if link and link.socio:
                    socio_name_for_staff = f"{link.socio.nombres} {link.socio.apellidos}".strip()
            except UserSocioLink.DoesNotExist:
                pass

            logger.info(f"Sending staff notification for new user: {user.username}")

            # Enviar notificación al staff
            staff_success = EmailNotificationService.send_user_creation_notification_to_staff(
                created_user=user,
                created_by=created_by,
                socio_name=socio_name_for_staff
            )

            if staff_success:
                logger.info(f"Staff notification sent successfully for user {user.username}")
            else:
                logger.warning(f"Failed to send staff notification for user {user.username}")

        except Exception as staff_error:
            logger.error(f"Error sending staff notification for {user.username}: {str(staff_error)}")

        logger.debug(f"Email processing completed for user {user.username}")

    except Exception as e:
        logger.error(f"Error processing user creation signal for {user.username}: {str(e)}", exc_info=True)


# Signal adicional para casos específicos donde se requiera solo notificación al staff
@receiver(post_save, sender=User)
def notify_staff_of_non_socio_user_creation(sender, instance, created, **kwargs):
    """
    Notifica al staff cuando se crea un usuario NO-SOCIO (Staff/Superuser).

    Este signal maneja usuarios que no pasan por el flujo de contraseña temporal.
    """
    if not created:
        return

    # Solo para usuarios NO-SOCIO (Staff/Superuser)
    user_type = UserType.get_user_type(instance)
    if user_type == UserType.SOCIO:
        # Los SOCIO se manejan en el signal personalizado
        return

    # Solo notificar si es Staff o Superuser importante
    if user_type not in [UserType.STAFF, UserType.SUPERUSER]:
        return

    try:
        logger.info(f"Sending staff notification for new {user_type.value} user: {instance.username}")

        # Enviar notificación al staff
        success = EmailNotificationService.send_user_creation_notification_to_staff(
            created_user=instance,
            created_by=getattr(instance, '_created_by', None),
            socio_name=None  # No hay socio para staff/superusers
        )

        if success:
            logger.info(f"Staff notification sent successfully for {user_type.value} user {instance.username}")
        else:
            logger.warning(f"Failed to send staff notification for {user_type.value} user {instance.username}")

    except Exception as e:
        logger.error(f"Error sending staff notification for {user_type.value} {instance.username}: {str(e)}")
