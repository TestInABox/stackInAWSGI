"""
Stack-In-A-WSGI: stackinawsgi.session.service.StackInAWsgiSessionManager
"""

import unittest
import uuid

from stackinabox.services.service import StackInABoxService
from stackinabox.services.hello import HelloService

from stackinawsgi.exceptions import (
    InvalidSessionId
)
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
        self.session_id = str(uuid.uuid4())

    def tearDown(self):
        """
        clean up after the test
        """
        keys = tuple(global_sessions.keys())
        for k in keys:
            del global_sessions[k]

    def test_session_id_extraction_with_session(self):
        """
        test extracting an ID from a URI with session
        """
        self.assertEqual(
            self.session_id,
            StackInAWsgiSessionManager.extract_session_id(
                '/{0}/'.format(
                    self.session_id
                )
            )
        )

    def test_session_id_extraction_without_session(self):
        """
        test extracting an ID from a URI without session
        """
        self.assertIsNone(
            StackInAWsgiSessionManager.extract_session_id(
                '/'
            )
        )

    def test_construction(self):
        """
        test basic construction of the manager
        """
        manager = StackInAWsgiSessionManager()

        self.assertIsInstance(manager, StackInABoxService)
        self.assertTrue(hasattr(manager, 'services'))
        self.assertEqual(len(manager.services), 0)

    def test_base_url(self):
        """
        Test Base URL
        """
        def validate(s, b):
            self.assertEqual(
                b,
                s.base_url
            )

        manager = StackInAWsgiSessionManager()

        new_base_url = 'howdy-from-the-test'
        manager.base_url = new_base_url
        validate(manager, new_base_url)

    def test_register(self):
        """
        test registering a service modifies the global services
        """
        manager = StackInAWsgiSessionManager()

        self.assertEqual(len(manager.services), 0)
        manager.register_service(HelloService)
        self.assertEqual(len(manager.services), 1)

    def test_create_session_no_session_id(self):
        """
        test creating a session
        """
        manager = StackInAWsgiSessionManager()
        manager.register_service(HelloService)

        session_id = manager.create_session()
        self.assertIn(session_id, global_sessions)

    def test_create_session_with_session_id(self):
        """
        test creating a session with a session id
        """
        manager = StackInAWsgiSessionManager()
        manager.register_service(HelloService)

        existing_session_id = 'christopher-columbus'
        session_id = manager.create_session(
            session_id=existing_session_id
        )
        self.assertEqual(
            existing_session_id,
            session_id
        )
        self.assertIn(session_id, global_sessions)

    def test_create_an_existing_session(self):
        """
        test creating a session using an existing session id
        """
        manager = StackInAWsgiSessionManager()
        manager.register_service(HelloService)

        session_id = manager.create_session()
        self.assertIn(session_id, global_sessions)

        new_session_id = manager.create_session(
            session_id=session_id
        )
        self.assertEqual(
            session_id,
            new_session_id
        )
        self.assertIn(session_id, global_sessions)

    def test_reset_session(self):
        """
        test reseting a session
        """
        manager = StackInAWsgiSessionManager()
        manager.register_service(HelloService)

        session_id = manager.create_session()
        self.assertIn(session_id, global_sessions)

        manager.reset_session(session_id)
        self.assertIn(session_id, global_sessions)

    def test_reset_session_invalid_session_id(self):
        """
        test reseting an invalid session id
        """
        manager = StackInAWsgiSessionManager()

        with self.assertRaises(InvalidSessionId):
            manager.reset_session('some invalid id')

    def test_remove_session(self):
        """
        test removing a session
        """
        manager = StackInAWsgiSessionManager()
        manager.register_service(HelloService)

        session_id = manager.create_session()
        self.assertIn(session_id, global_sessions)

        manager.remove_session(session_id)
        self.assertNotIn(session_id, global_sessions)

    def test_remove_invalid_session(self):
        """
        test removing an invalid session id
        """
        manager = StackInAWsgiSessionManager()

        with self.assertRaises(InvalidSessionId):
            manager.remove_session('some invalid id')

    def test_request(self):
        """
        test making a request into a session
        """
        manager = StackInAWsgiSessionManager()
        manager.register_service(HelloService)
        session_id = manager.create_session()

        uri = u'/{0}/hello/'.format(session_id)
        environment = make_environment(
            self,
            method='GET',
            path=uri[1:]
        )
        request = Request(environment)
        response = Response()

        result = manager.request(
            request.method,
            request,
            uri,
            request.headers
        )
        response.from_stackinabox(
            result[0],
            result[1],
            result[2]
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, 'Hello')

    def test_request_invalid_session(self):
        """
        test trying to find a non-existent session
        """
        manager = StackInAWsgiSessionManager()
        manager.register_service(HelloService)

        uri = u'/some-invalid-id/hello/'
        environment = make_environment(
            self,
            method='GET',
            path=uri[1:]
        )
        request = Request(environment)
        response = Response()

        result = manager.request(
            request.method,
            request,
            uri,
            request.headers
        )
        response.from_stackinabox(
            result[0],
            result[1],
            result[2]
        )
        self.assertEqual(response.status, 594)

    def test_request_no_session_in_url(self):
        """
        test failing to extract a session from the uri
        """
        manager = StackInAWsgiSessionManager()
        manager.register_service(HelloService)

        uri = u'/'
        environment = make_environment(
            self,
            method='GET',
            path=uri[1:]
        )
        request = Request(environment)
        response = Response()

        result = manager.request(
            request.method,
            request,
            uri,
            request.headers
        )
        response.from_stackinabox(
            result[0],
            result[1],
            result[2]
        )
        self.assertEqual(response.status, 593)
