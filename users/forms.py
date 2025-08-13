from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from legacy_models.models import Socio
from .models import UserSocioLink


class CustomUserAdminCreationForm(UserCreationForm):
    """
    Formulario para CREAR usuarios en el admin. Hereda de UserCreationForm
    para manejar las contraseñas de forma segura y profesional.
    """
    socio = forms.ModelChoiceField(
        queryset=Socio.objects.filter(usersociolink__isnull=True),
        required=False,
        label="Vincular a Socio (Opcional)",
        help_text="Seleccione un socio. Deje en blanco si crea un usuario de personal."
    )

    # Campos para permisos
    is_staff = forms.BooleanField(required=False, initial=False, label="Es personal (Staff)")
    is_superuser = forms.BooleanField(required=False, initial=False, label="Superusuario")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "socio", "is_staff", "is_superuser")

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)

        # Setear permisos según los datos del formulario
        user.is_staff = self.cleaned_data.get('is_staff', False)
        user.is_superuser = self.cleaned_data.get('is_superuser', False)

        if commit:
            user.save()

        socio_seleccionado = self.cleaned_data.get('socio')
        if socio_seleccionado:
            link, created = UserSocioLink.objects.get_or_create(user=user)
            link.socio = socio_seleccionado
            link.save()

        return user


class CustomUserAdminChangeForm(UserChangeForm):
    """
    Formulario para EDITAR usuarios existentes en el admin.
    """

    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'
