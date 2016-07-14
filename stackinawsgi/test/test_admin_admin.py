"""
Stack-In-A-WSGI: stackinawsgi.admin.admin.StackInAWsgiSessionManager
"""
import datetime
import json
import unittest

import ddt

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


@ddt.ddt
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
        test the base uri property to ensure the trailing slash
        is removed
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

    @ddt.data(0, 1, 2, 3, 5, 8, 13)
    def test_get_sessions(self, session_count):
        """
        test get sessions
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)

        uri = u'/'
        environment = make_environment(
            self,
            method='GET',
            path=uri[1:],
            headers={}
        )
        request = Request(environment)

        for _ in range(session_count):
            admin.manager.create_session()

        response = Response()
        result = admin.get_sessions(
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
        self.assertEqual(response.status, 200)

        response_body = response.body
        session_data = json.loads(response_body)

        self.assertIn('base_url', session_data)
        self.assertEqual(session_data['base_url'], self.base_uri)

        self.assertIn('services', session_data)
        self.assertEqual(len(session_data['services']), 1)

        self.assertIn('hello', session_data['services'])
        self.assertEqual(session_data['services']['hello'], 'HelloService')

        self.assertIn('sessions', session_data)
        self.assertEqual(len(session_data['sessions']), session_count)

    def test_get_session_info(self):
        """
        test resetting a session with an invalid session id
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)

        session_id = 'my-session-id'
        uri = u'/{0}'.format(session_id)
        environment = make_environment(
            self,
            method='GET',
            path=uri[1:],
            headers={
                'x-session-id': session_id
            }
        )
        request = Request(environment)
        self.assertIn('x-session-id', request.headers)
        self.assertEqual(session_id, request.headers['x-session-id'])

        response_created = Response()
        result_create = admin.create_session(
            request,
            uri,
            request.headers
        )
        response_created.from_stackinabox(
            result_create[0],
            result_create[1],
            result_create[2]
        )
        self.assertEqual(response_created.status, 201)

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
        self.assertEqual(response.status, 200)

        response_body = response.body
        session_data = json.loads(response_body)

        self.assertIn('base_url', session_data)
        self.assertEqual(session_data['base_url'], self.base_uri)

        self.assertIn('session_valid', session_data)
        self.assertTrue(session_data['session_valid'])

        self.assertIn('services', session_data)
        self.assertEqual(len(session_data['services']), 1)

        self.assertIn('hello', session_data['services'])
        self.assertEqual(session_data['services']['hello'], 'HelloService')

        self.assertIn('trackers', session_data)
        self.assertEqual(len(session_data['trackers']), 3)

        self.assertIn('created-time', session_data['trackers'])
        self.assertIsNotNone(session_data['trackers']['created-time'])
        created_time = datetime.datetime.strptime(
            session_data['trackers']['created-time'],
            "%Y-%m-%dT%H:%M:%S.%f"
        )

        self.assertIn('accessed', session_data['trackers'])
        self.assertEqual(len(session_data['trackers']['accessed']), 2)
        self.assertIn('time', session_data['trackers']['accessed'])
        self.assertIsNotNone(session_data['trackers']['accessed']['time'])
        accessed_time = datetime.datetime.strptime(
            session_data['trackers']['accessed']['time'],
            "%Y-%m-%dT%H:%M:%S.%f"
        )
        self.assertEqual(created_time, accessed_time)
        self.assertIn('count', session_data['trackers']['accessed'])

        self.assertIn('status', session_data['trackers'])
        self.assertEqual(len(session_data['trackers']['status']), 0)

    def test_get_session_info_invalid_session(self):
        """
        test resetting a session with an invalid session id
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)

        session_id = 'my-session-id'
        uri = u'/{0}'.format(session_id)

        environment = make_environment(
            self,
            method='PUT',
            path=uri[1:],
        )
        request = Request(environment)

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
        self.assertEqual(response.status, 200)

        response_body = response.body
        session_data = json.loads(response_body)

        self.assertIn('base_url', session_data)
        self.assertEqual(session_data['base_url'], self.base_uri)

        self.assertIn('session_valid', session_data)
        self.assertFalse(session_data['session_valid'])

        self.assertIn('services', session_data)
        self.assertEqual(len(session_data['services']), 1)

        self.assertIn('hello', session_data['services'])
        self.assertEqual(session_data['services']['hello'], 'HelloService')

        self.assertIn('trackers', session_data)
        self.assertEqual(len(session_data['trackers']), 3)

        self.assertIn('created-time', session_data['trackers'])
        self.assertIsNone(session_data['trackers']['created-time'])

        self.assertIn('accessed', session_data['trackers'])
        self.assertEqual(len(session_data['trackers']['accessed']), 2)
        self.assertIn('time', session_data['trackers']['accessed'])
        self.assertIsNone(session_data['trackers']['accessed']['time'])
        self.assertIn('count', session_data['trackers']['accessed'])

        self.assertIn('status', session_data['trackers'])
        self.assertEqual(len(session_data['trackers']['status']), 0)

    def test_extract_session_from_uri(self):
        """
        test extracting a session from the URI - positive test
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)

        session_id = 'my-session-id'
        uri = u'/{0}'.format(session_id)

        extracted_session_id = admin.helper_get_session_id_from_uri(
            uri
        )
        self.assertEqual(session_id, extracted_session_id)

    def test_extract_session_from_uri_invalid(self):
        """
        test extracting a session from the URI - negative test
        """
        admin = StackInAWsgiAdmin(self.manager, self.base_uri)

        uri = u'/'

        extracted_session_id = admin.helper_get_session_id_from_uri(
            uri
        )
        self.assertIsNone(extracted_session_id)
