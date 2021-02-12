"""
Defines the test cases for models of this application.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.gis.geos import Point
from organizations.models import Organization
from locations.models import Location, Floor, Block


class LocationModelTests(TestCase):
    """
    Defines unit tests Location model tests.
    """

    def setUp(self):
        """
        Sets up the test cases.
        """

        self.organization = Organization.objects.create(
            name='NUST',
            desc='NUST University Description'
        )

        self.sub_organization = Organization.objects.create(
            name='SMME',
            desc='SMME School Description',
            parent=self.organization
        )

        self.location_organization = Location.objects.create(
            name='NUST_location_1',
            organization=self.organization
        )

        self.location_sub_organization = Location.objects.create(
            name='SMME_location_1',
            organization=self.sub_organization
        )

    def test_model_creation(self):
        # test details of the location_organization
        location = Location.objects.get(id=self.location_organization.id)
        self.assertEquals(location.name, 'NUST_location_1')
        self.assertEquals(location.organization.id, self.organization.id)

        # test details of the location_sub_organization
        location = Location.objects.get(id=self.location_sub_organization.id)
        self.assertEquals(location.name, 'SMME_location_1')
        self.assertEquals(
            location.organization.id,
            self.sub_organization.id)


class FloorModelTests(TestCase):
    """
    Defines unit tests Floor model tests.
    """

    def setUp(self):
        """
        Sets up the test cases.
        """

        self.organization = Organization.objects.create(
            name='NUST',
            desc='NUST University Description'
        )

        self.sub_organization = Organization.objects.create(
            name='SMME',
            desc='SMME School Description',
            parent=self.organization
        )

        self.location_organization = Location.objects.create(
            name='NUST_location_1',
            organization=self.organization
        )

        self.location_sub_organization = Location.objects.create(
            name='SMME_location_1',
            organization=self.sub_organization
        )

        self.location_sub_organization_floor_0 = Floor.objects.create(
            number=0,
            location=self.location_sub_organization
        )

        self.location_sub_organization_floor_1 = Floor.objects.create(
            number=1,
            location=self.location_sub_organization
        )

    def test_model_creation(self):
        # test details of the floor 0 created in location_sub_organization
        floor = Floor.objects.get(id=self.location_sub_organization_floor_0.id)
        self.assertEquals(floor.number, 0)
        self.assertEquals(floor.location.id, self.location_sub_organization.id)

        # test details of the floor 1 created in location_sub_organization
        floor = Floor.objects.get(id=self.location_sub_organization_floor_1.id)
        self.assertEquals(floor.number, 1)
        self.assertEquals(floor.location.id, self.location_sub_organization.id)


class BlockModelTests(TestCase):
    """
    Defines unit tests Block model tests.
    """

    def setUp(self):
        """
        Sets up the test cases.
        """

        self.organization = Organization.objects.create(
            name='NUST',
            desc='NUST University Description'
        )

        self.sub_organization = Organization.objects.create(
            name='SMME',
            desc='SMME School Description',
            parent=self.organization
        )

        self.location_organization = Location.objects.create(
            name='NUST_location_1',
            organization=self.organization
        )

        self.location_sub_organization = Location.objects.create(
            name='SMME_location_1',
            organization=self.sub_organization
        )

        self.location_sub_organization_floor_0 = Floor.objects.create(
            number=0,
            location=self.location_sub_organization
        )

        self.location_sub_organization_floor_1 = Floor.objects.create(
            number=1,
            location=self.location_sub_organization
        )

        self.location_sub_organization_floor_0_block_A = Block.objects.create(
            name='Block_A',
            coordinate_frame=Point(100, 100),
            floor=self.location_sub_organization_floor_0)

        self.location_sub_organization_floor_1_block_A = Block.objects.create(
            name='Block_A',
            coordinate_frame=Point(100, 120),
            floor=self.location_sub_organization_floor_1)

    def test_model_creation(self):
        # test details of the block_A floor_0 created in
        # location_sub_organization
        block = Block.objects.get(
            id=self.location_sub_organization_floor_0_block_A.id)
        self.assertEquals(block.name, 'Block_A')
        self.assertEquals(block.coordinate_frame.x, 100)
        self.assertEquals(block.coordinate_frame.y, 100)
        self.assertEquals(
            block.floor.id, self.location_sub_organization_floor_0.id)

        # test details of the block_A floor_1 created in
        # location_sub_organization
        block = Block.objects.get(
            id=self.location_sub_organization_floor_1_block_A.id)
        self.assertEquals(block.name, 'Block_A')
        self.assertEquals(block.coordinate_frame.x, 100)
        self.assertEquals(block.coordinate_frame.y, 120)
        self.assertEquals(
            block.floor.id, self.location_sub_organization_floor_1.id)
