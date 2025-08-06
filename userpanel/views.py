# userpanel/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from banking.models import Account, Transaction


class DashboardView(LoginRequiredMixin, ListView):
    """
    Muestra el dashboard principal del socio con una lista de sus cuentas.
    Hereda de ListView para manejar la lista de objetos automáticamente.
    """
    model = Account
    template_name = 'userpanel/dashboard.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        """
        Sobrescribe el metodo base para devolver solo las cuentas
        que pertenecen al usuario actualmente autenticado.
        """
        # Usamos self.request.user para obtener el usuario logueado.
        return Account.objects.filter(socio=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Añade el nombre completo del usuario al contexto para usarlo en la plantilla.
        """
        context = super().get_context_data(**kwargs)
        context['full_name'] = self.request.user.get_full_name() or self.request.user.username
        return context


class AccountDetailView(LoginRequiredMixin, DetailView):
    """
    Muestra el detalle y el historial de transacciones de una cuenta específica.
    Hereda de DetailView para manejar la obtención de un objeto único.
    """
    model = Account
    template_name = 'userpanel/account_detail.html'
    context_object_name = 'account'

    def get_queryset(self):
        """
        Asegura que un usuario solo pueda acceder al detalle de sus propias cuentas.
        Esta es una medida de seguridad crucial.
        """
        return Account.objects.filter(socio=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Añade la lista de transacciones asociadas a la cuenta al contexto.
        """
        context = super().get_context_data(**kwargs)
        # El objeto 'account' ya está en el contexto gracias a DetailView.
        account = self.get_object()
        context['transactions'] = account.transactions.all()
        return context
