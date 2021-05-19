import datetime

from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from organizations.signals import owner_changed

from app_organizations.models import (AppOrganization, AppOrganizationOwner,
                                      AppOrganizationUser)
from backend import default_permissions
from backend.settings import CACHE_KEY_GENERATOR
from app_organizations.models import (DefaultOrganizationGroups,
                                      OrganizationGroup)


def generate_org_groups_and_permissions(organization):
    perms_map = default_permissions.ORGANIZATION_GROUP_PERMISSIONS
    for group_enum in perms_map:
        # create a new group or get if it already exists
        group, _ = OrganizationGroup.objects.get_or_create(
            name=group_enum.name,
            authority=group_enum.value,
            organization=organization)

        # loop models in group
        for model_cls in perms_map[group_enum]:

            # loop permissions in group/model
            for _, perm_name in \
                    enumerate(perms_map[group_enum][model_cls]):

                # generate permission name as Django would generate it
                codename = perm_name + "_" + model_cls._meta.model_name

                try:
                    # find permission object and add to group
                    perm = Permission.objects.get(
                        codename=codename)
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    print(codename + " not found")


@receiver(post_save, sender=AppOrganization)
def on_organization_created(sender, instance, created, **kwargs):
    if not created:
        return
    generate_org_groups_and_permissions(instance)


@receiver(post_save, sender=AppOrganizationUser)
def on_organization_user_created(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        if instance.is_admin:
            group = OrganizationGroup.objects.get(
                name=DefaultOrganizationGroups.ADMIN.name,
                organization=instance.organization)
            instance.groups.add(group)
        else:
            group = OrganizationGroup.objects.get(
                name=DefaultOrganizationGroups.MEMBER.name,
                organization=instance.organization)
            instance.groups.add(group)
    except OrganizationGroup.DoesNotExist as exc:
        raise exc


@receiver(m2m_changed, sender=AppOrganizationUser.groups.through)
def on_organization_user_created_m2m(instance, action, **kwargs):

    if action == 'post_add':
        if instance.is_admin:
            if not instance.groups.filter(
                    name=DefaultOrganizationGroups.ADMIN.name).exists():
                group = OrganizationGroup.objects.get(
                    name=DefaultOrganizationGroups.ADMIN.name,
                    organization=instance.organization)
                instance.groups.add(group)
        else:
            if not instance.groups.filter(
                    name=DefaultOrganizationGroups.MEMBER.name).exists():
                group = OrganizationGroup.objects.get(
                    name=DefaultOrganizationGroups.MEMBER.name,
                    organization=instance.organization)
                instance.groups.add(group)


@receiver(post_save, sender=AppOrganizationOwner)
def on_organization_owner_created(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        group = OrganizationGroup.objects.get(
            name=DefaultOrganizationGroups.OWNER.name,
            organization=instance.organization)
        instance.organization_user.groups.add(group)
    except OrganizationGroup.DoesNotExist as exc:
        raise exc


@receiver(owner_changed)
def on_owner_changed(_, old, new, **kwargs):
    """
    We remove previous owner from owner group and add the new owner to the
    group
    """
    group = OrganizationGroup.objects.get(
        name=DefaultOrganizationGroups.OWNER)
    group.organization_user_set.remove(old)
    group.organization_user_set.add(new)


@receiver(post_save, sender=OrganizationGroup)
def change_api_updated_at(sender, **kwargs):
    cache.set(CACHE_KEY_GENERATOR(sender), datetime.datetime.utcnow())


@receiver(post_save, sender=AppOrganization)
def change_api_updated_at(sender, **kwargs):
    cache.set(CACHE_KEY_GENERATOR(sender), datetime.datetime.utcnow())


@receiver(post_save, sender=AppOrganizationUser)
def change_api_updated_at(sender, **kwargs):
    cache.set(CACHE_KEY_GENERATOR(sender), datetime.datetime.utcnow())


@receiver(post_save, sender=AppOrganizationOwner)
def change_api_updated_at(sender, **kwargs):
    cache.set(CACHE_KEY_GENERATOR(sender), datetime.datetime.utcnow())
