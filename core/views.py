from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination, status
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework_jwt import authentication

from core.utils import *


class PaginationConfig(pagination.PageNumberPagination):
    """
    Defines the base pagination configuration for our applications
    """
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class CoreAPIView(GenericAPIView):
    """
    Defines the base class for the rest api views.
    """

    pagination_class = PaginationConfig
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'name', 'desc']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }

    def __init__(self):
        super(CoreAPIView, self).__init__()
        self._get_queryset_by_group_fn = \
            self._define_get_queryset_by_group_fn()

        self.model = self._get_model()

    def _define_get_queryset_by_group_fn(self):
        """
        Returns a dictionary mapping user group to get_queryset function
        that will be called if the request user is in that user group.

        To be implemented by the child class.
        """
        raise NotImplementedError()

    def _get_model(self):
        """
        Returns the model associated with the view.

        To be implemented by the child class.
        """
        raise NotImplementedError()

    def _get_queryset_by_staff(self):
        """
        Returns the get queryset for staff users.

        To be implemented by the child class.
        """
        raise NotImplementedError()

    def _get_fn_by_group(self, user, group_to_fn_map):
        """
        Returns the function to be called for the user group the user is in
        given the user group to function map.
        """
        get_queryset_fn = None
        for group in UserGroups:
            if is_in_group(user, group.name):
                get_queryset_fn = group_to_fn_map.get(group, None)
                break
        if get_queryset_fn is None:
            raise exceptions.PermissionDenied()
        return get_queryset_fn

    def _get_id_list(self):
        """
        Returns the list of ids based on different request types.
        """
        if self.request.method == "GET":
            return self.request.query_params.getlist('id')
        else:
            return self.request.data.get('id')

    def _get_queryset_by_group(self):
        """
        Returns the get queryset for individual user groups as defined by the
        [_get_queryset_by_group_fn] dictionary initialized in child class.
        """
        return self._get_fn_by_group(
            self.request.user, self._get_queryset_by_group_fn)()

    def _get_queryset(self):
        """
        Implements the customized get_queryset functionalty.
        """
        if self.request.user.is_staff:
            return self._get_queryset_by_staff()
        else:
            return self._get_queryset_by_group()

    def _perform_create_by_staff(self, serializer):
        """
        Implements perform_create for staff users.

        To be implemented by the child class.
        """
        raise NotImplementedError()

    def _perform_create_by_group(self, serializer):
        """
        Calls the get queryset for individual user groups as defined by the
        [_perform_create_by_group_fn] dictionary initialized in child class.
        """
        return self._get_fn_by_group(
            self.request.user, self._perform_create_by_group_fn)(serializer)


class CoreListCreateDestroyView(
        ListCreateAPIView, DestroyAPIView, CoreAPIView):
    """
    Defines the base list-create-destroy view that will be extended by our
    applications for model specific list-create-destroy views.
    """

    def __init__(self):
        super(CoreListCreateDestroyView, self).__init__()
        self._perform_create_by_group_fn = \
            self._define_perform_create_by_group_fn()

    def _get_queryset_by_staff(self):
        """
        Returns the get queryset for staff users.
        """
        id_list = self._get_id_list()
        if id_list:
            return filter_queryset_by_id_list(
                self._get_model().objects, id_list)
        return self._get_model().objects.all()

    def _perform_create_by_staff(self, serializer):
        """
        Implements perform_create for staff users.
        """
        serializer.save()

    def get_queryset(self):
        """
        Implements the get_queryset function. Any final modifications to the
        query set are made here.
        """
        return self._get_queryset().order_by('name')

    def perform_create(self, serializer):
        """
        Implements the customized perform_create functionalty.
        """
        if self.request.user.is_staff:
            return self._perform_create_by_staff(serializer)
        else:
            return self._perform_create_by_group(serializer)

    def destroy(self, request, *args, **kwargs):
        """
        Implements the customized destroy functionalty for list of ids.
        """
        instance = self.get_queryset()
        if not instance:
            raise exceptions.NotFound()
        self.perform_destroy(instance)
        return Response(data={
            "msg": "Object(s) deleted successfully."},
            status=status.HTTP_200_OK)


class CoreRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView, CoreAPIView):
    """
    Defines the base retrieve-update-destroy view that will be extended by our
    applications for model specific retrieve-update-destroy views.
    """

    def __init__(self):
        super(CoreRetrieveUpdateDestroyView, self).__init__()

    def _get_queryset_by_staff(self):
        """
        Returns the get queryset for staff users.
        """
        return self._get_model().objects.all()

    def get_queryset(self):
        """
        Implements the get_queryset function. Any final modifications to the
        query set are made here.
        """
        return self._get_queryset()

    def destroy(self, request, *args, **kwargs):
        """
        Implements the customized destroy functionalty for a different response
        on deletion of item.
        """
        resp = super(CoreRetrieveUpdateDestroyView, self).destroy(
            request, *args, **kwargs)
        return Response(data={
            "msg": "Object(s) deleted successfully."},
            status=status.HTTP_200_OK)
