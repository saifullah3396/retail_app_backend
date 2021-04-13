"""
Defines the test cases for models of this application.
"""

from django.test import TestCase

from organizations.models import Organization


class OrganizationModelTests(TestCase):
    """
    Test cases for organization models creation.
    """

    def setUp(self):
        self.organization = Organization.objects.create(
            name='NUST',
        )

        self.sub_organization = Organization.objects.create(
            name='SMME',
            parent=self.organization
        )

    def test_model(self):
        """Test case for making sure model is correctly defined."""

        # test details of the organization
        organization = Organization.objects.get(id=self.organization.id)
        self.assertEqual(organization.name, 'NUST')

        # test details of the sub-organization made under organization
        sub_organization = Organization.objects.get(
            id=self.sub_organization.id)
        self.assertEqual(sub_organization.name, 'SMME')
        self.assertEqual(sub_organization.parent.id, organization.id)
