# users/services.py

from django.db import transaction
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from legacy_models.models import Socio
from .models import UserSocioLink


@transaction.atomic
def create_web_user_for_socio(
        *,
        socio: Socio,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
) -> tuple[User, str]:
    """
    Crea un usuario web de Django y lo vincula a un registro de Socio existente.

    Esta operación es atómica. Si algo falla, se revierten todos los cambios.

    Args:
        socio: La instancia del modelo Socio a la que se vinculará el nuevo usuario.
        username: El nombre de usuario para el nuevo login web.
        email: El email para la nueva cuenta web.
        first_name: Nombres del usuario.
        last_name: Apellidos del usuario.

    Returns:
        Una tupla con el objeto User recién creado y su contraseña temporal.
    """
    # 1. Crear el usuario de Django
    web_user = User.objects.create_user(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name
    )

    # 2. Asignar contraseña temporal segura
    temp_password = get_random_string(length=12)
    web_user.set_password(temp_password)
    web_user.save()

    # 3. La señal 'post_save' ya ha creado un 'UserSocioLink' vacío.
    #    Ahora lo obtenemos y lo actualizamos para vincularlo al Socio
    #    y activar la bandera de cambio de contraseña.
    link = web_user.link
    link.socio = socio
    link.must_change_password = True
    link.save()

    return web_user, temp_password
