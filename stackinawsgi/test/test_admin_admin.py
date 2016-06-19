"""
Stack-In-A-WSGI: stackinawsgi.admin.admin.StackInAWsgiSessionManager
"""
import unittest

from stackinabox.services.service import StackInABoxService
from stackinabox.services.hello import HelloService

from stackinawsgi.admin.admin import StackInAWsgiAdmin
from stackinawsgi.session.service import (
    global_sessions,
    StackInAWsgiSessionManager
)
from stackinawsgi.wsgi.request import Request
from stackinawsgi.wsgi.response import Response
from stackinawsgi.test.helpers import make_environment


class TestSessionManager(unittest.TestCase):
    """
    Test the interaction of StackInAWSGI's Session Manager
    """

    def setUp(self):
        """
        configure env for the test
        """
        self.manager = StackInAWsgiSessionManager()
        self.manager.register_service(HelloService)
        self.base_uri = 'test://testing-url'

    def tearDown(self):
        """
        clean up after the test
        """
        keys = tuple(global_sessions.keys())
        for k in keys:
            del global_sessions[k]

    def test_construction(self):
        """
        test basic construction of the admin interface
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)
        self.assertIsInstance(admin, StackInABoxService)
        self.assertEqual(id(self.manager), id(admin.manager))
        self.assertTrue(admin.base_uri.startswith(self.base_uri))

    def test_property_base_uri_with_no_slash(self):
        """
        test basic construction of the admin interface
        """
        base_uri = 'hello'
        admin = StackInAWsgiAdmin(self.manager, base_uri)
        self.assertIsInstance(admin, StackInABoxService)
        self.assertEqual(id(self.manager), id(admin.manager))
        self.assertTrue(admin.base_uri.startswith(base_uri))

    def test_property_base_uri_start_with_slash(self):
        """
        test basic construction of the admin interface
        """
        base_uri = '/hello'
        admin = StackInAWsgiAdmin(self.manager, base_uri)
        self.assertIsInstance(admin, StackInABoxService)
        self.assertEqual(id(self.manager), id(admin.manager))
        self.assertTrue(admin.base_uri.startswith(base_uri[1:]))

    def test_property_base_uri_ends_with_slash(self):
        """
        """
        base_uri = 'hello/'
        admin = StackInAWsgiAdmin(self.manager, base_uri)
        self.assertIsInstance(admin, StackInABoxService)
        self.assertEqual(id(self.manager), id(admin.manager))
        self.assertTrue(admin.base_uri.startswith(base_uri[:-1]))

    def test_helper_get_session_id(self):
        """
        test extracting the session-id from the headers
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)
        session_id = 'some-session-id'
        headers = {
            'x-session-id': session_id
        }

        extracted_session_id = admin.helper_get_session_id(headers)
        self.assertEqual(session_id, extracted_session_id)

    def test_helper_get_session_id_no_session_id(self):
        """
        test extracting the session-id from the headers
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)
        headers = {}

        extracted_session_id = admin.helper_get_session_id(headers)
        self.assertIsNone(extracted_session_id)

    def test_helper_get_uri(self):
        """
        test building the URI
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)
        session_id = 'some-session-id'
        expected_uri = '{0}/{1}/'.format(self.base_uri, session_id)
        result_uri = admin.helper_get_uri(session_id)
        self.assertEqual(expected_uri, result_uri)

    def test_session_creation(self):
        """
        test creating a new session
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)

        uri = u'/'
        environment = make_environment(
            self,
            method='POST',
            path=uri[1:]
        )
        request = Request(environment)
        response = Response()

        result = admin.create_session(
            request,
            uri,
            response.headers
        )
        response.from_stackinabox(
            result[0],
            result[1],
            result[2]
        )
        # validate response
        self.assertEqual(response.status, 201)
        # validate header entries
        self.assertIn('x-session-id', response.headers)
        self.assertIn('location', response.headers)

        # validate x-session-id
        session_id = response.headers['x-session-id']
        self.assertIn(session_id, global_sessions)

        # validate location
        self.assertEqual(
            '{0}/{1}/'.format(self.base_uri, session_id),
            response.headers['location']
        )

    def test_session_creation_with_session_id(self):
        """
        test creating a new session with a session-id
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)

        session_id = 'my-session-id'
        uri = u'/'
        environment = make_environment(
            self,
            method='POST',
            path=uri[1:],
            headers={
                'x-session-id': session_id
            }
        )
        request = Request(environment)
        self.assertIn('x-session-id', request.headers)
        self.assertEqual(session_id, request.headers['x-session-id'])
        response = Response()

        result = admin.create_session(
            request,
            uri,
            request.headers
        )
        response.from_stackinabox(
            result[0],
            result[1],
            result[2]
        )
        # validate response
        self.assertEqual(response.status, 201)
        # validate header entries
        self.assertIn('x-session-id', response.headers)
        self.assertIn('location', response.headers)

        # validate x-session-id
        extracted_session_id = response.headers['x-session-id']
        self.assertEqual(session_id, extracted_session_id)
        self.assertIn(extracted_session_id, global_sessions)

        # validate location
        self.assertEqual(
            '{0}/{1}/'.format(self.base_uri, extracted_session_id),
            response.headers['location']
        )

    def test_session_remove(self):
        """
        test removing a session
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)

        session_id = self.manager.create_session()
        uri = u'/'
        environment = make_environment(
            self,
            method='DELETE',
            path=uri[1:],
            headers={
                'x-session-id': session_id
            }
        )
        request = Request(environment)
        self.assertIn('x-session-id', request.headers)
        self.assertEqual(session_id, request.headers['x-session-id'])
        response = Response()

        result = admin.remove_session(
            request,
            uri,
            request.headers
        )
        response.from_stackinabox(
            result[0],
            result[1],
            result[2]
        )
        # validate response
        self.assertEqual(response.status, 204)

    def test_session_remove_invalid_session_id(self):
        """
        test removing a session with an invalid session id
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)

        session_id = 'my-session-id'
        uri = u'/'
        environment = make_environment(
            self,
            method='DELETE',
            path=uri[1:],
            headers={
                'x-session-id': session_id
            }
        )
        request = Request(environment)
        self.assertIn('x-session-id', request.headers)
        self.assertEqual(session_id, request.headers['x-session-id'])
        response = Response()

        result = admin.remove_session(
            request,
            uri,
            request.headers
        )
        response.from_stackinabox(
            result[0],
            result[1],
            result[2]
        )
        # validate response
        self.assertEqual(response.status, 404)

    def test_session_reset(self):
        """
        test resetting a session
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)

        session_id = self.manager.create_session()
        uri = u'/'
        environment = make_environment(
            self,
            method='PUT',
            path=uri[1:],
            headers={
                'x-session-id': session_id
            }
        )
        request = Request(environment)
        self.assertIn('x-session-id', request.headers)
        self.assertEqual(session_id, request.headers['x-session-id'])
        response = Response()

        result = admin.reset_session(
            request,
            uri,
            request.headers
        )
        response.from_stackinabox(
            result[0],
            result[1],
            result[2]
        )
        # validate response
        self.assertEqual(response.status, 205)

    def test_session_reset_invalid_session_id(self):
        """
        test resetting a session with an invalid session id
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)

        session_id = 'my-session-id'
        uri = u'/'
        environment = make_environment(
            self,
            method='PUT',
            path=uri[1:],
            headers={
                'x-session-id': session_id
            }
        )
        request = Request(environment)
        self.assertIn('x-session-id', request.headers)
        self.assertEqual(session_id, request.headers['x-session-id'])
        response = Response()

        result = admin.reset_session(
            request,
            uri,
            request.headers
        )
        response.from_stackinabox(
            result[0],
            result[1],
            result[2]
        )
        # validate response
        self.assertEqual(response.status, 404)

    def test_get_session_info(self):
        """
        test resetting a session with an invalid session id
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)

        session_id = 'my-session-id'
        uri = u'/'
        environment = make_environment(
            self,
            method='PUT',
            path=uri[1:],
            headers={
                'x-session-id': session_id
            }
        )
        request = Request(environment)
        self.assertIn('x-session-id', request.headers)
        self.assertEqual(session_id, request.headers['x-session-id'])
        response = Response()

        result = admin.get_session_info(
            request,
            uri,
            request.headers
        )
        response.from_stackinabox(
            result[0],
            result[1],
            result[2]
        )
        # validate response
        self.assertEqual(response.status, 500)
