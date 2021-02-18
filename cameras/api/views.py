from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..models import Camera
from .serializers import CameraSerializer
from rest_framework import generics
from core.utils import *
from core.views import *
from ..permissions import *

class CameraView:
    ordering_fields = ['id', 'place_name', 'ip_addr']
    filterset_fields = {
        'place_name': ['exact', 'icontains'],
    }

    def _get_model(self):

        return Camera

    def _order_by(self):

        return 'place_name'

    # def _get_organizations_tree(self, organization):
    #     return self.organizations_tree_wrt_request[self.request.method](
    #         organization)




class CamerasListCreateDestroyView(CoreListCreateDestroyView, CameraView):

    queryset =Camera.objects.none()
    serializer_class = CameraSerializer
    permission_classes = (CamerasListCreateDestroyPermission,)

    def _get_model(self):

        return CameraView._get_model(self)

    def _define_get_queryset_by_group_fn(self):

        return {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                self._get_organization_admin_queryset,
            UserGroups.EMPLOYEE_GROUP:
                self._get_employee_queryset,
        }
    def _perform_create_by_organization_admin(self, serializer):

        descendents = self.request.user.organization.get_descendants(
            include_self=True)
        if not descendents.filter(id=self.request.data['organization']):
            raise exceptions.ValidationError(
                {
                    'organization': 'Invalid value.'
                })

        serializer.save()

    def _get_organization_admin_queryset(self):
        cameras = get_cameras_for_organization_admin(
            self.request.user, include_self=True)

        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                cameras, id_list)

        return cameras

    def _get_employee_queryset(self):
        cameras = get_cameras_for_employee(
            self.request.user, include_self=True)
        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                cameras, id_list)
        return cameras

    def _define_perform_create_by_group_fn(self):

        return {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                self._perform_create_by_organization_admin
        }
    def _order_by(self):

        return CameraView._order_by(self)



class CamerasRetrieveUpdateDestroyView(
        CoreRetrieveUpdateDestroyView, CameraView):
    """
    Defines the cameras retrieve-update-destroy view.
    """

    queryset = Camera.objects.none()  # Added for model permissions
    serializer_class = CameraSerializer
    permission_classes = (CamerasRetrieveUpdateDestroyPermission,)

    def _get_model(self):
        """
        Returns the model for this view
        """

        return CameraView._get_model(self)

    def _define_get_queryset_by_group_fn(self):
        """
        Returns a dictionary mapping user group to get_queryset function
        that will be called if the request user is in that user group.
        """
        return {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                self._get_organization_admin_queryset,
            UserGroups.EMPLOYEE_GROUP:
                self._get_employee_queryset,
        }

    def _define_perform_update_by_group_fn(self):
        """
        Returns a dictionary mapping user group to perform_update function
        that will be called if the request user is in that user group.
        """
        return {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                self._perform_update_by_organization_admin
        }

    def _get_organization_admin_queryset(self):
        """
        Returns the get_queryset for organization admin user group
        """
        return get_cameras_for_organization_admin(
            self.request.user, include_self=True)

    def _get_employee_queryset(self):
        """
        Returns the get_queryset for employee user group
        """
        return get_cameras_for_employee(
            self.request.user, include_self=True)

    def _perform_update_by_organization_admin(self, serializer):
        serializer.save()
