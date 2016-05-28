"""
Stack-In-A-WSGI: stackinawsgi.wsgi.response.Response testing
"""

import unittest

from stackinabox.util.tools import CaseInsensitiveDict

from stackinawsgi.wsgi.response import Response


class TestWsgiRequest(unittest.TestCase):
    """
    Test the interaction of StackInAWSGI's Response object
    """

    def setUp(self):
        """
        Test setup
        """
        self.response = Response()

    def tearDown(self):
        """
        Test Teardown
        """
        pass

    def test_construction(self):
        """
        Test default construction
        """
        self.assertIsInstance(self.response.headers, CaseInsensitiveDict)
        self.assertEqual(self.response.status, 500)
        self.assertEqual(self.response._body, b'Internal Server Error')

    def test_from_stackinabox(self):
        """
        Test building the response based on the response from StackInABox
        """
        status = 599
        headers = {}
        body = b'Response Body'

        self.response.from_stackinabox(status, headers, body)
        self.assertEqual(self.response.status, status)
        self.assertEqual(self.response.headers, CaseInsensitiveDict())
        self.assertEqual(self.response.body, body)

    def test_from_stackinabox_update_headers(self):
        """
        Testing building a response that provides headers to be returned
        to the HTTP client where the headers do not match the dictionary
        that is part of the Response object.
        """
        status = 599
        headers = {'new': 'value'}
        body = b'Response Body'
        expected_headers = CaseInsensitiveDict()
        expected_headers.update(headers)

        self.response.from_stackinabox(status, headers, body)
        self.assertEqual(self.response.status, status)
        self.assertEqual(
            self.response.headers,
            expected_headers
        )
        self.assertEqual(self.response.body, body)

    def test_from_stackinabox_own_headers(self):
        """
        Testing building a response that provides headers to be returned
        to the HTTP client where the headers are the dictionary
        that is part of the Response object.
        """
        status = 599
        headers = {'new': 'value2'}
        body = b'Response Body'
        expected_headers = CaseInsensitiveDict()
        expected_headers.update(headers)
        self.response.headers.update(headers)

        self.response.from_stackinabox(status, self.response.headers, body)
        self.assertEqual(self.response.status, status)
        self.assertEqual(
            self.response.headers,
            expected_headers
        )
        self.assertEqual(self.response.body, body)
