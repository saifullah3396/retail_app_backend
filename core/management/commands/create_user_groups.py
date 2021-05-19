"""
Defines the base command that is used in setup_apps.py to generate user groups
used in our applications along with all permissions as defined in any of our
application related to those user groups
"""

from django.apps import apps as django_apps
from django.contrib.auth.models import Permission
from django.core.exceptions import ImproperlyConfigured
from django.core.management import BaseCommand

from backend import default_permissions, settings


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


class Command(BaseCommand):
    """
    A command to generate application groups and their permissions
    """

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Create default groups"
    group_object = get_user_group_model()

    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')

    def handle(self, *args, **options):
        """
        Generates a new group and assigns its respective permissions as defined
        by the dictionary returned by self.get_group_permissions().
        """

        # get group permissions
        group_permissions = default_permissions.USER_GROUP_PERMISSIONS
        for group_enum in group_permissions:

            # create a new group
            group, _ = self.group_object.objects.get_or_create(
                name=group_enum.name, authority=group_enum.value)

            # loop models in group
            for model_cls in group_permissions[group_enum]:

                # loop permissions in group/model
                for _, perm_name in \
                        enumerate(group_permissions[group_enum][model_cls]):

                    # generate permission name as Django would generate it
                    codename = perm_name + "_" + model_cls._meta.model_name

                    try:
                        # find permission object and add to group
                        perm = Permission.objects.get(
                            codename=codename)
                        group.permissions.add(perm)
                        if not options['silent']:
                            print('Adding permission {} to group {}'.format(
                                perm, group))
                    except Permission.DoesNotExist:
                        self.stdout.write(codename + " not found")
