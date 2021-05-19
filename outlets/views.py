"""
Defines the REST API views for organizations models.
"""


from rest_framework import exceptions

from app_organizations.mixins import GetOrganizationMixin
from app_organizations.views import (BaseOrganizationListGetQuerySet,
                                     BaseOrganizationRetrieveGetQuerySet)
from core import views
from core.utils import field_not_found_error
from outlets.mixins import GetOutletMixin
from outlets.models import Outlet


class BaseOutletListGetQuerySet(
        BaseOrganizationListGetQuerySet, GetOutletMixin):
    def _get_list_queryset(self, model=None):
        valid_outlets = super()._get_list_queryset(model=Outlet)
        outlet = self.get_outlet()
        if not valid_outlets.filter(id=outlet.id).exists():
            raise exceptions.ValidationError({
                "outlet_pk": field_not_found_error()
            })

        if model:
            return model.objects.filter(outlet=outlet.id)
        else:
            return self.model.objects.filter(outlet=outlet.id)


class BaseOutletRetrieveGetQuerySet(
        BaseOrganizationRetrieveGetQuerySet, GetOutletMixin):

    def _get_retrieve_queryset(self, model=None):
        valid_outlets = super()._get_retrieve_queryset(model=Outlet)
        outlet = self.get_outlet()
        if not valid_outlets.filter(id=outlet.id).exists():
            raise exceptions.ValidationError({
                "outlet_pk": field_not_found_error()
            })

        if model:
            return model.objects.filter(outlet=outlet.id)
        else:
            return self.model.objects.filter(outlet=outlet.id)
