"""
Defines the permissions used in this application.
"""

import copy

from core.permissions import AppDjangoModelPermissions


class AppUsersListCreateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the AppUserListCreateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)

        # this affectively removes list deletion by user group on this view
        self.perms_map['DELETE'] = ['%(app_label)s.list_delete_%(model_name)s']
