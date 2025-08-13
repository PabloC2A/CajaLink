# users/models.py

from django.db import models
from django.conf import settings
from legacy_models.models import Socio


class UserSocioLink(models.Model):
    """
    Tabla intermedia que vincula un usuario de autenticación de Django ('User')
    con un registro de socio del sistema legacy ('Socio').
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='link',
        verbose_name="Usuario Web"
    )

    socio = models.OneToOneField(
        Socio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Socio Vinculado (Legacy)"
    )

    must_change_password = models.BooleanField(
        default=False,
        verbose_name="Forzar Cambio de Contraseña",
        help_text="Si está activo, el usuario será forzado a cambiar su contraseña en el próximo inicio de sesión."
    )

    class Meta:
        verbose_name = "Vínculo Usuario-Socio"
        verbose_name_plural = "Vínculos Usuario-Socio"

    def __str__(self):
        return f'Vínculo para {self.user.username}'
