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


class CoreListCreateDestroyView(ListCreateAPIView, DestroyAPIView):
    """
    Defines the base list-create-destroy view that will be extended by our
    applications for model specific list-create-destroy views.
    """

    pagination_class = PaginationConfig
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'name', 'desc']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }

    def __init__(self):
        super(CoreListCreateDestroyView, self).__init__()
        self._get_queryset_by_group_fn = \
            self._define_get_queryset_by_group_fn()

        self._perform_create_by_group_fn = \
            self._define_perform_create_by_group_fn()

        self.model = self._get_model()

    def _define_get_queryset_by_group_fn(self):
        raise NotImplementedError()

    def _define_perform_create_by_group_fn(self):
        raise NotImplementedError()

    def _get_model(self):
        raise NotImplementedError()

    def _get_fn_by_group(self, user, group_to_fn_map):
        get_queryset_fn = None
        for group in UserGroups:
            if is_in_group(user, group.name):
                get_queryset_fn = group_to_fn_map.get(group, None)
                break
        if get_queryset_fn is None:
            raise exceptions.PermissionDenied()
        return get_queryset_fn

    def _get_id_list(self):
        if self.request.method == "GET":
            return self.request.query_params.getlist('id')
        else:
            return self.request.data.get('id')

    def _get_queryset_by_staff(self):
        id_list = self._get_id_list()
        if id_list:
            return filter_queryset_by_id_list(
                self._get_model().objects, id_list)
        return self._get_model().objects.all()

    def _get_queryset_by_group(self):
        return self._get_fn_by_group(
            self.request.user, self._get_queryset_by_group_fn)()

    def _get_queryset(self):
        if self.request.user.is_staff:
            return self._get_queryset_by_staff()
        else:
            return self._get_queryset_by_group()

    def get_queryset(self):
        return self._get_queryset().order_by('name')

    def _perform_create_by_staff(self, serializer):
        serializer.save()

    def _perform_create_by_group(self, serializer):
        return self._get_fn_by_group(
            self.request.user, self._perform_create_by_group_fn)(serializer)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            return self._perform_create_by_staff(serializer)
        else:
            return self._perform_create_by_group(serializer)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_queryset()
        if not instance:
            raise exceptions.NotFound()
        self.perform_destroy(instance)
        return Response(data={
            "msg": "Object(s) deleted successfully."},
            status=status.HTTP_200_OK)


class CoreRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    Defines the base retrieve-update-destroy view that will be extended by our
    applications for model specific retrieve-update-destroy views.
    """

    pagination_class = PaginationConfig
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'name', 'desc']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }

    def __init__(self):
        super(CoreRetrieveUpdateDestroyView, self).__init__()
        self._get_queryset_by_group_fn = \
            self._define_get_queryset_by_group_fn()

        self.model = self._get_model()

    def _define_get_queryset_by_group_fn(self):
        raise NotImplementedError()

    def _get_model(self):
        raise NotImplementedError()

    def _get_fn_by_group(self, user, group_to_fn_map):
        get_queryset_fn = None
        for group in UserGroups:
            if is_in_group(user, group.name):
                get_queryset_fn = group_to_fn_map.get(group, None)
                break
        if get_queryset_fn is None:
            raise exceptions.PermissionDenied()
        return get_queryset_fn

    def _get_queryset_by_staff(self):
        return self._get_model().objects.all()

    def _get_queryset_by_group(self):
        return self._get_fn_by_group(
            self.request.user, self._get_queryset_by_group_fn)()

    def _get_queryset(self):
        if self.request.user.is_staff:
            return self._get_queryset_by_staff()
        else:
            return self._get_queryset_by_group()

    def get_queryset(self):
        return self._get_queryset().order_by('name')

    def destroy(self, request, *args, **kwargs):
        resp = super(CoreRetrieveUpdateDestroyView, self).destroy(
            request, *args, **kwargs)
        return Response(data={
            "msg": "Object(s) deleted successfully."},
            status=status.HTTP_200_OK)
