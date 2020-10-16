from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractUser
)


class AppUserManager(BaseUserManager):
    def create_user(self, *args, **kwargs):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not kwargs.get('email'):
            raise ValueError('Users must have an email address')

        user = self.model(
            email=AppUserManager.normalize_email(kwargs.get('email')),
            username=kwargs.get('username'),
        )

        user.set_password(kwargs.get('password'))
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        u = self.create_user(
            email=email,
            password=password,
            username=username
        )
        u.is_admin = True
        u.is_active = True
        u.is_staff = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class AppUser(AbstractUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=24)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = AppUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
