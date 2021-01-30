from django.urls import path
from .views import *


urlpatterns = [
    path(
        '',
        OrganizationsListCreateDestroyView.as_view(),
        name='organizations_list_create'),
    path(
        '<pk>',
        OrganizationsRetrieveUpdateDestroyView.as_view(),
        name='organizations_rud'),
]
