"""
Defines the urls for the views defined in the locations api.
"""

from django.urls import path

from .views import (MeasurementFramesListCreateDestroyView,
                    MeasurementFramesRetrieveUpdateDestroyView)

urlpatterns = [
    path(
        '',
        MeasurementFramesListCreateDestroyView.as_view(),
        name='measurement_frame_list_create_delete'),
    path(
        '<pk>',
        MeasurementFramesRetrieveUpdateDestroyView.as_view(),
        name='measurement_frame_retrieve_update_delete'),
]
