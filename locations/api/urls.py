from django.urls import path
from .views import *


urlpatterns = [
    path(
        '',
        LocationsListCreateDestroyView.as_view(),
        name='locations_list_create_delete'),
    path(
        '<pk>',
        LocationsRetrieveUpdateDestroyView.as_view(),
        name='locations_rud'),
]
