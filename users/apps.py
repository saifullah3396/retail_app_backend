"""
Defines the application configuration
"""

from django.apps import AppConfig


# pylint: disable=missing-class-docstring
class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals.handlers
