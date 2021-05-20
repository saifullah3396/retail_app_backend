"""
Defines the REST API views for organizations models.
"""


from rest_framework import exceptions

from core.utils import field_not_found_error
from locations.mixins import (GetBlockMixin, GetFloorMixin,
                              GetOutletLocationMixin)
from locations.models import Block, Floor, OutletLocation
from outlets.views import (BaseOutletListGetQuerySet,
                           BaseOutletRetrieveGetQuerySet)


class BaseOutletLocationListGetQuerySet(
        BaseOutletListGetQuerySet, GetOutletLocationMixin):
    def _get_list_queryset(self, model=None):
        location = self.validate_kwargs()

        if model:
            return model.objects.filter(location=location.id)
        else:
            return self.model.objects.filter(location=location.id)

    def validate_kwargs(self):
        outlet = super().validate_kwargs()
        location = self.get_location()
        if location.outlet.id != outlet.id:
            raise exceptions.ValidationError({
                "location": field_not_found_error()
            })
        return location


class BaseOutletLocationRetrieveGetQuerySet(
        BaseOutletRetrieveGetQuerySet, GetOutletLocationMixin):

    def _get_retrieve_queryset(self, model=None):
        location = self.validate_kwargs()

        if model:
            return model.objects.filter(location=location.id)
        else:
            return self.model.objects.filter(location=location.id)

    def validate_kwargs(self):
        outlet = super().validate_kwargs()
        location = self.get_location()
        if location.outlet.id != outlet.id:
            raise exceptions.ValidationError({
                "location": field_not_found_error()
            })
        return location


class BaseFloorListGetQuerySet(
        BaseOutletLocationListGetQuerySet, GetFloorMixin):
    def _get_list_queryset(self, model=None):
        floor = self.validate_kwargs()

        if model:
            return model.objects.filter(floor=floor.id)
        else:
            return self.model.objects.filter(floor=floor.id)

    def validate_kwargs(self):
        location = super().validate_kwargs()
        floor = self.get_floor()
        if floor.location.id != location.id:
            raise exceptions.ValidationError({
                "floor": field_not_found_error()
            })
        return floor


class BaseFloorRetrieveGetQuerySet(
        BaseOutletLocationRetrieveGetQuerySet, GetFloorMixin):

    def _get_retrieve_queryset(self, model=None):
        floor = self.validate_kwargs()

        if model:
            return model.objects.filter(floor=floor.id)
        else:
            return self.model.objects.filter(floor=floor.id)

    def validate_kwargs(self):
        location = super().validate_kwargs()
        floor = self.get_floor()
        if floor.location.id != location.id:
            raise exceptions.ValidationError({
                "floor": field_not_found_error()
            })
        return floor


class BaseBlockListGetQuerySet(
        BaseOutletLocationListGetQuerySet, GetBlockMixin):
    def _get_list_queryset(self, model=None):
        block = self.validate_kwargs()

        if model:
            return model.objects.filter(block=block.id)
        else:
            return self.model.objects.filter(block=block.id)

    def validate_kwargs(self):
        floor = super().validate_kwargs()
        block = self.get_block()
        if block.floor.id != floor.id:
            raise exceptions.ValidationError({
                "block": field_not_found_error()
            })
        return block


class BaseBlockRetrieveGetQuerySet(
        BaseOutletLocationRetrieveGetQuerySet, GetBlockMixin):

    def _get_retrieve_queryset(self, model=None):
        block = self.validate_kwargs()

        if model:
            return model.objects.filter(block=block.id)
        else:
            return self.model.objects.filter(block=block.id)

    def validate_kwargs(self):
        floor = super().validate_kwargs()
        block = self.get_block()
        if block.floor.id != floor.id:
            raise exceptions.ValidationError({
                "block": field_not_found_error()
            })
        return block
