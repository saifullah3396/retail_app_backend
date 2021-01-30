from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    """
    A command to generate application groups and their permissions
    """

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Create default groups"

    def get_group_permissions(self):
        """
        Must be implemented in child class to return a dictionary of groups
        and their authorized permission, e.g

        'GroupName': {
            models.Model: ['add', 'change', 'delete', 'view'],
        }
        """

        raise NotImplementedError(
            "This command must be implemented by a command of same name "
            "in other applications.")

    def handle(self, *args, **options):
        """
        Generates a new group and assigns its respective permissions as defined
        by the dictionary returned by self.get_group_permissions().
        """

        # get group permissions
        group_permissions = self.get_group_permissions()
        for group_name in group_permissions:

            # create a new group
            group, created = Group.objects.get_or_create(name=group_name)

            # loop models in group
            for model_cls in group_permissions[group_name]:

                # loop permissions in group/model
                for perm_index, perm_name in \
                        enumerate(group_permissions[group_name][model_cls]):

                    # generate permission name as Django would generate it
                    codename = perm_name + "_" + model_cls._meta.model_name

                    try:
                        # find permission object and add to group
                        perm = Permission.objects.get(codename=codename)
                        group.permissions.add(perm)
                        self.stdout.write(
                            "Adding "
                            + codename
                            + " to group "
                            + group.__str__())
                    except Permission.DoesNotExist:
                        self.stdout.write(codename + " not found")
