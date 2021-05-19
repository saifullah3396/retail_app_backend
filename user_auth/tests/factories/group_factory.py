"""
Defines the base functionality for unit tests generation for our applications.
"""


import factory

from user_auth.models import DefaultUserGroups, UserGroup

# This is for reference on how to make factory for one to one group
# relationships

# @factory.django.mute_signals(post_save)
# class UserGroupFactory(factory.django.DjangoModelFactory):
#     """
#     Generates a factory for user groups
#     """
#     class Meta:
#         model = UserGroup
#         django_get_or_create = ('group',)

#     authority = factory.fuzzy.FuzzyChoice([0, 1, 2, 3])
#     group = factory.SubFactory(
#         'users.tests.factories.group_factory.GroupFactory', info=None)


# @factory.django.mute_signals(post_save)
# class GroupFactory(factory.django.DjangoModelFactory):
#     """
#     Generates a factory for user groups
#     """
#     class Meta:
#         model = Group
#         django_get_or_create = ('name',)

#     name = factory.Sequence(lambda n: 'group%d' % n)
#     info = factory.RelatedFactory(
#         UserGroupFactory, factory_related_name='group')

class UserGroupFactory(factory.django.DjangoModelFactory):
    """
    Generates a factory for user groups
    """
    class Meta:
        model = UserGroup
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: 'group%d' % n)

    @factory.sequence
    def authority(n):
        return n if n <= 3 else 3


def generate_group_factory():
    """
    Generates factory data that can be used in test cases
    """
    # generate user groups to assign to users
    groups = [
        UserGroupFactory(name=g.name, authority=g.value)
        for g in DefaultUserGroups]
    groups_dict = {}
    for group in groups:
        groups_dict[group.name] = group
    return groups_dict
