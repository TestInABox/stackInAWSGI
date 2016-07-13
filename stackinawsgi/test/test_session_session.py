"""
Stack-In-A-WSGI: stackinawsgi.session.session.Session testing
"""
import unittest
from threading import Lock
import uuid

import ddt
import mock

from stackinabox.stack import StackInABox
from stackinabox.services.hello import HelloService

from stackinawsgi.exceptions import (
    InvalidSessionId,
    InvalidServiceList,
    NoServicesProvided
)
from stackinawsgi.session.session import Session


@ddt.ddt
class TestSessionSession(unittest.TestCase):
    """
    Test the interaction of StackInAWSGI's Session object
    """

    def setUp(self):
        """
        configure env for the test
        """
        self.session_id = str(uuid.uuid4())
        self.services = [HelloService]

    def tearDown(self):
        """
        clean up after the test
        """
        pass

    def test_contstruction_invalid_session_id(self):
        """
        Test construction of a session object with an invalid session id
        """
        with self.assertRaises(InvalidSessionId):
            Session(None, [HelloService])

    @ddt.unpack
    @ddt.data(
        ([], NoServicesProvided),
        (None, InvalidServiceList),
    )
    def test_construction_with_invalid_services(self, invalid_service_value,
                                                expected_exception):
        """
        test construction of a session object with a series of invalid values
        """
        with self.assertRaises(expected_exception):
            Session('invalid-services-list-testing', invalid_service_value)

    def test_construction(self):
        """
        Test successful construction and init_services()
        """

        session = Session(self.session_id, self.services)
        self.assertEqual(self.session_id, session.session_id)
        self.assertEqual(self.services, session.services)
        self.assertTrue(isinstance(session.lock, type(Lock())))
        self.assertTrue(isinstance(session.stack, StackInABox))
        self.assertEqual(session.session_id, session.stack.base_url)
        self.assertEqual(len(self.services), len(session.stack.services))
        self.assertEqual(0, session.access_count)
        self.assertEqual(session.created_at, session.last_accessed_at)
        self.assertEqual(0, len(session.status_tracker))
        tuple_services = tuple(self.services)
        for _, v in session.stack.services.items():
            _, svc = v
            self.assertIsInstance(svc, tuple_services)

    def test_base_url(self):
        """
        Test Base URL
        """
        def validate(s, b):
            self.assertEqual(0, s.access_count)
            self.assertEqual(s.created_at, s.last_accessed_at)
            self.assertEqual(
                b,
                s.base_url
            )
            self.assertEqual(
                b,
                s.stack.base_url
            )

        session = Session(self.session_id, self.services)
        validate(session, self.session_id)

        new_base_url = 'howdy-from-the-test'
        session.base_url = new_base_url
        validate(session, new_base_url)

    def test_reset(self):
        """
        test resetting
        """
        def get_service_instance_info(s):
            list_ids = {}
            for k, v in s.stack.services.items():
                m, svc = v
                list_ids[(k, m)] = id(svc)
            return list_ids

        session = Session(self.session_id, self.services)
        self.assertEqual(0, session.access_count)
        self.assertEqual(session.created_at, session.last_accessed_at)
        self.assertEqual(0, len(session.status_tracker))

        original_session_ids = get_service_instance_info(session)

        session.reset()

        self.assertEqual(1, session.access_count)
        self.assertLess(session.created_at, session.last_accessed_at)
        self.assertEqual(0, len(session.status_tracker))

        new_session_ids = get_service_instance_info(session)

        for k, v in original_session_ids.items():
            self.assertIn(k, new_session_ids)
            self.assertNotEqual(v, new_session_ids[k])

    def test_call(self):
        """
        test calling into the session
        """
        result = (200, {}, "we're all good")
        mock_session_stack_call = mock.Mock()
        mock_session_stack_call.return_value = result

        session = Session(self.session_id, self.services)
        session.stack.call = mock_session_stack_call
        self.assertEqual(0, session.access_count)
        self.assertEqual(session.created_at, session.last_accessed_at)
        self.assertEqual(0, len(session.status_tracker))

        self.assertEqual(mock_session_stack_call.call_count, 0)
        self.assertEqual(session.call('hello', 'world'), result)
        self.assertTrue(mock_session_stack_call.called)
        self.assertEqual(mock_session_stack_call.call_count, 1)
        self.assertEqual(
            mock_session_stack_call.call_args,
            (('hello', 'world'),)
        )
        self.assertEqual(1, session.access_count)
        self.assertLess(session.created_at, session.last_accessed_at)
        self.assertIn(result[0], session.status_tracker)
        self.assertEqual(1, session.status_tracker[result[0]])

    def test_try_handle_route(self):
        """
        test calling the session request handler
        """
        result = (200, {}, "we're all good")
        mock_session_try_handle_route = mock.Mock()
        mock_session_try_handle_route.return_value = result

        session = Session(self.session_id, self.services)
        session.stack.try_handle_route = mock_session_try_handle_route
        self.assertEqual(0, session.access_count)
        self.assertEqual(session.created_at, session.last_accessed_at)
        self.assertEqual(0, len(session.status_tracker))

        self.assertEqual(mock_session_try_handle_route.call_count, 0)
        self.assertEqual(session.try_handle_route('hello', 'world'), result)
        self.assertTrue(mock_session_try_handle_route.called)
        self.assertEqual(mock_session_try_handle_route.call_count, 1)
        self.assertEqual(
            mock_session_try_handle_route.call_args,
            (('hello', 'world'),)
        )
        self.assertEqual(1, session.access_count)
        self.assertLess(session.created_at, session.last_accessed_at)
        self.assertIn(result[0], session.status_tracker)
        self.assertEqual(1, session.status_tracker[result[0]])

    def test_request(self):
        """
        test calling the session request handler
        """
        result = (200, {}, "we're all good")
        mock_session_request = mock.Mock()
        mock_session_request.return_value = result

        session = Session(self.session_id, self.services)
        session.stack.request = mock_session_request
        self.assertEqual(0, session.access_count)
        self.assertEqual(session.created_at, session.last_accessed_at)
        self.assertEqual(0, len(session.status_tracker))

        self.assertEqual(mock_session_request.call_count, 0)
        self.assertEqual(session.request('hello', 'world'), result)
        self.assertTrue(mock_session_request.called)
        self.assertEqual(mock_session_request.call_count, 1)
        self.assertEqual(
            mock_session_request.call_args,
            (('hello', 'world'),)
        )
        self.assertEqual(1, session.access_count)
        self.assertLess(session.created_at, session.last_accessed_at)
        self.assertIn(result[0], session.status_tracker)
        self.assertEqual(1, session.status_tracker[result[0]])

    def test_sub_request(self):
        """
        test calling the session sub_request handler
        """
        result = (200, {}, "we're all good")
        mock_session_sub_request = mock.Mock()
        mock_session_sub_request.return_value = result

        session = Session(self.session_id, self.services)
        session.stack.sub_request = mock_session_sub_request
        self.assertEqual(0, session.access_count)
        self.assertEqual(session.created_at, session.last_accessed_at)
        self.assertEqual(0, len(session.status_tracker))

        self.assertEqual(mock_session_sub_request.call_count, 0)
        self.assertEqual(session.sub_request('hello', 'world'), result)
        self.assertTrue(mock_session_sub_request.called)
        self.assertEqual(mock_session_sub_request.call_count, 1)
        self.assertEqual(
            mock_session_sub_request.call_args,
            (('hello', 'world'),)
        )
        self.assertEqual(1, session.access_count)
        self.assertLess(session.created_at, session.last_accessed_at)
        self.assertIn(result[0], session.status_tracker)
        self.assertEqual(1, session.status_tracker[result[0]])
