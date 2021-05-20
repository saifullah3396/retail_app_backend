"""
Defines the common utility functions used in our applications.
"""

from django.apps import apps as django_apps
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.utils.cache import get_cache_key
from django.utils.module_loading import import_string
from organizations.models import Organization
from rest_framework import exceptions, serializers

from backend import settings


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


def filter_queryset_by_lookup_list(query_set, lookup_list, lookup_param):
    """
    Filters a queryset by th given list of lookup params
    """
    query = '{}__in'.format(lookup_param)
    return query_set.filter(**{query: lookup_list})


def exclude_queryset_by_lookup_list(query_set, lookup_list, lookup_param):
    """
    Filters a queryset by excluding the given list of lookup params
    """
    query = '{}__in'.format(lookup_param)
    return query_set.exclude(**{query: lookup_list})


def filter_objects_by_lookup_list(objects, lookup_list, lookup_param):
    """
    Filters the object by lookup list. If all lookup params in the list do not
    match, a not found exception is raised.
    """
    try:
        filtered_objects = filter_queryset_by_lookup_list(
            objects, lookup_list, lookup_param)

        # make sure all the given ids are inside filtered objects,
        # otherwise raise a validation error
        if len(filtered_objects) != len(lookup_list):
            raise exceptions.NotFound(
                {
                    'id': 'The following requested ids are invalid: {}'.format(
                        exclude_queryset_by_lookup_list(
                            objects, lookup_list, lookup_param).values_list(
                            lookup_param, flat=True))
                })
        return filtered_objects
    except:
        raise exceptions.ValidationError(
            detail={lookup_param: "Invalid list of parameters."})


def get_lookup_list(request, lookup_param):
    """
    Returns the list of ids from API request.
    """
    return request.query_params.getlist(lookup_param)


def get_user_group_model():
    try:
        return django_apps.get_model(settings.USER_GROUP_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "USER_GROUP_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "USER_GROUP_MODEL refers to model '%s' that has not been installed" % settings.USER_GROUP_MODEL
        )


def get_organization_model():
    try:
        return django_apps.get_model(settings.ORGANIZATION_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "ORGANIZATION_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "ORGANIZATION_MODEL refers to model '%s' that has not been installed" % settings.ORGANIZATION_MODEL
        )


def get_organization_user_model():
    try:
        return django_apps.get_model(settings.ORGANIZATION_USER_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "ORGANIZATION_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "ORGANIZATION_USER_MODEL refers to model '%s' that has not been installed" % settings.ORGANIZATION_USER_MODEL
        )


def get_organization_owner_model():
    try:
        return django_apps.get_model(settings.ORGANIZATION_OWNER_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "ORGANIZATION_OWNER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "ORGANIZATION_OWNER_MODEL refers to model '%s' that has not been installed" % settings.ORGANIZATION_OWNER_MODEL
        )


def get_organization_group_model():
    try:
        return django_apps.get_model(settings.ORGANIZATION_GROUP_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "ORGANIZATION_GROUP_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "ORGANIZATION_GROUP_MODEL refers to model '%s' that has not been installed" % settings.ORGANIZATION_GROUP_MODEL
        )


def get_organization_auth_backend():
    auth_backend = import_string(settings.ORGANIZATION_USER_AUTH_BACKEND)
    if not auth_backend:
        raise ImproperlyConfigured(
            'No authentication backends have been defined. Does '
            'ORGANIZATION_USER_AUTH_BACKEND contain anything?'
        )
    return auth_backend
