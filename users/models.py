"""
Defines the model of an organization
"""
import uuid

from allauth.account.models import EmailAddress
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.db import models
from django.db.models import Q, UniqueConstraint, When
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from safedelete import DELETED_VISIBLE_BY_PK, SOFT_DELETE_CASCADE
from safedelete.config import HARD_DELETE
from safedelete.managers import SafeDeleteManager
from safedelete.models import SafeDeleteModel

from user_auth.models import DefaultUserGroups, UserGroup, UserPermissionsMixin


class AppUserManager(UserManager, SafeDeleteManager):
    """
    Custom implements the user creation functions of UserManager.
    """

    _safedelete_visibility = DELETED_VISIBLE_BY_PK

    def create_user(self, username, email=None, password=None, **extra_fields):
        user = self._create_user(username, email, password, **extra_fields)

        try:
            user.save(using=self._db)

            # add user to free user group by default
            free_user_group, _ = UserGroup.objects.get_or_create(
                name=DefaultUserGroups.FREE_USER.name,
                authority=DefaultUserGroups.FREE_USER.value)
            user.groups.add(free_user_group)
            return user
        except Exception as exc:
            user.delete(force_policy=HARD_DELETE)
            raise exc

    def create_superuser(
            self, username, email=None, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username=username,
            email=email,
            password=password
        )

        try:
            user.is_staff = True
            user.is_superuser = True
            user.save(using=self._db)

            # add user to super user group
            super_group, _ = UserGroup.objects.get_or_create(
                name=DefaultUserGroups.SUPER_USER.name,
                authority=DefaultUserGroups.SUPER_USER.value)
            user.groups.add(super_group)

            address = EmailAddress.objects.create(user=user)
            address.email = email
            address.verified = True
            address.save()

            return user
        except Exception as exc:
            user.delete(force_policy=HARD_DELETE)
            raise exc


class AppUser(AbstractBaseUser, UserPermissionsMixin, SafeDeleteModel):
    """
    Custom user model for our application. The user can be a part of an
    organization or sub-organization and can have access to locations available
    in authorized_locations
    """
    _safedelete_policy = SOFT_DELETE_CASCADE
    objects = AppUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        constraints = [
            UniqueConstraint(fields=['email'], condition=Q(
                deleted__isnull=True), name='unique_email_if_not_deleted')
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)

    email_validator = EmailValidator()
    email = models.EmailField(
        _('email address'),
        max_length=150,
        validators=[email_validator],
        error_messages={
            'unique': _("A user with that email address already exists."),
        }
    )

    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    username = models.CharField(_('username'), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    # user avatar image
    avatar = models.ImageField(
        upload_to='avatars', blank=True, null=True)

    @property
    def highest_group(self):
        # get highest authority group
        return self.groups.all().order_by('authority').first()
