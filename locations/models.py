import uuid
from django.db import models


class Location(models.Model):
    # generate unique uuid for each location
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # location title
    title = models.CharField(max_length=120, default="Unknown", unique=True)

    # location description
    desc = models.TextField(blank=True)

    # organization with which this location is associated
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
    )

    # sub-organization with which this location is associated. Sub-organization
    # can be null
    sub_organization = models.ForeignKey(
        'organizations.SubOrganization',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


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
        return "Floor #{} ({})".format(self.number, str(self.location))


class Block(models.Model):
    # generate unique uuid for each location block
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # block name
    name = models.CharField(max_length=24, blank=True)

    # location with which this floor is associated
    floor = models.ForeignKey(
        'locations.Floor',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "{}, {}".format(self.name, str(self.floor))
