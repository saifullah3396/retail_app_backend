"""
Defines the base functionality for unit tests generation for our applications.
"""


import factory

from app_organizations.models import (DefaultOrganizationGroups,
                                      OrganizationGroup)
from app_organizations.tests.factories import app_organization_factory

ORGANIZATION_FACTORY = app_organization_factory.AppOrganizationFactory


class OrganizationGroupFactory(factory.django.DjangoModelFactory):
    """
    Generates a factory for organization groups
    """
    class Meta:
        model = OrganizationGroup
        django_get_or_create = ('name', 'organization')

    name = factory.Sequence(lambda n: 'group%d' % n)
    organization = factory.SubFactory(ORGANIZATION_FACTORY)

    @factory.sequence
    def authority(n):
        return n if n <= 3 else 3


def generate_org_groups_factory(orgs):
    """
    Generates organization groups
    """

    org_groups_dict = {}

    # assign users to organizations
    # for org in orgs:
    print(orgs)
    print('org groups', OrganizationGroup.objects.filter(
        organization=list(orgs)[0]))
    OrganizationGroupFactory(
        name=DefaultOrganizationGroups.OWNER.name,
        authority=DefaultOrganizationGroups.OWNER.value,
        organization=list(orgs)[0])
    # org_groups_dict[org] = [
    #     OrganizationGroupFactory(
    #         name=g.name,
    #         authority=g.value,
    #         organization=org)
    #     for g in DefaultOrganizationGroups]

    return org_groups_dict
