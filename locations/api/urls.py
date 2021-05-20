"""
Defines the urls for the views defined in the locations api.
"""

from django.conf.urls import include
from django.urls import path

from .views import (BlocksListCreateDestroyView,
                    BlocksRetrieveUpdateDestroyView,
                    FloorsListCreateDestroyView,
                    FloorsRetrieveUpdateDestroyView,
                    OutletLocationsListCreateDestroyView,
                    OutletLocationsRetrieveUpdateDestroyView)

urlpatterns = [
    path(
        '',
        OutletLocationsListCreateDestroyView.as_view(),
        name='outlet_locations_retrieve_update_delete'),
    path(
        '<location>/', include([
            path(
                '',
                OutletLocationsRetrieveUpdateDestroyView.as_view(),
                name='outlet_locations_retrieve_update_delete'),
            path(
                'floors/', include([
                    path(
                        '',
                        FloorsListCreateDestroyView.as_view(),
                        name='floors_list_create_delete'),
                    path(
                        '<floor>/', include([
                            path(
                                '',
                                FloorsRetrieveUpdateDestroyView.as_view(),
                                name='floors_retrieve_update_delete'),
                            path(
                                'blocks/', include([
                                    path(
                                        '',
                                        BlocksListCreateDestroyView.as_view(),
                                        name='blocks_list_create_delete'),
                                    path(
                                        '<block>/',
                                        BlocksRetrieveUpdateDestroyView.as_view(),
                                        name='blocks_retrieve_update_delete'),
                                ]))
                        ])),

                ])),

        ])),
]
