from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .forms import CustomUserAdminCreationForm, CustomUserAdminChangeForm
from .models import UserSocioLink


class UserAdmin(BaseUserAdmin):
    """
    Extiende el UserAdmin por defecto para usar nuestros formularios personalizados
    y definir explícitamente los campos que se muestran en cada vista.
    """
    form = CustomUserAdminChangeForm
    add_form = CustomUserAdminCreationForm

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "password1",
                    "password2",
                    "socio",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserSocioLink)
class UserSocioLinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'socio')
    raw_id_fields = ('user', 'socio')  # Optimización para búsquedas
