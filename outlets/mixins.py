"""
Defines the mixins related to the api.
"""
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from outlets.models import Outlet


class GetOutletMixin:
    """Mixin used like a SingleObjectMixin to fetch an outlet"""

    @cached_property
    def outlet(self):
        return get_object_or_404(
            Outlet, pk=self.kwargs.get("outlet", None))

    def get_outlet(self):
        return self.outlet
