# users/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from users.models import Profile


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and not request.user.is_superuser:
            try:
                profile = request.user.profile
                # CORRECCIÓN AQUÍ: Usamos el nombre completo de la URL 'users:password_change'
                password_change_url = reverse('users:password_change')

                if profile.debe_cambiar_password and request.path != password_change_url:
                    # CORRECCIÓN AQUÍ: Redirigimos al nombre completo de la URL
                    return redirect('users:password_change')
            except Profile.DoesNotExist:
                pass

        return response
