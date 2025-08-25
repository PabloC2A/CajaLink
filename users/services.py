# users/services.py

import logging
from typing import Tuple, Optional
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.crypto import get_random_string

from legacy_models.models import Socio
from .models import UserSocioLink
from .enums import UserType

logger = logging.getLogger(__name__)


class UserTypeManager:
    """
    Manager que maneja operaciones específicas por tipo de usuario.

    Strategy Pattern: Diferentes estrategias según el tipo de usuario.
    Factory Pattern: Crea componentes específicos según el tipo.
    Single Responsibility: Solo se encarga de lógica de tipos de usuario.
    """

    @classmethod
    def should_create_socio_link(cls, user) -> bool:
        """
        Determina si un usuario necesita UserSocioLink.

        Strategy Pattern: Estrategia específica por tipo de usuario.

        Args:
            user: Instancia de User

        Returns:
            bool: True si necesita UserSocioLink, False si no
        """
        user_type = UserType.get_user_type(user)

        # Mapeo de estrategias por tipo
        strategies = {
            UserType.SUPERUSER: False,  # Admins no necesitan link
            UserType.STAFF: False,  # Staff no necesita link
            UserType.SOCIO: True,  # Solo socios necesitan link
        }

        result = strategies.get(user_type, False)
        logger.debug(f"User {user.username} type {user_type.value} should_create_socio_link: {result}")

        return result

    @classmethod
    def should_check_password_change(cls, user) -> bool:
        """
        Determina si un usuario debe ser verificado para cambio de contraseña forzado.

        Args:
            user: Instancia de User

        Returns:
            bool: True si debe verificar cambio de contraseña
        """
        user_type = UserType.get_user_type(user)

        # Solo socios necesitan verificación de contraseña forzada
        should_check = user_type == UserType.SOCIO

        logger.debug(f"User {user.username} type {user_type.value} should_check_password_change: {should_check}")
        return should_check

    @classmethod
    def get_post_login_redirect_url(cls, user) -> str:
        """
        Obtiene la URL de redirección después del login según tipo de usuario.

        Factory Pattern: Crea respuestas específicas por tipo.

        Args:
            user: Instancia de User

        Returns:
            str: Nombre de la URL para redirect()
        """
        user_type = UserType.get_user_type(user)

        # Mapeo de estrategias de redirección
        redirect_strategies = {
            UserType.SUPERUSER: 'admin:index',
            UserType.STAFF: 'staffpanel:dashboard',
            UserType.SOCIO: 'userpanel:dashboard',
        }

        redirect_url = redirect_strategies.get(user_type, 'userpanel:dashboard')

        logger.info(f"Post-login redirect for user {user.username} ({user_type.value}): {redirect_url}")
        return redirect_url

    @classmethod
    def validate_user_creation(cls, user_type: UserType, socio: Optional[Socio] = None):
        """
        Valida la creación de usuario según su tipo.

        Fail Fast Pattern: Valida temprano para evitar estados inconsistentes.

        Args:
            user_type: Tipo de usuario a crear
            socio: Socio a vincular (solo para tipo SOCIO)

        Raises:
            ValidationError: Si la validación falla
        """
        logger.debug(f"Validating user creation for type {user_type.value}")

        if user_type == UserType.SOCIO:
            if not socio:
                raise ValidationError("Los usuarios tipo SOCIO requieren un socio vinculado")

            # Verificar que el socio no tenga usuario ya
            if UserSocioLink.objects.filter(socio=socio).exists():
                raise ValidationError(
                    f"El socio {socio.nombres} {socio.apellidos} ya tiene usuario web vinculado"
                )

            # Verificar que el socio esté activo
            if getattr(socio, 'cerrado', False):
                raise ValidationError(
                    f"No se puede crear usuario para socio inactivo: {socio.nombres} {socio.apellidos}"
                )

        elif user_type in [UserType.SUPERUSER, UserType.STAFF]:
            if socio:
                raise ValidationError(
                    f"Los usuarios {user_type.display_name} no deben tener socio vinculado"
                )

        logger.debug(f"User creation validation passed for type {user_type.value}")


class UserCreationService:
    """
    Service para creación de usuarios web de diferentes tipos.

    Factory Pattern: Crea diferentes tipos de usuario según especificación.
    Template Method: Define pasos del proceso de creación.
    Single Responsibility: Solo se encarga de crear usuarios.
    """

    DEFAULT_PASSWORD_LENGTH = 12

    @classmethod
    @transaction.atomic
    def create_user_by_type(
            cls,
            user_type: UserType,
            username: str,
            email: str,
            first_name: str = "",
            last_name: str = "",
            socio: Optional[Socio] = None,
            is_active: bool = True
    ) -> Tuple[User, Optional[str]]:
        """
        Crea usuario según su tipo con validaciones específicas.

        Template Method Pattern: Define pasos del proceso de creación.
        Strategy Pattern: Comportamiento específico por tipo de usuario.

        Args:
            user_type: Tipo de usuario a crear
            username: Username único
            email: Email del usuario
            first_name: Nombres
            last_name: Apellidos
            socio: Socio a vincular (solo para tipo SOCIO)
            is_active: Si el usuario está activo

        Returns:
            Tuple[User, contraseña_temporal]:
            - Para SOCIO: (user, password)
            - Para ADMIN/STAFF: (user, None)

        Raises:
            ValidationError: Si las validaciones fallan
        """
        logger.info(f"Creating user of type {user_type.value}: {username}")

        # Paso 1: Validar precondiciones por tipo
        UserTypeManager.validate_user_creation(user_type, socio)

        # Paso 2: Validar unicidad del username
        if User.objects.filter(username=username).exists():
            raise ValidationError(f"El username '{username}' ya existe")

        # Paso 3: Validar email si se proporciona
        if email:
            try:
                validate_email(email)
            except ValidationError as e:
                raise ValidationError(f"Email inválido: {email}")

        # Paso 4: Crear usuario base según el tipo
        user = cls._create_base_user(user_type, username, email, first_name, last_name, is_active)

        # Paso 5: Configurar específicos por tipo
        temp_password = None
        if user_type == UserType.SOCIO:
            temp_password = cls._setup_socio_user(user, socio)
        elif user_type == UserType.STAFF:
            cls._setup_staff_user(user)
        elif user_type == UserType.SUPERUSER:
            cls._setup_superuser(user)

        logger.info(f"User {username} created successfully as {user_type.value}")
        return user, temp_password

    @classmethod
    def _create_base_user(cls, user_type: UserType, username: str, email: str,
                          first_name: str, last_name: str, is_active: bool) -> User:
        """
        Crea el usuario base de Django.

        Factory Pattern: Crea usuario según especificaciones.
        """
        logger.debug(f"Creating base user {username} for type {user_type.value}")

        # Para socios, creamos con contraseña que será asignada después
        if user_type == UserType.SOCIO:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=is_active
            )
        else:
            # Para admin/staff, contraseña debe ser asignada manualmente después
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=is_active,
                password=None
            )
            user.set_unusable_password()  # Marcar como sin contraseña válida
            user.save()

        return user

    @classmethod
    def _setup_socio_user(cls, user: User, socio: Socio) -> str:
        """
        Configura usuario tipo SOCIO con contraseña temporal y vinculación.

        Returns:
            str: Contraseña temporal generada
        """
        logger.debug(f"Setting up socio user {user.username} for socio {socio.id}")

        # Generar contraseña temporal segura
        temp_password = cls._generate_secure_password()
        user.set_password(temp_password)
        user.save()

        # Crear vinculación con socio EXPLÍCITAMENTE
        # Usar get_or_create para evitar duplicados por si signal ya creó uno
        link, created = UserSocioLink.objects.get_or_create(
            user=user,
            defaults={
                'socio': socio,
                'must_change_password': True
            }
        )

        # Si ya existía (por signal), actualizarlo con el socio
        if not created:
            link.socio = socio
            link.must_change_password = True
            link.save()
            logger.debug(f"Updated existing UserSocioLink for user {user.username}")
        else:
            logger.debug(f"Created new UserSocioLink for user {user.username}")

        logger.info(f"Socio user {user.username} linked to socio {socio.id}")
        return temp_password

    @classmethod
    def _setup_staff_user(cls, user: User):
        """Configura usuario tipo STAFF."""
        logger.debug(f"Setting up staff user {user.username}")

        user.is_staff = True
        user.save()

        # Los staff NO necesitan UserSocioLink
        logger.debug(f"Staff user {user.username} configured (no UserSocioLink created)")

    @classmethod
    def _setup_superuser(cls, user: User):
        """Configura usuario tipo SUPERUSER."""
        logger.debug(f"Setting up superuser {user.username}")

        user.is_staff = True
        user.is_superuser = True
        user.save()

        # Los superusers NO necesitan UserSocioLink
        logger.debug(f"Superuser {user.username} configured (no UserSocioLink created)")

    @classmethod
    def _generate_secure_password(cls, length: int = DEFAULT_PASSWORD_LENGTH) -> str:
        """
        Genera contraseña temporal segura.

        Factory Pattern: Crea contraseñas con configuración específica.
        """
        # Usar caracteres seguros para contraseña temporal
        allowed_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
        return get_random_string(length=length, allowed_chars=allowed_chars)


# ========================================
# FUNCIONES DE COMPATIBILIDAD
# ========================================

@transaction.atomic
def create_web_user_for_socio(
        *,
        socio: Socio,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
) -> Tuple[User, str]:
    """
    Función de compatibilidad para crear usuarios SOCIO.
    Mantiene la API existente para no romper código que la usa.

    NOTA: Se recomienda migrar a UserCreationService.create_user_by_type()
    para mejor manejo de errores y funcionalidades extendidas.

    Args:
        socio: La instancia del modelo Socio a vincular
        username: Username para el nuevo usuario
        email: Email para la nueva cuenta
        first_name: Nombres del usuario
        last_name: Apellidos del usuario

    Returns:
        Tuple[User, str]: Usuario creado y contraseña temporal

    Raises:
        ValidationError: Si las validaciones fallan
        IntegrityError: Si hay problemas de integridad en BD
    """
    logger.info(f"Creating web user for socio {socio.id} via compatibility function")

    try:
        user, temp_password = UserCreationService.create_user_by_type(
            user_type=UserType.SOCIO,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            socio=socio
        )

        return user, temp_password

    except Exception as e:
        logger.error(f"Error in compatibility create_web_user_for_socio: {e}")
        raise


# ========================================
# UTILITIES
# ========================================

def get_user_display_info(user) -> dict:
    """
    Obtiene información de display para un usuario.

    Utility function para templates y logging.

    Args:
        user: Instancia de User

    Returns:
        dict: Información del usuario para display
    """
    user_type = UserType.get_user_type(user)

    info = {
        'username': user.username,
        'full_name': user.get_full_name() or user.username,
        'type': user_type.value,
        'type_display': user_type.display_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'has_socio_link': False,
        'socio_info': None
    }

    # Añadir info de socio si aplica
    if user_type == UserType.SOCIO and hasattr(user, 'link') and user.link and user.link.socio:
        info['has_socio_link'] = True
        info['socio_info'] = {
            'nombres': user.link.socio.nombres,
            'apellidos': user.link.socio.apellidos,
            'cedula': user.link.socio.cedula,
            'cuenta': user.link.socio.cuenta
        }

    return info
