"""
Defines the permissions used in this application.
"""

import copy

from django.contrib.auth import get_user_model

from app_organizations.models import DefaultOrganizationGroups
from core.utils import (get_organization_group_model, get_organization_model,
                        get_organization_user_model, get_user_group_model)
# from locations.models import Block, Floor, Location
from outlets.models import Outlet, OutletUser
from user_auth.models import DefaultUserGroups

USER_MODEL = get_user_model()
USER_GROUP_MODEL = get_user_group_model()
ORGANIZATION_MODEL = get_organization_model()
ORGANIZATION_USER_MODEL = get_organization_user_model()
ORGANIZATION_GROUP_MODEL = get_organization_group_model()

# Define the user group permissions for the ORGANIZATION_MODEL model.
USER_GROUP_PERMISSIONS = {
    # add user admin permissions on ORGANIZATION_MODEL
    DefaultUserGroups.FREE_USER: {
        USER_MODEL: ['change', 'view', 'delete'],
        USER_GROUP_MODEL: ['view'],
        ORGANIZATION_MODEL: ['add', 'change', 'view', 'delete'],
        Outlet: ['add', 'change', 'view', 'delete'],
        # Location: ['add', 'change', 'view', 'delete'],
        # Floor: ['add', 'view', 'delete'],
        # Block: ['add', 'change', 'view', 'delete'],

        # models that are handled according to permissions inside
        # organization groups must have all permission on user group end
        ORGANIZATION_USER_MODEL: ['add', 'change', 'view', 'delete'],
        ORGANIZATION_GROUP_MODEL: ['add', 'change', 'view', 'delete'],
    },
}

# Define the organization group permissions for the ORGANIZATION_MODEL model.
ORGANIZATION_GROUP_PERMISSIONS = {
    # add organization admin permissions on ORGANIZATION_MODEL
    DefaultOrganizationGroups.OWNER: {
        ORGANIZATION_MODEL: ['change', 'view', 'delete'],
        ORGANIZATION_USER_MODEL: ['add', 'change', 'view', 'delete'],
        ORGANIZATION_GROUP_MODEL: ['add', 'change', 'view', 'delete'],
        Outlet: ['add', 'change', 'view', 'delete'],
        # Location: ['add', 'change', 'view', 'delete'],
        # Floor: ['add', 'view', 'delete'],
        # Block: ['add', 'change', 'view', 'delete'],
    },

    # add organization admin permissions on ORGANIZATION_MODEL
    DefaultOrganizationGroups.ADMIN: {
        ORGANIZATION_MODEL: ['change', 'view'],
        ORGANIZATION_USER_MODEL: ['add', 'change', 'view', 'delete'],
        ORGANIZATION_GROUP_MODEL: ['add', 'change', 'view', 'delete'],
        Outlet: ['add', 'change', 'view', 'delete'],
        # Location: ['add', 'change', 'view', 'delete'],
        # Floor: ['add', 'view', 'delete'],
        # Block: ['add', 'change', 'view', 'delete'],
    },

    # add organization member permissions on ORGANIZATION_MODEL
    DefaultOrganizationGroups.MEMBER: {
        # can view details of the organization
        ORGANIZATION_MODEL: ['view'],
        ORGANIZATION_USER_MODEL: ['view'],
        ORGANIZATION_GROUP_MODEL: ['view'],
        Outlet: ['add'],
        # Location: ['view'],
        # Floor: ['view'],
        # Block: ['view']
    },
}
