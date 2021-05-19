"""
Defines the mixins related to the api.
"""
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from core.utils import get_organization_model

ORGANIZATION_MODEL = get_organization_model()


class GetOrganizationMixin:
    """Mixin used like a SingleObjectMixin to fetch an organization"""

    org_model = ORGANIZATION_MODEL
    org_context_name = "organization"

    def __init__(self):
        self.get_context_data()

    def get_org_model(self):
        return self.org_model

    def get_context_data(self, **kwargs):
        kwargs.update({self.org_context_name: self.organization})

    @cached_property
    def organization(self):
        organization_pk = self.kwargs.get("organization_pk", None)
        print("ORG OB:, ", get_object_or_404(
            self.get_org_model(), pk=organization_pk))
        return get_object_or_404(self.get_org_model(), pk=organization_pk)

    def get_object(self):
        return self.organization

    get_organization = get_object
