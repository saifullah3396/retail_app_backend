from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import AppUserCreationForm, AppUserChangeForm
from .models import AppUser


class AppUserAdmin(UserAdmin):
    """
    Provides a custom user view for admin site
    """

    add_form = AppUserCreationForm
    form = AppUserChangeForm
    model = AppUser
    list_display = ('username', 'email', 'is_staff', 'is_active',)
    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': (
                    'avatar',
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2',
                    'organization',
                )
            }
        ),
        (
            'Permissions', {
                'fields': (
                    'groups',
                    'authorized_locations',
                )
            }
        ),
    )
    fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': (
                    'avatar',
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'is_staff',
                    'is_active',
                    'is_superuser',
                    'organization',
                )
            }
        ),
        (
            'Permissions', {
                'fields': (
                    'groups',
                    'user_permissions',
                    'authorized_locations',
                )
            }
        ),
    )

    filter_horizontal = ('groups', 'authorized_locations', 'user_permissions')


admin.site.register(AppUser, AppUserAdmin)
