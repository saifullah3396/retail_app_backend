"""
Defines the application configuration
"""


from django.apps import AppConfig


# pylint: disable=missing-class-docstring
class OrganizationsAuthConfig(AppConfig):
    name = 'organizations_auth'

    def ready(self):
        import app_organizations.signals.handlers
