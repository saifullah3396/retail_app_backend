

from importlib import import_module

from django.contrib.auth.models import Permission
from django.utils.module_loading import module_has_submodule
from organizations.utils import model_field_names

from app_organizations.models import OrganizationGroup


def create_organization(
        user,
        name,
        slug=None,
        is_active=None,
        org_defaults=None,
        org_user_defaults=None,
        **kwargs):

    org_model = (
        kwargs.pop("model", None)
        or kwargs.pop("org_model", None)
    )
    kwargs.pop("org_user_model", None)  # Discard deprecated argument

    org_owner_model = org_model.owner.related.related_model
    org_user_model = org_model.organization_users.rel.related_model

    if org_defaults is None:
        org_defaults = {}
    if org_user_defaults is None:
        if "is_admin" in model_field_names(org_user_model):
            org_user_defaults = {"is_admin": True}
        else:
            org_user_defaults = {}

    if slug is not None:
        org_defaults.update({"slug": slug})
    if is_active is not None:
        org_defaults.update({"is_active": is_active})

    org_defaults.update({"name": name})
    organization = org_model.objects.create(**org_defaults)

    org_user_defaults.update({"organization": organization, "user": user})
    new_user = org_user_model.objects.create(**org_user_defaults)

    org_owner_model.objects.create(
        organization=organization, organization_user=new_user
    )
    return organization

    # generate default organization groups within the organization along
    # with their permissions
