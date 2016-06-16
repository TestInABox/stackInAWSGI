"""
Stack-In-A-WSGI: stackinawsgi.wsgi.request.Request testing
"""
import unittest

import ddt

from stackinawsgi.wsgi.request import Request
from stackinawsgi.test.helpers import (
    make_environment
)


@ddt.ddt
class TestWsgiRequest(unittest.TestCase):
    """
    Test the interaction of StackInAWSGI's Request object

    Request object should be similar to requests's Request object.
    """

    def setUp(self):
        """
        Test setup
        """
        self.environment = make_environment(self)
        self.environment_https = make_environment(self, url_scheme='https')

        self.example_headers = {
            'x-example': 'here'
        }
        self.environment_headers = make_environment(
            self,
            headers=self.example_headers
        )

    def tearDown(self):
        """
        Test Teardown
        """
        pass

    @ddt.unpack
    @ddt.data(
        (None, u'/'),
        ('/', u'/'),
        ('/hello', u'/hello'),
        ('/hello/', u'/hello')
    )
    def test_get_path(self, url, expected_url):
        """
        Test get_path normalization
        """
        result = Request.get_path(url)
        self.assertEqual(result, expected_url)

    def test_construction(self):
        """
        Basic object creation
        """
        self.assertNotIn('QUERY_STRING', self.environment)

        request = Request(self.environment)
        self.assertEqual(request.environment, self.environment)
        self.assertEqual(request.stream, self.environment['wsgi.input'])
        self.assertEqual(request.method, self.environment['REQUEST_METHOD'])
        self.assertEqual(request.path, self.environment['PATH_INFO'])
        self.assertIsNone(request.query)

    def test_construction_without_path(self):
        """
        Basic object creation without any URL path
        """
        self.assertNotIn('QUERY_STRING', self.environment)
        self.environment['PATH_INFO'] = None

        request = Request(self.environment)
        self.assertEqual(request.environment, self.environment)
        self.assertEqual(request.stream, self.environment['wsgi.input'])
        self.assertEqual(request.method, self.environment['REQUEST_METHOD'])
        self.assertEqual(request.path, '/')
        self.assertIsNone(request.query)

    def test_construction_with_nonroot_path(self):
        """
        Basic Object creation with a non-root path (e.g. not simply '/') ending
        without any slash (/)
        """
        self.environment['PATH_INFO'] = u'/happy/days'
        request = Request(self.environment)
        self.assertEqual(request.environment, self.environment)
        self.assertEqual(request.stream, self.environment['wsgi.input'])
        self.assertEqual(request.method, self.environment['REQUEST_METHOD'])
        self.assertEqual(request.path, self.environment['PATH_INFO'])
        self.assertIsNone(request.query)

    def test_construction_with_nonroot_path_ends_with_slash(self):
        """
        Basic Construction with a non-root path (not simply '/') ending with
        a slash (/)
        """
        self.environment['PATH_INFO'] = u'/happy/days/'
        request = Request(self.environment)
        self.assertEqual(request.environment, self.environment)
        self.assertEqual(request.stream, self.environment['wsgi.input'])
        self.assertEqual(request.method, self.environment['REQUEST_METHOD'])
        self.assertEqual(request.path, self.environment['PATH_INFO'][:-1])
        self.assertIsNone(request.query)

    def test_construction_with_qs(self):
        """
        Basic construction with a Query String
        """
        self.assertNotIn('QUERY_STRING', self.environment)
        self.environment['QUERY_STRING'] = 'happy=days'

        request = Request(self.environment)
        self.assertEqual(request.environment, self.environment)
        self.assertEqual(request.stream, self.environment['wsgi.input'])
        self.assertEqual(request.method, self.environment['REQUEST_METHOD'])
        self.assertEqual(request.path, self.environment['PATH_INFO'])
        self.assertEqual(request.query, self.environment['QUERY_STRING'])

    def test_url_property_http(self):
        """
        Validate the re-construction of the HTTP URL without a Query String
        """
        self.assertNotIn('QUERY_STRING', self.environment)

        request = Request(self.environment)
        self.assertIsNone(request.query)

        url = request.url
        self.assertEqual(
            url,
            u"http://localhost/"
        )

    def test_url_property_https(self):
        """
        Validate the re-construction of the HTTPS URL without a Query String
        """
        self.assertNotIn('QUERY_STRING', self.environment_https)

        request = Request(self.environment_https)
        self.assertIsNone(request.query)

        url = request.url
        self.assertEqual(
            url,
            u"https://localhost/"
        )

    def test_url_property_http_alternate_port(self):
        """
        Validate the re-construction of the HTTP URL without a Query String on
        a non-standard HTTP port
        """
        self.assertNotIn('QUERY_STRING', self.environment)
        self.environment['SERVER_PORT'] = str(8080)

        request = Request(self.environment)
        self.assertIsNone(request.query)

        url = request.url
        self.assertEqual(
            url,
            u"http://localhost:8080/"
        )

    def test_url_property_https_alternate_port(self):
        """
        Validate the re-construction of the HTTPS URL without a Query String on
        a non-standard HTTP port
        """
        self.assertNotIn('QUERY_STRING', self.environment_https)
        self.environment_https['SERVER_PORT'] = str(8443)

        request = Request(self.environment_https)
        self.assertIsNone(request.query)

        url = request.url
        self.assertEqual(
            url,
            u"https://localhost:8443/"
        )

    def test_url_property_with_http_host_envvar(self):
        """
        Validate the re-construction of the HTTPS URL without a Query String
        with the HTTP_HOST variable set
        """
        self.assertNotIn('QUERY_STRING', self.environment)
        self.environment['HTTP_HOST'] = "stackinabox:9000"

        request = Request(self.environment)
        self.assertIsNone(request.query)

        url = request.url
        self.assertEqual(
            url,
            u"http://stackinabox:9000/"
        )

    def test_url_property_http_with_qs(self):
        """
        Validate the re-construction of the HTTPS URL with a Query String
        """
        self.assertNotIn('QUERY_STRING', self.environment)
        self.environment['QUERY_STRING'] = 'happy=days'

        request = Request(self.environment)
        self.assertIsNotNone(request.query)

        url = request.url
        self.assertEqual(
            url,
            u"http://localhost/?happy=days"
        )

    def test_headers(self):
        """
        Validate the construction of headers
        """
        request = Request(self.environment_headers)
        self.assertEqual(len(request.headers), 1)
        self.assertIn('x-example', request.headers)
        self.assertEqual(
            request.headers['x-example'],
            self.example_headers['x-example']
        )
