"""
Defines the base functionality for unit tests generation for our applications.
"""

import tempfile

from django.conf import settings as django_settings
from django.core.management import call_command
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework.test import APITestCase, URLPatternsTestCase

from core.tests.utils import generate_token, generate_token_string
from users.models import DefaultUserGroups


class TestsBase(APITestCase, URLPatternsTestCase):
    # pylint: disable=attribute-defined-outside-init
    """
    Generates a test database with example values for different models for
    performing tests
    """
    users = None

    def setUp(self):
        """
        Sets up the test database with example values for different models
        """
        # set media root to temp file
        django_settings.MEDIA_ROOT = tempfile.mkdtemp()

        # call the setup_apps command to generate any common functionality such
        # as groups added separately in the applications.
        call_command('setup_apps', silent=True)

        # generate factory data
        self.generate_factory_data()

        # make sure users are defined
        if not self.users:
            raise ValueError("Users must be defined")

    def generate_factory_data(self):
        """
        Generates factory data that can be used in test cases
        """
        raise NotImplementedError()

    def run_single_test(self, config, show_passed=False):
        """
        Runs a single test as defined in the config. Each test contains
        multiple sub-tests that are called separately.

        :param config: The test configuration. An example configuration is
            shown below:

        config = {
                # name of the test
                'test_name': 'test_name',

                # (get, patch, delete, post, etc)
                'type': 'get',

                # view url name as defined in urls.py
                'path_name': 'url_name',

                # A list of requests. Each request is a sub-test hitting the
                # specified url with specified type
                'request': [
                    {
                        # sub test name
                        'test_name': 'sub_test_1',

                        # query parameters to send
                        'query_args': [query_param_1, query_param_2],

                        # user that is calling the request
                        'user': 'staff_user',

                        # data to be sent, for example, for post requests
                        'data': {
                            'data1': 'data1',
                            'data2': 'data2',
                        },

                        # return status code that should be matched for a
                        # successful run. Test fails if the returned status
                        # code is different from this one
                        'status': status.HTTP_200_OK,

                        # a lambda function that asserts the returned response.
                        # the lambda takes the returned response data and
                        # performs any necessary assertions for the test.
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['name'],
                                'data1')
                        )
                    },
                    {...},
                    ...
                    {...},
        """
        test_name = config['test_name']
        path_name = config['path_name']
        test_base_string = "Test: {}\n".format(test_name)
        for request in config['request']:
            with self.subTest(request=request, test_name=request['name']):
                test_req_string = test_base_string + \
                    "\tRequest: {}\n".format(request['name'])

                query_args = None
                if 'query_args' in request:
                    query_args = request['query_args']
                    url = reverse(path_name, kwargs=query_args)
                else:
                    url = reverse(path_name)

                query_params = None
                if 'query_params' in request:
                    query_params = request['query_params']
                    query_params_enc = urlencode(query_params)
                    url = '{}?{}'.format(url, query_params_enc)

                data = None
                data_format = 'json'
                if 'data' in request:
                    data = request['data']

                if 'data_format' in request:
                    data_format = request['data_format']

                response_check_fn = None
                if 'response_check_fn' in request:
                    response_check_fn = request['response_check_fn']

                for user in self.users.values():
                    post_test_cb = None
                    if 'post_test_cb' in request and request['post_test_cb']:
                        post_test_cb = request['post_test_cb']
                    test_result, response, error = self.call_api(
                        url,
                        user,
                        data,
                        query_args,
                        query_params,
                        config['type'],
                        data_format=data_format,
                        response_check_fn=response_check_fn,
                        post_test_cb=post_test_cb)
                    if not test_result:
                        test_log = test_req_string + \
                            "\t\tBY USER: {}\n\t\tRESULT: FAILED\n\t\tERROR: {}" \
                            "\n\t\tRESPONSE: {}".format(
                                user.username, error, response.data)
                        print(test_log)
                    elif show_passed:
                        test_log = test_req_string + \
                            "\t\tBY USER: {}\n\t\tRESULT: PASSED".format(
                                user.username)
                        print(test_log)

    def call_api(
            self,
            url,
            user,
            data,
            query_args,
            query_params,
            api_type,
            data_format='json',
            response_check_fn=None,
            post_test_cb=None):
        """
        Calls the rest api for tests cases as defined by the input parameters.
        """

        # get authorization string
        auth_string = generate_token_string(self.tokens[user])

        # get api function
        rest_fn = None
        if api_type == 'get':
            rest_fn = self.client.get
        elif api_type == 'post':
            rest_fn = self.client.post
        elif api_type == 'put':
            rest_fn = self.client.put
        elif api_type == 'patch':
            rest_fn = self.client.patch
        elif api_type == 'delete':
            rest_fn = self.client.delete
        else:
            print(
                "Invalid API function type provided. Allowed types are: "
                "[get, post, put, patch, delete]")

        # get data
        if data:
            data = data()

        # call api
        if data:
            response = rest_fn(
                url,
                data=data,
                format=data_format,
                HTTP_AUTHORIZATION=auth_string)
        else:
            response = rest_fn(
                url,
                HTTP_AUTHORIZATION=auth_string)

        try:
            # run post test callback here
            if post_test_cb:
                post_test_cb()

            # then call response check
            if response_check_fn:
                response_check_fn(
                    user=user, data=data, response=response,
                    query_args=query_args, query_params=query_params)
        except AssertionError as error:
            return False, response, error
        else:
            return True, response, None
