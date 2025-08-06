# users/services.py

from django.db import transaction
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from .models import Profile


@transaction.atomic
def create_socio_user(
        *,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        cedula: str
) -> tuple[User, str]:
    """
    Crea un User y actualiza su Profile con los datos adicionales.
    La señal 'post_save' se encarga de la creación inicial del Profile.
    """
    # 1. Crear el usuario
    new_user = User.objects.create_user(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name
    )

    # 2. Asignar contraseña temporal
    temp_password = get_random_string(length=12)
    new_user.set_password(temp_password)
    new_user.save()

    # 3. Obtenemos el perfil que la señal acaba de crear
    # y lo actualizamos con los datos del formulario.
    profile = new_user.profile
    profile.cedula = cedula
    profile.debe_cambiar_password = True
    profile.save()

    return new_user, temp_password
