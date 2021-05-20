"""
Defines the urls for the views defined in the organizations api.
"""

from django.conf.urls import include
from django.urls import path

from outlets.api.views import (OutletsListCreateDestroyView,
                               OutletsRetrieveUpdateDestroyView,
                               OutletUsersListCreateDestroyView,
                               OutletUsersRetrieveUpdateDestroyView)

userspk_urlpatterns = [
    path(
        '',
        OutletUsersListCreateDestroyView.as_view(),
        name='outlet_users_retrieve_update_destroy'),
    path(
        '<pk>/',
        OutletUsersRetrieveUpdateDestroyView.as_view(),
        name='outlet_users_retrieve_update_destroy'),
]

outletspk_urlpatterns = [
    path('users/', include(userspk_urlpatterns)),
    path('locations/', include('locations.api.urls'))
]
urlpatterns = [
    path(
        '',
        OutletsListCreateDestroyView.as_view(),
        name='outlets_list_create_destroy'),
    path(
        '<pk>/',
        OutletsRetrieveUpdateDestroyView.as_view(),
        name='outlets_retrieve_update_destroy'),
    path('<outlet>/', include(outletspk_urlpatterns))

]
