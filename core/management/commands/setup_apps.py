"""
Sets up the base configuration or functionality required in our applications.
"""

from importlib import import_module

from django.apps import apps
from django.core.management import BaseCommand, call_command
from django.utils.module_loading import module_has_submodule


class Command(BaseCommand):
    """
    A command to setup common initialization parameters used across our
    applications
    """

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def create_groups(self, app_config):
        """
        Calls the create_groups command from the specific application. Each
        call generates app specific groups (or gets them if they already exist)
        along with app specific permissions on those groups.
        """
        if module_has_submodule(
                app_config.module, "management.commands.create_groups"):
            command = import_module(
                '.management.commands.create_groups', app_config.name)
            call_command(command.Command())

    def handle(self, *args, **options):
        """
        Runs the command
        """

        for app_config in apps.get_app_configs():
            self.create_groups(app_config)
