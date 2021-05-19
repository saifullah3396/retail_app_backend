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

    def create_user_groups(self, app_config, *args, **options):
        """
        Calls the create_user_groups command from the specific application. Each
        call generates the user groups defined in core/permissions.py (or gets
        them if they already exist) along with app specific permissions on
        those groups.
        """
        if module_has_submodule(
                app_config.module, "management.commands.create_user_groups"):
            command = import_module(
                '.management.commands.create_user_groups', app_config.name)
            call_command(command.Command(), **options)

    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')

    def handle(self, *args, **options):
        """
        Runs the command
        """
        for app_config in apps.get_app_configs():
            self.create_user_groups(app_config, **options)
