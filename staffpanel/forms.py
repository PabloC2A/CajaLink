# staffpanel/forms.py
from django import forms
from django.contrib.auth.models import User
from users.models import Profile


class SqlUploadForm(forms.Form):
    sql_file = forms.FileField(label="Archivo de Sincronización (.sql)")


class SocioCreationForm(forms.Form):
    first_name = forms.CharField(label="Nombres", max_length=150)
    last_name = forms.CharField(label="Apellidos", max_length=150)
    email = forms.EmailField(label="Correo Electrónico")
    username = forms.CharField(label="Nombre de Usuario", max_length=150)
    cedula = forms.CharField(label="Cédula", max_length=10)

    def clean_username(self):
        """Valida que el nombre de usuario no exista."""
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        """Valida que el correo electrónico no exista."""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_cedula(self):
        """Valida que la cédula no exista."""
        cedula = self.cleaned_data['cedula']
        if Profile.objects.filter(cedula=cedula).exists():
            # Esta validación previene el IntegrityError
            raise forms.ValidationError("Esta cédula ya está registrada.")
        return cedula
