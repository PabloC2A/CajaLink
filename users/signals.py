# users/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserSocioLink


@receiver(post_save, sender=User)
def handle_user_save(sender, instance, created, **kwargs):
    """
    Maneja la creación de Vínculos para usuarios normales y la
    actualización de la bandera de cambio de contraseña.
    """
    # CORRECCIÓN: Si el usuario es staff (incluyendo superusuarios), no hacemos nada.
    if instance.is_staff:
        return

    if created:
        if not hasattr(instance, 'link'):
            UserSocioLink.objects.create(user=instance)
    else:
        if hasattr(instance, 'link') and instance.link.must_change_password:
            instance.link.must_change_password = False
            instance.link.save()
