"""
Defines the REST API views for organizations models.
"""


from rest_framework import exceptions

from app_organizations.views import (BaseOrganizationListGetQuerySet,
                                     BaseOrganizationRetrieveGetQuerySet)
from core.utils import field_not_found_error
from outlets.mixins import GetOutletMixin
from outlets.models import Outlet


class BaseOutletListGetQuerySet(
        BaseOrganizationListGetQuerySet, GetOutletMixin):
    def _get_list_queryset(self, model=None):
        outlet = self.validate_kwargs()

        if model:
            return model.objects.filter(outlet=outlet.id)
        else:
            return self.model.objects.filter(outlet=outlet.id)

    def validate_kwargs(self):
        organization = super().validate_kwargs()
        outlet = self.get_outlet()
        if outlet.organization != organization:
            raise exceptions.ValidationError({
                "outlet": field_not_found_error()
            })
        return outlet


class BaseOutletRetrieveGetQuerySet(
        BaseOrganizationRetrieveGetQuerySet, GetOutletMixin):

    def _get_retrieve_queryset(self, model=None):
        outlet = self.validate_kwargs()

        if model:
            return model.objects.filter(outlet=outlet.id)
        else:
            return self.model.objects.filter(outlet=outlet.id)

    def validate_kwargs(self):
        organization = super().validate_kwargs()
        outlet = self.get_outlet()
        if outlet.organization != organization:
            raise exceptions.ValidationError({
                "outlet": field_not_found_error()
            })
        return outlet
