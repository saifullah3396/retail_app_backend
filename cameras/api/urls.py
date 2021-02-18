from django.urls import path
from .views import CamerasListCreateDestroyView,CamerasRetrieveUpdateDestroyView
#  CameraDetailView, CameraFilterListView, \
#     CameraFilterDetailView
from .views import *
urlpatterns = [
 path(
        '',
        CamerasListCreateDestroyView.as_view(),
        name='cameras_list_create_delete'),
 path(
        '<pk>',
        CamerasRetrieveUpdateDestroyView.as_view(),
        name='cameras_retrieve_update_delete'),
]
