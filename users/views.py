# users/views.py

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def redirect_after_login(request):
    """
    Redirige a los usuarios a su panel correspondiente después de iniciar sesión.
    """
    if request.user.is_staff:
        return redirect('staffpanel:dashboard')
    else:
        return redirect('userpanel:dashboard')
