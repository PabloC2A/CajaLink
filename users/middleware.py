# users/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from .models import UserSocioLink


class ForcePasswordChangeMiddleware:
    """
    Este middleware comprueba si el usuario autenticado necesita cambiar su
    contraseña y lo redirige si es necesario.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and not request.user.is_superuser:
            try:
                link = request.user.link
                password_change_url = reverse('users:password_change')

                if link.must_change_password and request.path != password_change_url:
                    return redirect(password_change_url)
            except UserSocioLink.DoesNotExist:
                # Si no hay vínculo, no se aplica la regla.
                pass

        return response
