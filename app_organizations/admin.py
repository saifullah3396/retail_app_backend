"""
Registers the models to the admin interface
"""

from django.contrib import admin
from organizations.models import (Organization, OrganizationOwner,
                                  OrganizationUser)

from core.admin import BaseAdmin, list_display_fn, list_filter_fn

from .models import (AppOrganization, AppOrganizationOwner,
                     AppOrganizationUser, OrganizationGroup)


class OrganizationGroupAdmin(BaseAdmin):
    """
    Defines custom admin interface view
    """
    list_display = list_display_fn(())
    list_filter = list_filter_fn(())


class AppOrganizationAdmin(BaseAdmin):
    """
    Defines custom admin interface view
    """
    list_display = list_display_fn(())
    list_filter = list_filter_fn(())


class AppOrganizationUserAdmin(BaseAdmin):
    """
    Defines custom admin interface view
    """
    list_display = list_display_fn(("user", "organization",))


class AppOrganizationOwnerAdmin(BaseAdmin):
    """
    Defines custom admin interface view
    """

    list_display = list_display_fn(("organization_user", "organization",))


admin.site.unregister(Organization)
admin.site.unregister(OrganizationUser)
admin.site.unregister(OrganizationOwner)

admin.site.register(OrganizationGroup, OrganizationGroupAdmin)
admin.site.register(AppOrganization, AppOrganizationAdmin)
admin.site.register(AppOrganizationOwner, AppOrganizationOwnerAdmin)
admin.site.register(AppOrganizationUser, AppOrganizationUserAdmin)
