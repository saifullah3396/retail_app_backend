"""
Defines the base functionality for unit tests generation for our applications.
"""


import factory

from app_organizations.models import (AppOrganization, AppOrganizationOwner,
                                      AppOrganizationUser)
from core.tests.utils import generate_test_image
from users.tests.factories import user_factory


class AppOrganizationFactory(factory.django.DjangoModelFactory):
    """
    Organization factory
    """
    class Meta:
        model = AppOrganization
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: 'organization%d' % n)
    avatar = factory.LazyAttribute(lambda _: generate_test_image('avatar'))


class AppOrganizationUserFactory(factory.django.DjangoModelFactory):
    """
    Organization User factory
    """
    class Meta:
        model = AppOrganizationUser

    user = factory.SubFactory(user_factory.AppUserFactory)
    organization = factory.SubFactory(AppOrganizationFactory)


class AppOrganizationOwnerFactory(factory.django.DjangoModelFactory):
    """
    Organization User factory
    """
    class Meta:
        model = AppOrganizationOwner

    organization_user = factory.SubFactory(AppOrganizationUserFactory)
    organization = factory.SubFactory(AppOrganizationFactory)


def generate_org_factory(num_orgs=10):
    """
    Generates organizations
    """

    # generate some organizations
    orgs = []
    orgs.extend(
        AppOrganizationFactory.create_batch(num_orgs))

    orgs_dict = {}
    for org in orgs:
        orgs_dict[org.id] = org
    return orgs_dict


def generate_org_users_factory(users, orgs):
    """
    Generates organization users
    """

    org_users_dict = {}

    # assign users to organizations
    for org in orgs:
        org_users_dict[org] = []
        for user in users:
            if user.is_superuser:  # don't add staff to any organization
                continue

            # assign users to organizations
            org_users_dict[org].append(org.add_user(user))

    return org_users_dict
