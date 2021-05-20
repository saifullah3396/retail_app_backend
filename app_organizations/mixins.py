"""
Defines the mixins related to the api.
"""
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from core.utils import get_organization_model

ORGANIZATION_MODEL = get_organization_model()


class GetOrganizationMixin:
    """Mixin used like a SingleObjectMixin to fetch an organization"""

    @cached_property
    def organization(self):
        return get_object_or_404(
            ORGANIZATION_MODEL, pk=self.kwargs.get("organization", None))

    def get_organization(self):
        return self.organization
