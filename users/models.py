from django.db import models
from django.contrib.auth.models import AbstractUser


class AppUser(AbstractUser):
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
