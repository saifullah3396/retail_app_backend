"""
Defines the mixins related to the api.
"""
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from locations.models import Block, Floor, OutletLocation


class GetOutletLocationMixin:
    """Mixin used like a SingleObjectMixin to fetch an location"""

    @cached_property
    def location(self):
        return get_object_or_404(
            OutletLocation, pk=self.kwargs.get("location", None))

    def get_location(self):
        return self.location


class GetFloorMixin:
    """Mixin used like a SingleObjectMixin to fetch an floor"""

    @cached_property
    def floor(self):
        return get_object_or_404(
            Floor, pk=self.kwargs.get("floor", None))

    def get_floor(self):
        return self.floor


class GetBlockMixin:
    """Mixin used like a SingleObjectMixin to fetch an block"""

    @cached_property
    def block(self):
        return get_object_or_404(
            Block, pk=self.kwargs.get("block", None))

    def get_block(self):
        return self.block
