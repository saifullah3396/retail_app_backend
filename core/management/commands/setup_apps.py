from django.core.management import BaseCommand, call_command
from django.apps import apps
from django.utils.module_loading import module_has_submodule
from importlib import import_module


class Command(BaseCommand):
    """
    A command to setup application common functionality
    """

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        """
        Generates a new group and assigns its respective permissions as defined
        by the dictionary returned by self.get_group_permissions().
        """

        for app_config in apps.get_app_configs():

            # call create_groups command from all apps
            if module_has_submodule(
                    app_config.module, "management.commands.create_groups"):
                command = import_module(
                    '.management.commands.create_groups', app_config.name)
                call_command(command.Command())
