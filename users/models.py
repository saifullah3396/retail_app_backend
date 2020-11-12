import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class AppUser(AbstractUser):
    """
    Custom user model for our application. The user can be a part of an
    organization or sub-organization and can have access to locations available
    in authorized_locations
    """

    # replace id with uuid
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    # user authority [0, 1, ... N]. N means highest authority
    authority = models.IntegerField(default=-1)

    # organization with which this sub-organization is associated
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # organization with which this sub-organization is associated
    sub_organization = models.ForeignKey(
        'organizations.SubOrganization',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # authorized locations
    authorized_locations = models.ManyToManyField(
        'locations.Location',
        blank=True,
        null=True
    )
