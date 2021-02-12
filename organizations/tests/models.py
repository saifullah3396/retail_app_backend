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

        self.sub_organization = Organization.objects.create(
            name='SMME',
            desc='SMME School Description',
            parent=self.organization
        )

    def test_model(self):
        # test details of the organization
        organization = Organization.objects.get(id=self.organization.id)
        self.assertEquals(organization.name, 'NUST')
        self.assertEquals(organization.desc, 'NUST University Description')

        # test details of the sub-organization made under organization
        sub_organization = Organization.objects.get(
            id=self.sub_organization.id)
        self.assertEquals(sub_organization.name, 'SMME')
        self.assertEquals(sub_organization.desc, 'SMME School Description')
        self.assertEquals(sub_organization.parent.id, organization.id)
