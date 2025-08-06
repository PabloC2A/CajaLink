# staffpanel/forms.py
from django import forms


class SqlUploadForm(forms.Form):
    sql_file = forms.FileField(label="Archivo de Sincronización (.sql)")
