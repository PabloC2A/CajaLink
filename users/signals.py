import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserSocioLink
from .services import UserTypeManager

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
