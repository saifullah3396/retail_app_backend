import uuid
from django.db import models


class Organization(models.Model):
    # generate unique uuid for each organization
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # organization title
    title = models.CharField(max_length=120)

    # organization description
    desc = models.TextField()

    def __str__(self):
        return self.title
