from core.views import CoreListGetQuerySet, CoreRetrieveGetQueryset

from .mixins import GetOrganizationMixin


class BaseOrganizationListGetQuerySet(
        CoreListGetQuerySet, GetOrganizationMixin):
    def _get_list_queryset(self, model=None):
        organization = self.validate_kwargs()
        if model:
            return model.objects.filter(organization=organization.id)
        else:
            return self.model.objects.filter(organization=organization.id)

    def validate_kwargs(self):
        return self.get_organization()


class BaseOrganizationRetrieveGetQuerySet(
        CoreRetrieveGetQueryset, GetOrganizationMixin):
    def _get_retrieve_queryset(self, model=None):
        organization = self.validate_kwargs()
        if model:
            return model.objects.filter(organization=organization.id)
        else:
            return self.model.objects.filter(organization=organization.id)

    def validate_kwargs(self):
        return self.get_organization()
