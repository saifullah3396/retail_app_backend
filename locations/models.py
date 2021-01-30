import uuid
from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


class Location(models.Model):
    # generate unique uuid for each location
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # location name
    name = models.CharField(max_length=120, default="Unknown", unique=True)

    # organization with which this location is associated
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "Location={}, Organization={}".format(
            self.name, self.organization.name)


class Floor(models.Model):
    # generate unique uuid for each location floor
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # floor
    number = models.IntegerField(default=0)

    # location with which this floor is associated
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "Floor={}, {}".format(self.number, str(self.location))


class Block(models.Model):
    # generate unique uuid for each location block
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # block name
    name = models.CharField(
        default='Main', max_length=150, blank=True, unique=True)

    # add image field for block floor map
    floor_map = models.ImageField(
        upload_to='maps', blank=True, null=True)

    # local coordinate frame of the block
    coordinate_frame = models.PointField(default=Point(0, 0))

    # location with which this floor is associated
    floor = models.ForeignKey(
        'locations.Floor',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "Block={}, {}".format(self.name, str(self.floor))
