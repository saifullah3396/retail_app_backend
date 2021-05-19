from core.views import CoreListGetQuerySet, CoreRetrieveGetQueryset

from .mixins import GetOrganizationMixin


class BaseOrganizationListGetQuerySet(
        CoreListGetQuerySet, GetOrganizationMixin):
    def _get_list_queryset(self):
        print('organization', self.get_organization().id)
        return self.model.objects.filter(organization=self.get_organization())


class BaseOrganizationRetrieveGetQuerySet(
        CoreRetrieveGetQueryset, GetOrganizationMixin):
    def _get_retrieve_queryset(self):
        return self.model.objects.filter(organization=self.get_organization())
