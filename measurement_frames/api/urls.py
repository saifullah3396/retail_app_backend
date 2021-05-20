"""
Defines the urls for the views defined in the api.
"""

from django.urls import path

from measurement_frames.api.views import (
    MeasurementFramesListCreateDestroyView,
    MeasurementFramesRetrieveUpdateDestroyView)

urlpatterns = [
    path(
        '',
        MeasurementFramesListCreateDestroyView.as_view(),
        name='frames_list_create_delete'),
    path(
        '<pk>/',
        MeasurementFramesRetrieveUpdateDestroyView.as_view(),
        name='frames_retrieve_update_delete'),
]
