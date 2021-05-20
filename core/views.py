"""
Defines the core REST API views on which all other application views will be
based.
"""

import datetime

from django.core.cache import cache
from django.db.models import ProtectedError
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.utils.functional import cached_property
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.views.generic import GenericViewError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, pagination, status
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     GenericAPIView, ListAPIView,
                                     RetrieveAPIView, UpdateAPIView)
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.key_constructor.bits import (KeyBitBase,
                                                            PaginationKeyBit)
from rest_framework_extensions.key_constructor.constructors import \
    DefaultKeyConstructor

# views.py
from backend.settings import CACHE_KEY_GENERATOR
from core.utils import filter_objects_by_lookup_list, get_lookup_list


class UpdatedAtKeyBit(KeyBitBase):
    def get_data(self, view_instance, **kwargs):
        key = CACHE_KEY_GENERATOR(view_instance.queryset.model)
        value = cache.get(key, None)
        if not value:
            value = datetime.datetime.utcnow()
            cache.set(key, value=value)
        return force_str(value)


class CustomObjectKeyConstructor(DefaultKeyConstructor):
    updated_at = UpdatedAtKeyBit()


class CustomListKeyConstructor(DefaultKeyConstructor):
    pagination = PaginationKeyBit()
    updated_at = UpdatedAtKeyBit()


class PaginationConfig(pagination.PageNumberPagination):
    """
    Defines the base pagination configuration for our applications
    """
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class ModelMixin:
    @property
    def model(self):
        return self.queryset.model


class CoreAPIViewBase(GenericAPIView, ModelMixin):
    """
    Defines the base class for the rest api views.
    """

    list_on_get = False
    pagination_class = PaginationConfig
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    list_serializer = None
    create_serializer = None
    retrieve_serializer = None
    update_serializer = None

    def get_serializer_class(self):
        """
        Returns separate serializer classes for get/put/patch requests.
        """

        if self.request.method == 'GET':
            if self.list_on_get:
                if self.list_serializer:
                    return self.list_serializer
                else:
                    raise GenericViewError("List serializer is not provided.")
            else:
                if self.retrieve_serializer:
                    return self.retrieve_serializer
                else:
                    raise GenericViewError(
                        "Retrieve serializer is not provided.")
        elif self.request.method == 'POST':
            if self.create_serializer:
                return self.create_serializer
            else:
                raise GenericViewError("Create serializer is not provided.")
        elif self.request.method == 'PUT' or self.request.method == 'PATCH':
            if self.update_serializer:
                return self.update_serializer
            else:
                raise GenericViewError("Update serializer is not provided.")


class CoreListGetQuerySet(GenericAPIView, ModelMixin):
    order_by = 'id'

    def _get_list_queryset(self, model=None):
        """
        Returns the list queryset for super users.
        """
        if model:
            return model.objects.all()
        else:
            return self.model.objects.all()

    def _get_list_queryset_superuser(self):
        return self._get_list_queryset()

    def _get_list_queryset_user(self):
        return self._get_list_queryset()

    def get_queryset(self):
        """
        Implements the get_queryset function. Any final modifications to the
        query set are made here.
        """
        objects = self.model.objects.none()
        if self.request.user.is_superuser:
            objects = self._get_list_queryset_superuser().order_by(self.order_by)
        else:
            objects = self._get_list_queryset_user().order_by(self.order_by)

        lookup_list = get_lookup_list(self.request, self.lookup_url_kwarg)
        if lookup_list:
            return filter_objects_by_lookup_list(
                objects, lookup_list, self.lookup_url_kwarg)

        return objects

    def validate_kwargs(self):
        return None


class CoreListAPIView(CoreListGetQuerySet, ListAPIView, CoreAPIViewBase):
    """
    Defines the base list view that will be extended by our
    applications for model specific list views.
    """
    lookup_url_kwarg = 'id'
    list_on_get = True  # conflicts with retrieve api view for obvious reasons

    @method_decorator(vary_on_headers("Authorization",))
    @cache_response(key_func=CustomListKeyConstructor())
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CoreCreateAPIView(CreateAPIView, CoreAPIViewBase):
    """
    Defines the base create view that will be extended by our
    applications for model specific create views.
    """

    def _perform_create_superuser(self, serializer):
        serializer.save()

    def _perform_create_user(self, serializer):
        serializer.save()

    def perform_create(self, serializer):
        """
        Implements the customized perform_create functionalty.
        """
        if self.request.user.is_superuser:
            self._perform_create_superuser(serializer)
        else:
            self._perform_create_user(serializer)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CoreListDestroyAPIView(DestroyAPIView, CoreAPIViewBase):
    """
    Defines the base destroy view that will be extended by our
    applications for model specific destroy views.
    """

    def _perform_destroy_superuser(self, instance):
        instance.delete()

    def _perform_destroy_user(self, instance):
        instance.delete()

    def perform_destroy(self, instance):
        """
        Implements the customized perform_destroy functionalty.
        """
        if self.request.user.is_superuser:
            self._perform_destroy_superuser(instance)
        else:
            self._perform_destroy_user(instance)

    def destroy(self, request, *args, **kwargs):
        return self._destroy(request, *args, **kwargs)

    def _destroy(self, request, *args, **kwargs):
        """
        Implements the customized destroy functionalty for list of ids.
        """

        id_list = get_lookup_list(request, self.lookup_url_kwarg)
        if not id_list:
            # objects as default can only be deleted by a list of ids. Direct
            # deletion of all the listed objects is not allowed as it is really
            # unsafe
            raise exceptions.PermissionDenied()

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


class CoreRetrieveGetQueryset(GenericAPIView, ModelMixin):
    def _get_retrieve_queryset(self, model=None):
        if model:
            return model.objects.all()
        else:
            return self.model.objects.all()

    def _get_retrieve_queryset_superuser(self):
        return self._get_retrieve_queryset()

    def _get_retrieve_queryset_user(self):
        return self._get_retrieve_queryset()

    def get_queryset(self):
        """
        Implements the get_queryset function. Any final modifications to the
        query set are made here.
        """

        if self.request.user.is_superuser:
            return self._get_retrieve_queryset_superuser()
        else:
            return self._get_retrieve_queryset_user()

    def validate_kwargs(self):
        return None


class CoreRetrieveAPIView(
        CoreRetrieveGetQueryset, RetrieveAPIView, CoreAPIViewBase):
    """
    Defines the base retrieve view that will be extended by our
    applications for model specific retrieve views.
    """
    list_on_get = False  # conflicts with list api view for obvious reasons

    @method_decorator(vary_on_headers("Authorization",))
    @cache_response(key_func=CustomObjectKeyConstructor())
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CoreUpdateAPIView(
        UpdateAPIView, CoreAPIViewBase):
    """
    Defines the base update view that will be extended by our
    applications for model specific update views.
    """

    def _perform_update_superuser(self, serializer):
        serializer.save()

    def _perform_update_user(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        """
        Implements the customized perform_update functionalty.
        """
        if self.request.user.is_superuser:
            self._perform_update_superuser(serializer)
        else:
            self._perform_update_user(serializer)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class CoreDestroyAPIView(
        DestroyAPIView, CoreAPIViewBase):
    """
    Defines the base destroy view that will be extended by our
    applications for model specific destroy views.
    """

    def _perform_destroy_superuser(self, instance):
        instance.delete()

    def _perform_destroy_user(self, instance):
        instance.delete()

    def perform_destroy(self, instance):
        """
        Implements the customized perform_destroy functionalty.
        """
        if self.request.user.is_superuser:
            self._perform_destroy_superuser(instance)
        else:
            self._perform_destroy_user(instance)

    def destroy(self, request, *args, **kwargs):
        return self._destroy(request, *args, **kwargs)

    def _destroy(self, request, *args, **kwargs):
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
