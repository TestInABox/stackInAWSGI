"""
Stack-In-A-WSGI: StackInAWsgiAdmin
"""
import json
import logging
import re

from stackinabox.services.service import StackInABoxService

from stackinawsgi.exceptions import InvalidSessionId
from stackinawsgi.session.service import (
    global_sessions,
    session_regex
)


logger = logging.getLogger(__name__)


class StackInAWsgiAdmin(StackInABoxService):
    """
    Stack-In-A-WSGI RESTful Admin API

    :ivar :obj:`StackInAWsgiSessionManager` manager: session manager instance
    :ivar text_type base_uri: base URI for accessing the session to which the
        session uuid will be appended, http://localhost/stackinabox/ which
        would result in http://localhost/stackinabox/<session-id>/
    """

    def __init__(self, session_manager, base_uri):
        """
        Initialize the Admin Interface
        """
        super(StackInAWsgiAdmin, self).__init__('admin')
        self.manager = session_manager
        self.base_uri = base_uri

        self.register(
            StackInABoxService.GET,
            re.compile('^{0}$'.format(session_regex)),
            StackInAWsgiAdmin.get_session_info
        )

        self.register(
            StackInABoxService.DELETE, '/', StackInAWsgiAdmin.remove_session
        )
        self.register(
            StackInABoxService.POST, '/', StackInAWsgiAdmin.create_session
        )
        self.register(
            StackInABoxService.PUT, '/', StackInAWsgiAdmin.reset_session
        )
        self.register(
            StackInABoxService.GET, '/', StackInAWsgiAdmin.get_sessions
        )

    @property
    def base_uri(self):
        """
        Base URI of the WSGI App
        """
        return self.__base_uri

    @base_uri.setter
    def base_uri(self, value):
        """
        Update the Base URI of the WSGI App
        """
        if value.startswith('/'):
            value = value[1:]

        if value.endswith('/'):
            value = value[:-1]

        self.__base_uri = value
        logger.debug(
            'Received Base URI: {0}'.format(
                self.__base_uri
            )
        )

    def helper_get_session_id(self, headers):
        """
        Helper to retrieve the session id or build a new one

        :param dict headers: case insensitive header dictionary
        :returns: text_type with the UUID of the session
        """
        session_id = None

        if 'x-session-id' in headers:
            session_id = headers['x-session-id']
        else:
            logger.debug('x-session-id not in headers')

        logger.debug('Found Session Id: {0}'.format(session_id))
        return session_id

    def helper_get_session_id_from_uri(self, uri):
        """
        Helper to retrieve the Session-ID FROM a URI

        :param text_type uri: complete URI
        :returns: text_type with the session-id
        """
        matcher = re.compile(session_regex)
        try:
            matched_groups = matcher.match(uri)
            session_id = matched_groups.group(0)[1:]
            logger.debug(
                'Helper Get Session From URI - URI: "{0}", '
                'Session ID: "{1}"'.format(
                    uri,
                    session_id
                )
            )

        except Exception:
            logger.exception('Failed to find session-id')
            session_id = None
        return session_id

    def helper_get_uri(self, session_id):
        """
        Helper to build the session URL

        :param text_type session_id: session-id for URL is for
        :returns: text_type, the URL for the session-id
        """
        logger.debug(
            'Helper Get URI - Base URI: "{0}", Session ID: "{1}"'.format(
                self.base_uri,
                session_id
            )
        )
        return '{0}/{1}/'.format(
            self.base_uri,
            session_id
        )

    def create_session(self, request, uri, headers):
        """
        Create a new session

        :param :obj:`Request` request: object containing the HTTP Request
        :param text_type uri: the URI for the request per StackInABox
        :param dict headers: case insensitive header dictionary

        :returns: tuple for StackInABox HTTP Response

        HTTP Request:
            POST /admin/
                X-Session-ID: (Optional) Session-ID to use when creating the
                    new session

        HTTP Responses:
            201 - Session Created
                X-Session-ID header contains the session-id
                Location header contains the URL for the session
        """
        requested_session_id = self.helper_get_session_id(
            headers
        )
        logging.debug(
            'Requested Session Id: {0}'.format(requested_session_id)
        )

        session_id = self.manager.create_session(
            requested_session_id
        )
        logging.debug(
            'Created Session Id: {0}'.format(session_id)
        )

        headers['x-session-id'] = session_id
        headers['location'] = self.helper_get_uri(
            session_id
        )
        return (201, headers, '')

    def remove_session(self, request, uri, headers):
        """
        Remove an existing session

        :param :obj:`Request` request: object containing the HTTP Request
        :param text_type uri: the URI for the request per StackInABox
        :param dict headers: case insensitive header dictionary

        :returns: tuple for StackInABox HTTP Response

        HTTP Request:
            DELETE /admin/
                X-Session-ID: (Required) Session-ID to destroy

        HTTP Responses:
            204 - Session Destroyed
            404 - Session-ID Not Found
        """
        try:
            self.manager.remove_session(
                self.helper_get_session_id(
                    headers
                )
            )

        except InvalidSessionId as ex:
            return (404, headers, str(ex))
        else:
            return (204, headers, '')

    def reset_session(self, request, uri, headers):
        """
        Reset the session; shortcut for removing and creating the session
        while preserving the session-id.

        :param :obj:`Request` request: object containing the HTTP Request
        :param text_type uri: the URI for the request per StackInABox
        :param dict headers: case insensitive header dictionary

        :returns: tuple for StackInABox HTTP Response

        HTTP Request:
            PUT /admin/
                X-Session-ID: (Required) Session-ID to reset

        HTTP Responses:
            205 - Session Reset
            404 - Session-ID Not Found
        """
        try:
            self.manager.reset_session(
                self.helper_get_session_id(
                    headers
                )
            )

        except InvalidSessionId as ex:
            return (404, headers, str(ex))
        else:
            return (205, headers, '')

    def get_session_info(self, request, uri, headers):
        """
        Get Session Information - TBD

        :param :obj:`Request` request: object containing the HTTP Request
        :param text_type uri: the URI for the request per StackInABox
        :param dict headers: case insensitive header dictionary

        :returns: tuple for StackInABox HTTP Response

        HTTP Request:
            GET /admin/{X-Session-ID}
                X-Session-ID: (Required) Session-ID to reset

        HTTP Responses:
            200 - Session Data in JSON format
        """
        requested_session_id = self.helper_get_session_id_from_uri(
            uri
        )

        session_info = {
            'session_valid': requested_session_id in global_sessions,
            'created-time': None,
            'accessed-time': None,
            'accessed-count': 0,
            'http-status': {}
        }

        if session_info['session_valid']:
            session = global_sessions[requested_session_id]
            session_info['created-time'] = session.created_at.isoformat()
            session_info['accessed-time'] = (
                session.last_accessed_at.isoformat()
            )
            session_info['accessed-count'] = session.access_count
            session_info['http-status'] = session.status_tracker

        data = {
            'base_url': self.base_uri,
            'services': {
                svc().name: svc.__name__
                for svc in self.manager.services
            },
            'trackers': {
                'created-time': session_info['created-time'],
                'accessed': {
                    'time': session_info['accessed-time'],
                    'count': session_info['accessed-count']
                },
                'status': session_info['http-status']
            },
            'session_valid': session_info['session_valid']
        }

        return (200, headers, json.dumps(data))

    def get_sessions(self, request, uri, headers):
        """
        Get Session List - TBD

        :param :obj:`Request` request: object containing the HTTP Request
        :param text_type uri: the URI for the request per StackInABox
        :param dict headers: case insensitive header dictionary

        :returns: tuple for StackInABox HTTP Response

        HTTP Request:
            GET /admin/

        HTTP Responses:
            200 - Session List in JSON format
        """
        data = {
            'base_url': self.base_uri,
            'services': {
                svc().name: svc.__name__
                for svc in self.manager.services
            },
            'sessions': [
                requested_session_id
                for requested_session_id in global_sessions
            ]
        }

        return (200, headers, json.dumps(data))
