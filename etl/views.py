# etl/views.py

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import connection, transaction
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import SqlUploadForm


class StaffRequiredMixin(UserPassesTestMixin):
    """
    Mixin que verifica que el usuario sea parte del personal (staff).
    """

    def test_func(self):
        return self.request.user.is_staff


class ETLUploadView(StaffRequiredMixin, FormView):
    """
    Maneja la subida y ejecución de un archivo SQL para el ETL.
    La ejecución se realiza de forma segura dentro de una transacción atómica.
    """
    template_name = 'etl/upload.html'
    form_class = SqlUploadForm
    success_url = reverse_lazy('etl:upload')

    def form_valid(self, form):
        sql_file = self.request.FILES['sql_file']
        sql_content = sql_file.read().decode('utf-8')

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.executescript(sql_content)
            messages.success(self.request, 'El script SQL se ha ejecutado exitosamente.')
        except Exception as e:
            messages.error(self.request, f'Ocurrió un error al ejecutar el script: {e}')

        return super().form_valid(form)
