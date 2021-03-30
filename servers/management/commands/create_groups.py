"""
Implements the create_groups_base to generate user groups in the application
and their related permissions.
"""

from core.management.commands.create_groups_base import Command
from servers.permissions import USER_GROUP_PERMISSIONS


class Command(Command):
    """
    A command to generate organization related groups and their permissions
    """

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def get_group_permissions(self):
        """
        Defines groups and their respective permissions
        """

        return USER_GROUP_PERMISSIONS
