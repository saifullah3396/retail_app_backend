from django.contrib import admin

from .models import Organization, SubOrganization

admin.site.register(Organization)
admin.site.register(SubOrganization)
