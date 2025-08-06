# users/models.py

from django.db import models
from django.conf import settings


class Profile(models.Model):
    """
    Almacena información adicional para cada usuario del sistema.
    """
    # Relación uno-a-uno con el usuario de Django.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Cédula de identidad, debe ser única.
    cedula = models.CharField(max_length=10, unique=True, help_text="Cédula de identidad del socio")

    def __str__(self):
        return f'Perfil de {self.user.username}'
