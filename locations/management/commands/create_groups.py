from backend.management.commands import create_groups
from locations.permissions import USER_GROUP_PERMISSIONS


class Command(create_groups.Command):
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
