from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from users.models import Profile


@login_required
def redirect_after_login(request):
    if request.user.is_staff:
        return redirect('staffpanel:dashboard')
    else:
        return redirect('userpanel:dashboard')


class CustomPasswordChangeView(PasswordChangeView):
    """
    Vista personalizada que toma control total del flujo de éxito
    para garantizar la redirección y la actualización del perfil.
    """
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')

    def form_valid(self, form):
        """
        Este metodo se ejecuta cuando el formulario es válido.
        Nosotros manejaremos todos los pasos aquí.
        """
        # 1. El metodo .save() del formulario guarda la nueva contraseña.
        user = form.save()

        # 2. Esta función crucial actualiza la sesión del usuario para
        #    que no se cierre después de cambiar la contraseña.
        update_session_auth_hash(self.request, user)

        # 3. Ejecutamos nuestra lógica personalizada para desactivar la bandera.
        try:
            profile = self.request.user.profile
            if profile.debe_cambiar_password:
                profile.debe_cambiar_password = False
                profile.save()
        except Profile.DoesNotExist:
            # En caso de que el perfil no exista por alguna razón, no hacemos nada.
            pass

        # 4. Añadimos un mensaje de éxito.
        messages.success(self.request, '¡Tu contraseña ha sido actualizada exitosamente!')

        # 5. Creamos y devolvemos la redirección a la página de éxito.
        return HttpResponseRedirect(self.get_success_url())
