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

blockpk_urlpatterns = [
    path('frames/', include(
        'measurement_frames.api.urls')),
    path('cameras/', include(
        'cameras.api.urls'))
]

floorpk_urlpatterns = [
    path(
        'blocks/', include([
            path(
                '',
                BlocksListCreateDestroyView.as_view(),
                name='blocks_list_create_delete'),
            path(
                '<pk>/',
                BlocksRetrieveUpdateDestroyView.as_view(),
                name='blocks_retrieve_update_delete'),
            path('<block>/', include(blockpk_urlpatterns)),
        ]))
]

locationpk_urlpatterns = [
    path(
        'floors/', include([
            path(
                '',
                FloorsListCreateDestroyView.as_view(),
                name='floors_list_create_delete'),
            path(
                '<pk>/',
                FloorsRetrieveUpdateDestroyView.as_view(),
                name='floors_retrieve_update_delete'),
            path('<floor>/', include(floorpk_urlpatterns)),
        ])),
]

urlpatterns = [
    path(
        '',
        OutletLocationsListCreateDestroyView.as_view(),
        name='outlet_locations_retrieve_update_delete'),
    path(
        '<pk>/',
        OutletLocationsRetrieveUpdateDestroyView.as_view(),
        name='outlet_locations_retrieve_update_delete'),
    path('<location>/', include(locationpk_urlpatterns)),
]
