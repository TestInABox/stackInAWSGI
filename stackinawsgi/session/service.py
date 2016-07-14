"""
Stack-In-A-WSGI: StackInAWsgiSessionManager
"""
from __future__ import absolute_import

import logging
import re
import uuid

from stackinabox.services.service import StackInABoxService

from stackinawsgi.exceptions import (
    InvalidSessionId
)
from .session import Session


# Use a shared dictionary to try to ensure its availability under
# various WSGI servers - e.g gunicorn, uwsgi.
# note: using them multiprocessing functionality means the objects
#       must be able to be pickled, which we can't guarantee. So
#       we're stuck with threading.
global_sessions = dict()
session_regex = '^\/([\w-]+)'
session_regex_instance = '{0}\/.*'.format(session_regex)


logger = logging.getLogger(__name__)


class StackInAWsgiSessionManager(StackInABoxService):
    """
    WSGI Session Manager for StackInABox

    This is a special version of the StackInABoxService object that
    overrides functionality in the base class that is not normally
    overriden in order to provide access to the sessions.

    This module does not provide an HTTP RESTful interface itself.
    The :obj:`StackInAWsgiAdmin` uses this object to dynamically
    manage the available sessions.

    :ivar list services: a list of StackInABoxService objects that
        have not yet been initialized.
    """

    def __init__(self):
        """
        Initialize the session manager
        """
        super(StackInAWsgiSessionManager, self).__init__('stackinabox')
        logger.debug('Initializing Service Manager')
        self.services = []

    @staticmethod
    def extract_session_id(uri):
        """
        Helper to extract a session-id from the URI

        :param text_type uri: URI from the caller to extract the session-id
            from.

        :returns: None if session-id was not extractable, or a text_type
            containing the session-id.
        """
        logger.debug(
            'Attempting to extract session id from URI: {0}'.format(
                uri
            )
        )
        matcher = re.compile(session_regex_instance)

        matches = matcher.match(uri)
        if matches:
            session_id = matches.groups()[0]
            logger.debug(
                'Extracted session id {0} from {1}'.format(
                    session_id,
                    uri
                )
            )
            return session_id

        else:
            logger.debug(
                'Failed to find any session id in {0}'.format(
                    uri
                )
            )
            return None

    @property
    def base_url(self):
        """
        Base URI for the this module

        :returns: text_type with the base URI
        """
        return self.__base_url

    @base_url.setter
    def base_url(self, value):
        """
        Setter for the Base URI

        :param text_type value: base URI to use
        """
        self.__base_url = value

    def register_service(self, service):
        """
        Add the service to the global list of services to be instantiated into
        each newly created session

        :param object-type service: an uninstantiated object what is derived
            from :obj:`StackInABoxService`. When a session is created then it
            will be instantiated and added to the StackInABox Service.
        """
        logger.debug(
            'Adding service'
        )
        self.services.append(service)

    def create_session(self, session_id=None):
        """
        Create a new session and return its uuid

        :param text_type session_id: optional session id to create, if not
            provided then one will be created.

        :returns: text_type with the session id
        """
        global global_sessions

        logger.debug(
            'Requesting creation of session. Optional Session Id: {0}'.format(
                session_id
            )
        )
        if session_id is None:
            logger.debug(
                'Creating new session id'
            )
            session_id = str(uuid.uuid4())

        logger.debug(
            'Session id: {0}'.format(
                session_id
            )
        )

        if session_id not in global_sessions:
            logger.debug(
                'Creating new session for session id {0}'.format(
                    session_id
                )
            )
            global_sessions[session_id] = Session(
                session_id,
                self.services
            )

        return session_id

    def reset_session(self, session_id):
        """
        Recreate the session so it starts from scratch

        :raises: InvalidSessionId if the Session ID is not found
        """
        logger.debug(
            'Resetting Session {0}'.format(
                session_id
            )
        )
        if session_id in global_sessions:
            logger.debug(
                'Removing Session {0}'.format(
                    session_id
                )
            )
            del global_sessions[session_id]
            logger.debug(
                'Re-creating Session {0}'.format(
                    session_id
                )
            )
            self.create_session(session_id=session_id)
            logger.debug(
                'Reset of Session {0} Completed'.format(
                    session_id
                )
            )

        else:
            raise InvalidSessionId('Invalid Session ID')

    def remove_session(self, session_id):
        """
        Remove the session

        :param text_type session_id: session id to remove

        :raises: InvalidSessionId if session id is not found
        """
        global global_sessions

        if session_id in global_sessions:
            del global_sessions[session_id]
        else:
            raise InvalidSessionId('Invalid Session ID')

    def request(self, method, request, uri, headers):
        """
        Override the standard handler in order to redirect to the
        appropriate session.

        :param :obj:`Request` request: object containing the HTTP Request
        :param text_type uri: the URI for the request per StackInABox
        :param dict headers: case insensitive header dictionary

        HTTP Request:
            <METHOD> /stackinabox/<session-id>/...

            Does not provide any support directly on /stackinabox/

        HTTP Response:
            593 - Session-ID was not present in the URI
            594 - Invalid Session-ID

            Other responses are from StackInABox or the session.
        """
        # uri = /<session-id>/url/for/session/handler
        # lookup <session-id> in the global 'global_sessions'
        session_id = self.extract_session_id(uri)
        if session_id is None:
            logger.debug(
                'Failed to locate session id in {0}'.format(
                    uri
                )
            )
            return (593, headers, 'StackInAWSGI - Missing Session')

        logger.debug(
            'Operating with Session Id {0}'.format(
                session_id
            )
        )

        if session_id in global_sessions:
            logger.debug(
                'Located session id {0}'.format(
                    session_id
                )
            )
            session_uri = uri[1:]

            logger.debug(
                'Updated URI from {0} to {1}'.format(
                    uri,
                    session_uri
                )
            )

            # Let the session handle the request
            return global_sessions[session_id].call(
                method,
                request,
                session_uri,
                headers
            )

        else:
            logger.debug(
                'Failed to find a matching session for session id {0}'.format(
                    session_id
                )
            )
            # Report an unknown session
            return (594, headers, 'StackInAWSGI - Unknown Session')
