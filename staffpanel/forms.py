# staffpanel/forms.py

from django import forms
from django.contrib.auth.models import User


class WebUserLinkForm(forms.Form):
    """
    Formulario para crear las credenciales de un usuario web para un Socio
    que ya existe en la base de datos legacy.
    """
    username = forms.CharField(
        label="Nombre de Usuario",
        max_length=150,
        help_text="Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente."
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        required=False,
        help_text="Opcional. Se usará el del socio si se deja en blanco."
    )

    def clean_username(self):
        """
        Valida que el nombre de usuario no exista en el sistema Django.
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        """
        Valida que el correo, si se proporciona, no esté ya en uso.
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email
