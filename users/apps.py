# users/apps.py

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuración de la aplicación Users.

    Maneja la configuración inicial y la importación de signals.
    Single Responsibility: Solo configuración de la aplicación.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Gestión de Usuarios'

    def ready(self):
        """
        Se ejecuta cuando la aplicación está lista.

        Importa los signals para que se registren automáticamente.
        """
        try:
            # Importar signals para que se registren
            import users.signals

            # Log de confirmación (si se necesita)
            import logging
            logger = logging.getLogger(__name__)
            logger.debug("Users app signals registered successfully")

        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error importing users signals: {e}")
            raise
