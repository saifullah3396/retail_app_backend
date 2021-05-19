

from outlets.models import Outlet


def create_outlet(
        user,
        name,
        organization,
        **kwargs):

    org_model = Outlet
    org_owner_model = org_model.owner.related.related_model
    org_user_model = org_model.organization_users.rel.related_model

    outlet = org_model.objects.create(
        **{
            "name": name,
            "is_active": True,
            "organization": organization})
    outlet_user = org_user_model.objects.create(
        **{"organization": outlet, "user": user})
    org_owner_model.objects.create(
        organization=outlet, organization_user=outlet_user
    )
    return outlet
