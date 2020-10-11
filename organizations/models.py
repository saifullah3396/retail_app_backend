import uuid
from django.db import models


class Organization(models.Model):
    # generate unique uuid for each organization
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # organization title
    title = models.CharField(max_length=120, default="Unknown", unique=True)

    # organization description
    desc = models.TextField(blank=True)

    def __str__(self):
        return self.title


class SubOrganization(models.Model):
    # generate unique uuid for each sub-organization
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # sub-organization title
    title = models.CharField(max_length=120, default="Unknown", unique=True)

    # sub-organization description
    desc = models.TextField(blank=True)

    # organization with which this sub-organization is associated
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title
