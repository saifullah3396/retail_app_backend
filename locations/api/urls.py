"""
Defines the urls for the views defined in the locations api.
"""

from django.urls import path

from .views.blocks_views import *
from .views.floors_views import *
from .views.locations_views import *

urlpatterns = [
    path(
        '',
        LocationsListCreateDestroyView.as_view(),
        name='locations_list_create_delete'),
    path(
        '<pk>',
        LocationsRetrieveUpdateDestroyView.as_view(),
        name='locations_retrieve_update_delete'),
    path(
        '<uuid:location_id>/floors/',
        FloorsListCreateDestroyView.as_view(),
        name='floors_list_create_delete'),
    path(
        '<uuid:location_id>/floors/<pk>',
        FloorsRetrieveUpdateDestroyView.as_view(),
        name='floors_retrieve_update_delete'),
    path(
        '<uuid:location_id>/floors/<uuid:floor_id>/blocks/',
        BlocksListCreateDestroyView.as_view(),
        name='blocks_list_create_delete'),
    path(
        '<uuid:location_id>/floors/<uuid:floor_id>/blocks/<pk>',
        BlocksRetrieveUpdateDestroyView.as_view(),
        name='blocks_retrieve_update_delete'),
]
