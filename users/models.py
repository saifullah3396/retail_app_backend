import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from allauth.account.models import EmailAddress
from backend import settings
# from locations.models import Location


class AppUserManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(
            self,
            username,
            email,
            password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username=username,
            email=email,
            password=password
        )

        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True

        user.save(using=self._db)

        address = EmailAddress.objects.create(user=user)
        address.email = email
        address.verified = True
        address.save()

        return user


class AppUser(AbstractUser):
    """
    Custom user model for our application. The user can be a part of an
    organization or sub-organization and can have access to locations available
    in authorized_locations
    """
    objects = AppUserManager()

    # replace id with uuid
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    # organization with which this user is associated
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # authorized locations
    authorized_locations = models.ManyToManyField(
        'locations.Location',
        blank=True
    )

    # user avatar image
    avatar = models.ImageField(
        upload_to='avatars', blank=True, null=True)
