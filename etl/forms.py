# etl/forms.py

from django import forms


class SqlUploadForm(forms.Form):
    """
    Formulario para validar la subida de un archivo con extensión .sql.
    """
    sql_file = forms.FileField(
        label="Archivo de Sincronización (.sql)",
        help_text="Selecciona el archivo 'output.sql' generado por el script local.",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.sql'})
    )
