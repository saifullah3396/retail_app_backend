
"""
Defines the base functionality for unit tests generation for our applications.
"""

from functools import partial

import factory
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.utils.module_loading import import_string
from factory.base import StubObject
from rest_framework.authtoken.models import Token
from rest_framework_jwt.settings import api_settings

from backend import settings

# define payload handler for generating JWT token in tests
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER

# define encode handler for generating JWT token in tests
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

# use JWT authentication tokens?
JWT_AUTH = True


def generate_token(user):
    """
    Generates auth token for user
    """
    if JWT_AUTH:
        payload = JWT_PAYLOAD_HANDLER(user)
        return JWT_ENCODE_HANDLER(payload)
    else:
        token = Token.objects.create(user=user)
        token.save()
        return token


def generate_token_string(token):
    """
    Generates auth token string from token
    """
    if JWT_AUTH:
        return 'JWT {}'.format(token)
    else:
        return 'Token {}'.format(token)


def generate_test_image(name, size=(36, 36)):
    """
    Generates a test image for image fields.
    """
    return ContentFile(
        factory.django.ImageField()._make_data(
            {'width': size[0], 'height': size[1]}
        ), '{}.jpg'.format(name))


def generate_dict_factory(_factory):
    """
    Generates a python dict from factory object.
    """
    def stub_is_list(stub: StubObject):
        try:
            return all(k.isdigit() for k in stub.__dict__.keys())
        except AttributeError:
            return False

    def convert_dict_from_stub(stub: StubObject):
        stub_dict = stub.__dict__
        for key, value in stub_dict.items():
            if isinstance(value, StubObject):
                stub_dict[key] = (
                    [
                        convert_dict_from_stub(v)
                        for v in value.__dict__.values()]
                    if stub_is_list(value)
                    else convert_dict_from_stub(value)
                )
        return stub_dict

    def dict_factory(_factory, **kwargs):
        stub = _factory.stub(**kwargs)
        stub_dict = convert_dict_from_stub(stub)
        return stub_dict

    return partial(dict_factory, _factory)


def generate_fake_data(factory_class, *args, **kwargs):
    """
    Wrapper for generate_dict_factory
    """
    return generate_dict_factory(factory_class)(*args, **kwargs)
