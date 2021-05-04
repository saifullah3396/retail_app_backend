"""
Defines the core REST API views on which all other application views will be
based.
"""

from django.db.models import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, pagination, status
from rest_framework.generics import (DestroyAPIView, GenericAPIView,
                                     ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.response import Response

from core.utils import (filter_queryset_by_id_list, get_fn_by_user_group,
                        get_id_list)


class PaginationConfig(pagination.PageNumberPagination):
    """
    Defines the base pagination configuration for our applications
    """
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class BaseAPIHandler:
    """
    Defines the custom user-based functionality for get-create-update-delete
    API calls for our views.
    """

    def __init__(self, model, get_is_list):
        self._api_handler_by_group = \
            self._define_api_handler_by_group()
        self._model = model
        self._get_is_list = get_is_list

    def _define_api_handler_by_group(self):
        """
        Returns a dictionary mapping user group to rest api handler functions
        that will be called if the request user is in that user group.
        """
        raise NotImplementedError()

    def _get_queryset_by_staff(self, request):
        """
        Returns the get queryset for staff users.
        """
        if self._get_is_list:
            id_list = get_id_list(request)
            if id_list:
                return filter_queryset_by_id_list(
                    self._model.objects, id_list)
            return self._model.objects.all()
        else:
            return self._model.objects.all()

    def _perform_create_by_staff(self, serializer):
        """
        Implements perform_create for staff users.
        """
        serializer.save()

    def _perform_update_by_staff(self, serializer):
        """
        Implements perform_update for staff users.
        """
        serializer.save()

    def _call_api_by_group(self, user, request_type, *args, **kwargs):
        """
        Implements the customized get_queryset functionalty.
        """
        if user.is_staff:
            return self._api_handler_by_group[request_type]['staff'](
                *args, **kwargs)
        else:
            if user.organization:
                return get_fn_by_user_group(
                    user, self._api_handler_by_group[request_type])(
                        *args, **kwargs)
            else:
                raise exceptions.PermissionDenied(
                    {"detail": "You must be part of an organization."})


class CoreAPIViewBase(GenericAPIView):
    """
    Defines the base class for the rest api views.
    """

    pagination_class = PaginationConfig
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]


class CoreListCreateDestroyView(
        ListCreateAPIView, DestroyAPIView, CoreAPIViewBase, BaseAPIHandler):
    """
    Defines the base list-create-destroy view that will be extended by our
    applications for model specific list-create-destroy views.
    """

    def __init__(self):
        super(CoreListCreateDestroyView, self).__init__()
        BaseAPIHandler.__init__(
            self,
            model=self.queryset.model,
            get_is_list=True)

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.

        To be implemented by the child class.
        """
        raise NotImplementedError()

    def get_serializer_class(self):
        """
        Returns separate serializer classes for get/put/patch requests.
        """

        if self.request.method == 'GET':
            return self._get_list_serializer_class()
        if self.request.method == 'POST':
            return self._get_create_serializer_class()

    def _get_list_serializer_class(self):
        """
        Returns the list serializer.
        """
        raise NotImplementedError()

    def _get_create_serializer_class(self):
        """
        Returns the create serializer.
        """
        raise NotImplementedError()

    def _define_api_handler_by_group(self):
        """
        Returns a dictionary mapping user group to rest api handler functions
        that will be called if the request user is in that user group.
        """
        return {
            'get': {
                'staff': self._get_queryset_by_staff,
            },
            'create': {
                'staff': self._perform_create_by_staff,
            }
        }

    def get_queryset(self):
        """
        Implements the get_queryset function. Any final modifications to the
        query set are made here.
        """
        return self._call_api_by_group(
            self.request.user, 'get', request=self.request).order_by(
                self._order_by())

    def perform_create(self, serializer):
        """
        Implements the customized perform_create functionalty.
        """
        self._call_api_by_group(
            self.request.user, 'create', serializer=serializer)

    def destroy(self, request, *args, **kwargs):
        """
        Implements the customized destroy functionalty for list of ids.
        """
        instance = self.get_queryset()
        if not instance:
            raise exceptions.NotFound()

        try:
            self.perform_destroy(instance)
        except ProtectedError as error:
            return Response(data={
                "error": str(error)},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(data={
            "msg": "Object(s) deleted successfully."},
            status=status.HTTP_200_OK)


class CoreRetrieveUpdateDestroyView(
        RetrieveUpdateDestroyAPIView, CoreAPIViewBase, BaseAPIHandler):
    """
    Defines the base retrieve-update-destroy view that will be extended by our
    applications for model specific retrieve-update-destroy views.
    """

    def __init__(self):
        super(CoreRetrieveUpdateDestroyView, self).__init__()
        BaseAPIHandler.__init__(
            self,
            model=self.queryset.model,
            get_is_list=False)

    def get_serializer_class(self):
        """
        Returns separate serializer classes for get/put/patch requests.
        """

        if self.request.method == 'GET':
            return self._get_detail_serializer_class()
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return self._get_update_serializer_class()

    def _get_detail_serializer_class(self):
        """
        Returns the detail serializer.
        """
        raise NotImplementedError()

    def _get_update_serializer_class(self):
        """
        Returns the update serializer.
        """
        raise NotImplementedError()

    def _perform_update_by_staff(self, serializer):
        """
        Implements perform_update for staff users.
        """
        serializer.save()

    def _define_api_handler_by_group(self):
        """
        Returns a dictionary mapping user group to rest api handler functions
        that will be called if the request user is in that user group.
        """
        return {
            'get': {
                'staff': self._get_queryset_by_staff,
            },
            'update': {
                'staff': self._perform_update_by_staff,
            }
        }

    def get_queryset(self):
        """
        Implements the get_queryset function. Any final modifications to the
        query set are made here.
        """
        return self._call_api_by_group(
            self.request.user, 'get', request=self.request)

    def perform_update(self, serializer):
        """
        Implements the customized perform_update functionalty.
        """
        return self._call_api_by_group(
            self.request.user, 'update', serializer=serializer)

    def destroy(self, request, *args, **kwargs):
        """
        Implements the customized destroy functionalty for a different response
        on deletion of item.
        """

        # pylint: disable=no-member
        try:
            _ = super().destroy(request, *args, **kwargs)
        except ProtectedError as error:
            return Response(data={
                "error": str(error)},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(data={
            "msg": "Object(s) deleted successfully."},
            status=status.HTTP_200_OK)
