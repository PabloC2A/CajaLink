# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


# Define un 'inline' para el modelo Profile.
# Esto permite que el perfil se muestre y edite en la página del usuario.
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'perfiles'


# Define un nuevo UserAdmin que incluye el ProfileInline.
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


# Vuelve a registrar el modelo User con nuestra configuración personalizada.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
