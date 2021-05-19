"""
Defines the base functionality for unit tests generation for our applications.
"""


import factory
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from rest_framework_jwt.settings import api_settings

from core.tests.utils import generate_test_image, generate_token
from user_auth.models import DefaultUserGroups, UserGroup
from user_auth.tests.factories.group_factory import (UserGroupFactory,
                                                     generate_group_factory)

# define payload handler for generating JWT token in tests
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER

# define encode handler for generating JWT token in tests
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

# use JWT authentication tokens?
JWT_AUTH = True

# get user model
USER_MODEL = get_user_model()


class AppUserFactoryBase(factory.django.DjangoModelFactory):
    """
    Base user factory
    """
    class Meta:
        model = USER_MODEL
        django_get_or_create = ('username',)

    @ factory.post_generation
    def groups(self, create, extracted, **kwargs):
        """
        Adds given user groups to user many-to-many groups relation
        """
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                # pylint: disable=no-member
                self.groups.add(group)


class EmailAddressFactory(factory.django.DjangoModelFactory):
    """
    Generates a factory for user groups
    """
    class Meta:
        model = EmailAddress
        django_get_or_create = ('email',)

    user = factory.SubFactory(AppUserFactoryBase)
    verified = True
    primary = True


class SuperUserFactory(AppUserFactoryBase):
    """
    Generates a factory for super users
    """
    first_name = 'admin'
    last_name = 'admin'
    username = 'admin'
    email = factory.Sequence(lambda n: 'admin%d@admin.com' % n)
    password = 'admin'
    avatar = factory.LazyAttribute(lambda _: generate_test_image('avatar'))

    is_staff = True
    is_superuser = True


class AppUserFactory(AppUserFactoryBase):
    """
    Generates a factory for normal app users
    """
    class Meta:
        model = USER_MODEL
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: 'username%d' % n)
    first_name = factory.LazyAttribute(lambda obj: '%s_first' % obj.username)
    last_name = factory.LazyAttribute(lambda obj: '%s_last' % obj.username)
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.username)
    password = 'Abcd1234@'
    avatar = factory.LazyAttribute(lambda _: generate_test_image('avatar'))


def generate_user_factory(num_users=2):
    """
    Generates factory data that can be used in test cases
    """
    # generate superuser and users with different groups
    AppUserFactoryBase.reset_sequence()
    groups = generate_group_factory()

    users = []
    users.append(SuperUserFactory.create(
        groups=(groups[DefaultUserGroups.SUPER_USER.name],)))
    users.extend(AppUserFactory.create_batch(
        num_users,
        groups=(groups[DefaultUserGroups.FREE_USER.name],)))

    # generate verified email addresses
    for user in users:
        EmailAddressFactory(user=user, email=user.email)

    # generate user tokens
    tokens = {}
    for user in users:
        tokens[user] = generate_token(user)

    users_dict = {}
    for user in users:
        users_dict[user.id] = user
    return users_dict, tokens
