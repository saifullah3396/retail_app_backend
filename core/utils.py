"""
Defines the common utility functions used in our applications.
"""

from django.contrib.auth.models import Group
from rest_framework import exceptions, serializers

from core.permissions import UserGroups
from locations.models import Location
from organizations.models import Organization

MAC_ADDRESS_VALIDATOR_REGEX = '([0-9a-fA-F]{2}[:]){5}([0-9a-fA-F]{2})'


class WritableSerializerMethodField(serializers.SerializerMethodField):
    """A serializer method field that allows both read/write operations.

    Args:
        method_name (string): Name of the method field
    """

    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        self.setter_method_name = kwargs.pop('setter_method_name', None)
        self.deserializer_field = kwargs.pop('deserializer_field')

        kwargs['source'] = '*'
        super().__init__(**kwargs)

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        if not self.setter_method_name:
            self.setter_method_name = f'set_{field_name}'

    def to_internal_value(self, data):
        value = self.deserializer_field.to_internal_value(data)
        method = getattr(self.parent, self.setter_method_name)
        return method(value)


def get_user_from_serializer(serializer, raise_exception=False):
    """
    Returns the user from serializer context. Raises permission denied error
    if user is not found.
    """

    # get user requesting for a new registration
    request_user = None
    request = serializer.context.get("request")
    if request and hasattr(request, "user"):
        request_user = request.user
    else:
        if raise_exception:
            # raise unauthorized error if user is not found
            # most probably this will never get called
            raise exceptions.PermissionDenied()
    return request_user


def is_in_group(user, group_name):
    """
    Takes a user and a group name, and returns True if the user is in that
    group.
    """
    try:
        return Group.objects.get(name=group_name).\
            user_set.filter(id=user.id).exists()
    except Group.DoesNotExist:
        return None


def get_fn_by_group(user, group_to_fn_map):
    """
    Returns the function to be called for the user group the user is in
    given the user group to function map.
    """
    get_queryset_fn = None
    for group in UserGroups:
        if is_in_group(user, group.name):
            get_queryset_fn = group_to_fn_map.get(group, None)
            break
    if get_queryset_fn is None:
        raise exceptions.PermissionDenied()
    return get_queryset_fn


def is_organization_admin(user):
    """
    Returns true if the user is in ORGANIZATION_ADMIN_GROUP user group.
    """
    return is_in_group(user, UserGroups.ORGANIZATION_ADMIN_GROUP.name)


def is_employee(user):
    """
    Returns true if the user is in EMPLOYEE_GROUP user group.
    """
    return is_in_group(user, UserGroups.EMPLOYEE_GROUP.name)


def filter_queryset_by_id_list(query_set, id_list):
    """
    Filters a queryset by th given list of ids
    """
    return query_set.filter(id__in=id_list)


def exclude_queryset_by_id_list(query_set, id_list):
    """
    Filters a queryset by excluding the given list of ids
    """
    return query_set.exclude(id__in=id_list)


def get_staff_authorized_organizations():
    """
    Returns the locations authorized to staff user
    """
    Organization.objects.all()


def get_organization_admin_authorized_organizations(user, include_self=True):
    """
    Returns the locations authorized to organization admin user
    """
    return user.organization.get_descendants(include_self=include_self)


def get_employee_authorized_organizations(user):
    """
    Returns the locations authorized to employee user
    """
    return [user.organization]


def get_staff_authorized_locations():
    """
    Returns the locations authorized to staff user
    """
    Location.objects.all()


def get_organization_admin_authorized_locations(user, include_self=True):
    """
    Returns the locations authorized to organization admin user
    """
    organizations_tree = user.organization.get_descendants(
        include_self=include_self)
    return Location.objects.filter(organization__in=organizations_tree)


def get_employee_authorized_locations(user):
    """
    Returns the locations authorized to employee user
    """
    return user.authorized_locations.all()


def get_object_by_id(model, object_id):
    """
    Returns the model for given id
    """
    try:
        return model.objects.get(id=object_id)
    except model.DoesNotExist:
        return None


def field_not_found_error():
    """Generates error message for when a field does not exist."""
    return "Field not found."


def field_with_id_not_found_error(field_id):
    """Generates error message for when a field does not exist."""
    return "Field with id={} not found.".format(field_id)


def field_required_error():
    """Generates error message for when a field is required."""
    return "This is a required field."


def field_invalid_error():
    """Generates error message for when a field is invalid."""
    return "Invalid field."
