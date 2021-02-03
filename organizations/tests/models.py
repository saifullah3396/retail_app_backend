"""
Defines the test cases for models of this application.
"""

from django.test import TestCase
from django.urls import reverse
from organizations.models import Organization


class OrganizationModelTests(TestCase):

    def setUp(self):
        self.organization = Organization.objects.create(
            name='NUST',
            desc='NUST University Description'
        )

    def test_model(self):
        organization = Organization.objects.get(id=self.organization.id)
        self.assertEquals(organization.name, 'NUST')
        self.assertEquals(organization.desc, 'NUST University Description')
