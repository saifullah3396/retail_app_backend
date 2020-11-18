from django.urls import path
from .views import \
    OrganizationsListCreateView, \
    OrganizationsRUDView, \
    SubOrganizationsListCreateView, \
    SubOrganizationsRUDView


urlpatterns = [
    path(
        '',
        OrganizationsListCreateView.as_view(),
        name='organizations_list_create'),
    path(
        '<pk>',
        OrganizationsRUDView.as_view(),
        name='organizations_rud'),
    path(
        'sub/',
        SubOrganizationsListCreateView.as_view(),
        name='sub_organizations_list_create'),
    path(
        'sub/<pk>',
        SubOrganizationsRUDView.as_view(),
        name='sub_organizations_rud'),
]
