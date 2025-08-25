# users/email_services.py

import logging
from typing import Optional, List

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class BaseEmailService:
    """
    Clase base para servicios de email.

    Template Method Pattern: Define estructura común para envío de emails.
    Single Responsibility: Solo maneja operaciones base de email.
    """

    @classmethod
    def _get_base_url(cls) -> str:
        """Obtiene la URL base del sistema."""
        return getattr(settings, 'BASE_URL', 'http://localhost:8000')

    @classmethod
    def _get_support_email(cls) -> str:
        """Obtiene el email de soporte."""
        return getattr(settings, 'SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL)

    @classmethod
    def _get_company_name(cls) -> str:
        """Obtiene el nombre de la empresa."""
        return getattr(settings, 'COMPANY_NAME', 'ByteAndino')

    @classmethod
    def _get_admin_url(cls) -> str:
        """Obtiene la URL del panel de administración."""
        base_url = cls._get_base_url()
        return f"{base_url}/admin/"

    @classmethod
    def _get_from_email(cls) -> str:
        """Obtiene el email remitente."""
        return getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@refse.org')

    @classmethod
    def _send_email(
            cls,
            subject: str,
            html_content: str,
            plain_content: str,
            recipient_list: List[str],
            from_email: Optional[str] = None
    ) -> bool:
        """
        Metodo base para envío de emails con HTML y texto plano.

        Template Method Pattern: Estructura común de envío.

        Args:
            subject: Asunto del email
            html_content: Contenido HTML
            plain_content: Contenido texto plano
            recipient_list: Lista de destinatarios
            from_email: Email remitente (opcional)

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            if not from_email:
                from_email = cls._get_from_email()

            # Usar EmailMultiAlternatives para soporte HTML + texto
            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_content,
                from_email=from_email,
                to=recipient_list
            )
            msg.attach_alternative(html_content, "text/html")

            result = msg.send(fail_silently=False)
            return bool(result)

        except Exception as e:
            logger.error(f"Error sending email to {recipient_list}: {str(e)}")
            return False

    @classmethod
    def _validate_email_requirements(cls, user: User, require_email: bool = True) -> bool:
        """
        Valida requerimientos básicos para envío de email.

        Args:
            user: Usuario destinatario
            require_email: Si se requiere email válido

        Returns:
            bool: True si pasa validaciones
        """
        if require_email and not user.email:
            logger.warning(f"User {user.username} has no email address")
            return False

        return True


class WelcomeEmailService(BaseEmailService):
    """
    Servicio especializado en envío de emails de bienvenida.

    Single Responsibility: Solo maneja emails de bienvenida.
    Open/Closed: Extensible para diferentes tipos de emails sin modificar código existente.
    Dependency Inversion: Depende de abstracciones (configuración), no implementaciones concretas.
    """

    @classmethod
    def send_welcome_email_with_credentials(
            cls,
            user: User,
            temporary_password: str,
            socio_name: Optional[str] = None
    ) -> bool:
        """
        Envía email de bienvenida con credenciales temporales.

        MEJORADO: Logging detallado para debug de contraseña.
        """
        try:
            logger.info(f"📧 Sending welcome email to user: {user.username} ({user.email})")
            logger.info(f"🔑 Using temp password: {temporary_password[:3]}*** (length: {len(temporary_password)})")

            # Validaciones previas
            if not cls._validate_email_requirements(user, require_email=True):
                return False

            # Preparar contexto para los templates
            context = cls._build_welcome_email_context(user, temporary_password, socio_name)

            # Log del contexto para verificar
            logger.debug(
                f"📋 Email context - username: {context['username']}, password: {context['temporary_password'][:3]}***")

            # Generar contenido del email
            subject = cls._generate_welcome_subject()
            html_content = cls._render_welcome_html_template(context)
            plain_content = cls._render_welcome_text_template(context)

            # Log del contenido generado (parcial)
            logger.debug(f"📄 Email content preview: {plain_content[:200]}...")

            # Enviar email usando metodo base
            success = cls._send_email(
                subject=subject,
                html_content=html_content,
                plain_content=plain_content,
                recipient_list=[user.email]
            )

            if success:
                logger.info(f"✅ Welcome email sent successfully to {user.email}")
                return True
            else:
                logger.error(f"❌ Failed to send welcome email to {user.email}")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending welcome email to {user.username}: {str(e)}", exc_info=True)
            return False

    @classmethod
    def _build_welcome_email_context(
            cls,
            user: User,
            temporary_password: str,
            socio_name: Optional[str]
    ) -> dict:
        """
        Construye el contexto para los templates de bienvenida.

        Factory Pattern: Crea contexto específico para welcome emails.
        """
        # Determinar nombre para mostrar
        if socio_name:
            display_name = socio_name
        elif user.first_name and user.last_name:
            display_name = f"{user.first_name} {user.last_name}".strip()
        else:
            display_name = user.username

        return {
            'user': user,
            'username': user.username,
            'temporary_password': temporary_password,
            'socio_name': display_name,
            'login_url': cls._get_login_url(),
            'support_email': cls._get_support_email(),
            'company_name': cls._get_company_name(),
            'base_url': cls._get_base_url(),
        }

    @classmethod
    def _render_welcome_html_template(cls, context: dict) -> str:
        """Renderiza template HTML de bienvenida."""
        try:
            return render_to_string('emails/welcome_email.html', context)
        except Exception as e:
            logger.error(f"Error rendering welcome HTML template: {e}")
            # Fallback a template básico en caso de error
            return cls._get_fallback_html_template(context)

    @classmethod
    def _render_welcome_text_template(cls, context: dict) -> str:
        """Renderiza template texto de bienvenida."""
        try:
            return render_to_string('emails/welcome_email.txt', context)
        except Exception as e:
            logger.error(f"Error rendering welcome text template: {e}")
            # Fallback a template básico en caso de error
            return cls._get_fallback_text_template(context)

    @classmethod
    def _get_login_url(cls) -> str:
        """Obtiene la URL de login del sistema."""
        return f"{cls._get_base_url()}/accounts/login/"

    @classmethod
    def _generate_welcome_subject(cls) -> str:
        """Genera el subject del email de bienvenida."""
        company_name = cls._get_company_name()
        return f"¡Bienvenido a {company_name}! - Credenciales de Acceso"

    @classmethod
    def _get_fallback_html_template(cls, context: dict) -> str:
        """Template HTML básico en caso de error."""
        return f"""
        <html>
        <body>
            <h2>¡Bienvenido a {context['company_name']}!</h2>
            <p>Hola {context['socio_name']},</p>
            <p>Tu cuenta ha sido creada exitosamente.</p>
            <p><strong>Usuario:</strong> {context['username']}</p>
            <p><strong>Contraseña temporal:</strong> {context['temporary_password']}</p>
            <p>Accede en: <a href="{context['login_url']}">{context['login_url']}</a></p>
            <p>Soporte: {context['support_email']}</p>
        </body>
        </html>
        """

    @classmethod
    def _get_fallback_text_template(cls, context: dict) -> str:
        """Template texto básico en caso de error."""
        return f"""
¡Bienvenido a {context['company_name']}!

Hola {context['socio_name']},

Tu cuenta ha sido creada exitosamente.

Usuario: {context['username']}
Contraseña temporal: {context['temporary_password']}

Accede en: {context['login_url']}
Soporte: {context['support_email']}

---
{context['company_name']}
        """.strip()


class EmailNotificationService(BaseEmailService):
    """
    Servicio para diferentes tipos de notificaciones por email.

    Single Responsibility: Maneja notificaciones específicas.
    Open/Closed: Fácil agregar nuevos tipos de notificación.
    """

    @classmethod
    def send_user_creation_notification_to_staff(
            cls,
            created_user: User,
            created_by: Optional[User] = None,
            socio_name: Optional[str] = None
    ) -> bool:
        """
        Notifica al staff sobre la creación de un nuevo usuario.

        Args:
            created_user: Usuario que fue creado
            created_by: Usuario staff que creó la cuenta
            socio_name: Nombre del socio vinculado

        Returns:
            bool: True si se envió correctamente
        """
        try:
            logger.info(f"Sending staff notification for user creation: {created_user.username}")

            # Obtener lista de destinatarios (superusers y staff)
            staff_emails = cls._get_staff_email_list()

            if not staff_emails:
                logger.warning("No staff emails found for notification")
                return False

            # Construir contexto
            context = cls._build_staff_notification_context(created_user, created_by, socio_name)

            # Generar contenido
            subject = cls._generate_staff_notification_subject(created_user)
            html_content = cls._render_staff_notification_html_template(context)
            plain_content = cls._render_staff_notification_text_template(context)

            # Enviar email
            success = cls._send_email(
                subject=subject,
                html_content=html_content,
                plain_content=plain_content,
                recipient_list=staff_emails
            )

            if success:
                logger.info(f"Staff notification sent successfully to {len(staff_emails)} recipients")
                return True
            else:
                logger.error("Failed to send staff notification")
                return False

        except Exception as e:
            logger.error(f"Error sending staff notification: {str(e)}", exc_info=True)
            return False

    @classmethod
    def _get_staff_email_list(cls) -> List[str]:
        """
        Obtiene lista de emails del personal para notificaciones.

        Returns:
            List[str]: Lista de emails de staff/superusers
        """
        try:
            staff_emails = list(
                User.objects.filter(
                    is_staff=True,
                    is_active=True,
                    email__isnull=False
                ).exclude(
                    email=""
                ).values_list('email', flat=True).distinct()
            )

            logger.debug(f"Found {len(staff_emails)} staff emails for notifications")
            return staff_emails

        except Exception as e:
            logger.error(f"Error getting staff email list: {e}")
            return []

    @classmethod
    def _build_staff_notification_context(
            cls,
            created_user: User,
            created_by: Optional[User],
            socio_name: Optional[str]
    ) -> dict:
        """
        Construye contexto para notificación al staff.

        Factory Pattern: Crea contexto específico para staff notifications.
        """
        return {
            'created_user': created_user,
            'created_by': created_by,
            'socio_name': socio_name,
            'creation_time': created_user.date_joined,
            'admin_url': cls._get_admin_url(),
            'company_name': cls._get_company_name(),
            'base_url': cls._get_base_url(),
        }

    @classmethod
    def _render_staff_notification_html_template(cls, context: dict) -> str:
        """Renderiza template HTML de notificación al staff."""
        try:
            return render_to_string('emails/staff_user_creation_notification.html', context)
        except Exception as e:
            logger.error(f"Error rendering staff notification HTML template: {e}")
            return cls._get_fallback_staff_html_template(context)

    @classmethod
    def _render_staff_notification_text_template(cls, context: dict) -> str:
        """Renderiza template texto de notificación al staff."""
        try:
            return render_to_string('emails/staff_user_creation_notification.txt', context)
        except Exception as e:
            logger.error(f"Error rendering staff notification text template: {e}")
            return cls._get_fallback_staff_text_template(context)

    @classmethod
    def _generate_staff_notification_subject(cls, created_user: User) -> str:
        """Genera subject para notificación al staff."""
        return f"Nuevo usuario creado: {created_user.username}"

    @classmethod
    def _get_fallback_staff_html_template(cls, context: dict) -> str:
        """Template HTML básico para notificación al staff."""
        created_by_info = ""
        if context['created_by']:
            created_by_info = f"<p><strong>Creado por:</strong> {context['created_by'].username}</p>"

        socio_info = ""
        if context['socio_name']:
            socio_info = f"<p><strong>Socio vinculado:</strong> {context['socio_name']}</p>"

        return f"""
        <html>
        <body>
            <h2>Nuevo Usuario Creado</h2>
            <p><strong>Usuario:</strong> {context['created_user'].username}</p>
            <p><strong>Email:</strong> {context['created_user'].email or 'No especificado'}</p>
            <p><strong>Nombre:</strong> {context['created_user'].first_name} {context['created_user'].last_name}</p>
            {socio_info}
            <p><strong>Fecha:</strong> {context['creation_time']}</p>
            {created_by_info}
            <p><a href="{context['admin_url']}">Ir al Panel de Administración</a></p>
        </body>
        </html>
        """

    @classmethod
    def _get_fallback_staff_text_template(cls, context: dict) -> str:
        """Template texto básico para notificación al staff."""
        created_by_info = ""
        if context['created_by']:
            created_by_info = f"Creado por: {context['created_by'].username}\n"

        socio_info = ""
        if context['socio_name']:
            socio_info = f"Socio vinculado: {context['socio_name']}\n"

        return f"""
NUEVO USUARIO CREADO

Usuario: {context['created_user'].username}
Email: {context['created_user'].email or 'No especificado'}
Nombre: {context['created_user'].first_name} {context['created_user'].last_name}
{socio_info}Fecha: {context['creation_time']}
{created_by_info}
Panel de Administración: {context['admin_url']}

---
{context['company_name']}
        """.strip()


class EmailTemplateService(BaseEmailService):
    """
    Servicio para manejo avanzado de templates de email.

    Single Responsibility: Solo maneja renderizado y validación de templates.
    Strategy Pattern: Diferentes estrategias de renderizado según tipo de template.
    """

    @classmethod
    def render_email_template(
            cls,
            template_name: str,
            context: dict,
            fallback_content: Optional[str] = None
    ) -> str:
        """
        Renderiza un template de email con manejo de errores.

        Args:
            template_name: Nombre del template
            context: Contexto para el template
            fallback_content: Contenido fallback en caso de error

        Returns:
            str: Contenido renderizado
        """
        try:
            return render_to_string(template_name, context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")

            if fallback_content:
                return fallback_content

            return cls._get_generic_fallback_template(context)

    @classmethod
    def _get_generic_fallback_template(cls, context: dict) -> str:
        """Template genérico en caso de error."""
        return f"""
        Estimado usuario,

        Este es un mensaje del sistema {cls._get_company_name()}.

        Si tiene alguna consulta, contacte a: {cls._get_support_email()}

        ---
        {cls._get_company_name()}
        """

    @classmethod
    def validate_template_exists(cls, template_name: str) -> bool:
        """
        Verifica si un template existe.

        Args:
            template_name: Nombre del template

        Returns:
            bool: True si existe
        """
        try:
            render_to_string(template_name, {})
            return True
        except Exception:
            return False


class EmailQueueService:
    """
    Servicio para manejo de cola de emails (para implementación futura).

    Single Responsibility: Solo maneja colas de email.
    Open/Closed: Preparado para diferentes backends de cola.
    """

    @classmethod
    def queue_welcome_email(cls, user: User, temp_password: str, socio_name: str = None):
        """
        Encola un email de bienvenida para envío asíncrono.

        Implementar con Celery o Django-RQ para produccion.
        """
        # Por ahora, envío directo
        return WelcomeEmailService.send_welcome_email_with_credentials(
            user=user,
            temporary_password=temp_password,
            socio_name=socio_name
        )

    @classmethod
    def queue_staff_notification(cls, created_user: User, created_by: User = None, socio_name: str = None):
        """
        Encola notificación al staff para envío asíncrono.

        Implementar con Celery o Django-RQ para producción.
        """
        # Por ahora, envío directo
        return EmailNotificationService.send_user_creation_notification_to_staff(
            created_user=created_user,
            created_by=created_by,
            socio_name=socio_name
        )
