# users/views.py

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy


@login_required
def redirect_after_login(request):
    """
    Redirige a los usuarios a su panel correspondiente después de iniciar sesión.
    """
    # 1. Primero, revisamos si el usuario es un superusuario.
    if request.user.is_superuser:
        return redirect('admin:index')

    # 2. Si no es superusuario, pero sí es staff, va al panel de empleados.
    elif request.user.is_staff:
        return redirect('staffpanel:dashboard')

    # 3. En cualquier otro caso (un socio), va a su dashboard.
    else:
        return redirect('userpanel:dashboard')


class CustomPasswordChangeView(PasswordChangeView):
    """
    Vista personalizada que toma control del flujo de éxito del cambio de contraseña
    para garantizar la redirección y la actualización del perfil.
    """
    success_url = reverse_lazy('users:password_change_done')

    def form_valid(self, form):
        response = super().form_valid(form)

        # Lógica personalizada para desactivar la bandera
        if hasattr(self.request.user, 'link'):
            link = self.request.user.link
            if link.must_change_password:
                link.must_change_password = False
                link.save()

        messages.success(self.request, '¡Tu contraseña ha sido actualizada exitosamente!')
        return response
