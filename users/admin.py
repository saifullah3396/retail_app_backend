from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import AppUserCreationForm, AppUserChangeForm
from .models import AppUser


class AppUserAdmin(UserAdmin):
    add_form = AppUserCreationForm
    form = AppUserChangeForm
    model = AppUser
    list_display = ('username', 'email', 'is_staff', 'is_active',)
    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                    'organization',
                    'sub_organization',
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
                    'username',
                    'email',
                    'is_staff',
                    'is_active',
                    'is_superuser',
                    'organization',
                    'sub_organization',
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

    filter_horizontal = ('groups', 'authorized_locations',)

    def clean(self):
        print('clean main')
        print(cleaned_data.get('groups'))


admin.site.register(AppUser, AppUserAdmin)
