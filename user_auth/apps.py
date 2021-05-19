"""
Defines the application configuration
"""

from django.apps import AppConfig


# pylint: disable=missing-class-docstring
class UserAuthConfig(AppConfig):
    name = 'user_auth'

    def ready(self):
        import user_auth.signals.handlers
