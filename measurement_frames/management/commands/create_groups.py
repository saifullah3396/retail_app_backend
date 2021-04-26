"""
Implements the create_groups_base to generate user groups in the application
and their related permissions.
"""

from core.management.commands import create_groups_base
from measurement_frames.permissions import USER_GROUP_PERMISSIONS


class Command(create_groups_base.Command):
    """
    A command to generate organization related groups and their permissions
    """

    def get_group_permissions(self):
        """
        Defines groups and their respective permissions
        """

        return USER_GROUP_PERMISSIONS
