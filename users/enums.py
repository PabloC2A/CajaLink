# users/enums.py

from enum import Enum


class UserType(Enum):
    """
    Enum que define los tipos de usuario en el sistema.

    Strategy Pattern: Define estrategias para diferentes tipos de usuario.
    Type Safety: Previene errores con magic strings.
    """
    SUPERUSER = "superuser"
    STAFF = "staff"
    SOCIO = "socio"

    @classmethod
    def get_user_type(cls, user):
        """
        Determina el tipo de usuario basado en sus permisos.

        Factory Method Pattern: Crea la estrategia correcta según el usuario.

        Args:
            user: Instancia de User

        Returns:
            UserType: Tipo de usuario correspondiente
        """
        if not user or not hasattr(user, 'is_superuser'):
            return cls.SOCIO  # Default seguro

        if user.is_superuser:
            return cls.SUPERUSER
        elif user.is_staff:
            return cls.STAFF
        else:
            return cls.SOCIO

    def __str__(self):
        """String representation para templates y logging."""
        return self.value

    @property
    def display_name(self):
        """Nombre legible para mostrar en interfaz."""
        display_names = {
            self.SUPERUSER: "Administrador",
            self.STAFF: "Personal",
            self.SOCIO: "Socio"
        }
        return display_names.get(self, "Desconocido")
