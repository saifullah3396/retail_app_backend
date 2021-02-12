from .models import Location


def get_locations_in_organizations(organizations):
    """
    Returns all locations which present within the given organizations
    queryset
    """
    return Location.objects.filter(organization__in=organizations)


def get_locations_for_staff():
    """
    Returns all locations that are authorized to staff users
    """
    return Location.objects.all()


def get_locations_for_organization_admin(user, include_self):
    """
    Returns all locations that are authorized to an organization admin
    """
    print('get_locations_for_organization_admin')

    # get all organizations under this one
    organizations_tree = user.organization.get_descendants(
        include_self=include_self)

    # get all locations in the tree
    return get_locations_in_organizations(organizations_tree)


def get_locations_for_employee(user):
    """
    Returns all locations that are authorized to an employee
    """

    return user.authorized_locations.all()
