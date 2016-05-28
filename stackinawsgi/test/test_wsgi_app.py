"""
Stack-In-A-WSGI: wsgi.app.App testing
"""
from __future__ import print_function

import unittest

from stackinabox.services.hello import HelloService
from stackinabox.stack import StackInABox

from stackinawsgi.wsgi.app import App
from stackinawsgi.wsgi.request import Request
from stackinawsgi.wsgi.response import Response
from stackinawsgi.test.helpers import (
    InvalidService,
    WsgiMock,
    make_environment
)


class TestWsgiApp(unittest.TestCase):
    """
    Stack-In-A-WSGI's wsgi.app.App test suite
    """

    def setUp(self):
        """
        Test setup
        """
        self.apps = [
            HelloService()
        ]

    def tearDown(self):
        """
        Test Teardown
        """
        pass

    def test_construction(self):
        """
        Basic App creation w/o any StackInABoxServices
        """
        the_app = App()
        self.assertTrue(hasattr(the_app, 'stackinabox'))
        self.assertIsInstance(the_app.stackinabox, StackInABox)
        self.assertEqual(len(the_app.stackinabox.services), 0)

    def test_construction_with_service(self):
        """
        Basic App creation with a StackInABoxService
        """
        the_app = App(self.apps)
        self.assertTrue(hasattr(the_app, 'stackinabox'))
        self.assertIsInstance(the_app.stackinabox, StackInABox)
        self.assertEqual(len(the_app.stackinabox.services), 1)
        for an_app in self.apps:
            self.assertIn(an_app.name, the_app.stackinabox.services)
            self.assertEqual(
                an_app,
                the_app.stackinabox.services[an_app.name][1]
            )

    def test_construction_with_invalid_service(self):
        """
        Basic App creation with an invalid StackInABoxService
        """
        with self.assertRaises(TypeError):
            App([InvalidService()])

    def test_reset(self):
        """
        Reset a StackInAWSGI
        """
        the_app = App(self.apps)
        self.assertTrue(hasattr(the_app, 'stackinabox'))
        self.assertIsInstance(the_app.stackinabox, StackInABox)
        self.assertEqual(len(the_app.stackinabox.services), 1)
        the_app.ResetStackInABox()
        self.assertEqual(len(the_app.stackinabox.services), 0)

    def test_holdonto(self):
        """
        Add an object into the StackInABox Hold via StackInAWSGI
        """
        hold_name = 'some-thing'
        hold_value = 'some-value'

        the_app = App()
        self.assertEqual(len(the_app.stackinabox.holds), 0)
        the_app.StackInABoxHoldOnto(hold_name, hold_value)
        self.assertEqual(len(the_app.stackinabox.holds), 1)
        self.assertIn(hold_name, the_app.stackinabox.holds)
        self.assertEqual(hold_value, the_app.stackinabox.holds[hold_name])

    def test_holdout(self):
        """
        Get something out of a StackInABox Hold via StackInAWSGI
        """
        hold_name = 'some-other-thing'
        hold_value = 'some-other-value'

        the_app = App()
        the_app.StackInABoxHoldOnto(hold_name, hold_value)

        retrieved_value = the_app.StackInABoxHoldOut(hold_name)
        self.assertEqual(hold_value, retrieved_value)

    def test_base_url(self):
        """
        Update the URI for a StackInBox under StackInAWSGI
        """
        the_app = App()

        new_url = '/different/url'

        default_base_url = the_app.stackinabox.base_url
        the_app.StackInABoxUriUpdate(new_url)
        self.assertNotEqual(default_base_url, the_app.stackinabox.base_url)
        self.assertEqual(new_url, the_app.stackinabox.base_url)

    def test_default_returns_597(self):
        """
        Validate that calling into StackInAWSGI without any services will
        yield an HTTP 597 error code, a StackInABox HTTP error for invalid
        StackInABoxService
        """
        the_app = App()
        the_app.StackInABoxUriUpdate('localhost')
        environment = make_environment(self, path=u'/howdy')

        request = Request(environment)
        response = Response()

        the_app.CallStackInABox(request, response)
        self.assertEqual(response.status, 597)

    def test_handle_hello_service(self):
        """
        Validate that calling into StackInAWSGI with a loaded StackInBoxService
        will the response from the StackInABoxService by directly calling into
        the StackInAWSGI handler
        """
        the_app = App([HelloService()])
        the_app.StackInABoxUriUpdate('localhost')
        environment = make_environment(self, method='GET', path=u'/hello/')

        request = Request(environment)
        response = Response()

        the_app.CallStackInABox(request, response)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, 'Hello')

    def test_handle_as_callable(self):
        """
        Validate that calling into StackInAWSGI with a loaded StackInBoxService
        will the response from the StackInABoxService by into StackInAWSGI as
        a WSGI Callable per PEP-3333.
        """
        the_app = App([HelloService()])
        the_app.StackInABoxUriUpdate('localhost')
        environment = make_environment(self, method='GET', path=u'/hello/')

        wsgi_mock = WsgiMock()
        response_body = ''.join(the_app(environment, wsgi_mock))
        self.assertEqual(wsgi_mock.status, '200')
        self.assertEqual(response_body, 'Hello')
