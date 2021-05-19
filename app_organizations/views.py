from core.views import CoreListGetQuerySet, CoreRetrieveGetQueryset

from .mixins import GetOrganizationMixin


class BaseOrganizationListGetQuerySet(
        CoreListGetQuerySet, GetOrganizationMixin):
    def _get_list_queryset(self, model=None):
        organization = self.get_organization()
        if model:
            return model.objects.filter(organization=organization)
        else:
            return self.model.objects.filter(organization=organization)


class BaseOrganizationRetrieveGetQuerySet(
        CoreRetrieveGetQueryset, GetOrganizationMixin):
    def _get_retrieve_queryset(self, model=None):
        organization = self.get_organization()
        if model:
            return model.objects.filter(organization=organization)
        else:
            return self.model.objects.filter(organization=organization)
