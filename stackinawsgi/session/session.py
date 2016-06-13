"""
Stack-In-A-WSGI Session Module
"""
from __future__ import absolute_import

import logging
from threading import Lock

from stackinabox.stack import StackInABox

from stackinawsgi.exceptions import *


logger = logging.getLogger(__name__)


class Session(object):
    """
    Wrapper for StackInABox to be safely use it in a multi-request
    supported environment.
    """

    def __init__(self, session_id, services):
        """
        Initialize the wrapper

        :ivar str session_id: session-id for the StackInABox instance
        :ivar list services: list of non-instances services
        :ivar Lock lock: Lock for ensuring StackInABox is safely used
        :ivar StackInABox stack: StackInABox instance being managed
        """
        logger.debug(
            'Creating wrapper for session: {0}'.format(session_id)
        )
        if session_id is None:
            raise InvalidSessionId('Session ID cannot be none')

        if services is None:
            raise InvalidServiceList('Services is empty')

        logger.debug(
            'Session {0} has {1} services'.format(
                session_id,
                len(services)
            )
        )

        if len(services) == 0:
            raise NoServicesProvided('No services configured')

        self.session_id = session_id
        self.services = services
        self.lock = Lock()
        self.stack = StackInABox()
        self.stack.base_url = self.session_id
        self.init_services()

    def init_services(self):
        """
        Initialize the StackInABox instance with the services
        """
        for service in self.services:
            svc = service()
            logger.debug(
                'Session {0}: Initializing service {1}'.format(
                    self.session_id,
                    svc.name
                )
            )
            self.stack.register(svc)

    @property
    def base_url(self):
        """
        Pass-thru to the StackInABox instance's base_url property
        """
        logger.debug(
            'Session {0}: Waiting for lock'.format(
                self.session_id
            )
        )
        with self.lock:
            return self.stack.base_url

    @base_url.setter
    def base_url(self, value):
        """
        Pass-thru to the StackInABox instance's base_url property
        """
        logger.debug(
            'Session {0}: Waiting for lock'.format(
                self.session_id
            )
        )
        with self.lock:
            self.stack.base_url = value

    def reset(self):
        """
        Reset the StackInABox instance to the initial state by
        resetting the instance then re-registering all the services.
        """
        logger.debug(
            'Session {0}: Waiting for lock'.format(
                self.session_id
            )
        )
        with self.lock:
            logger.debug(
                'Session {0}: Acquired lock'.format(
                    self.session_id
                )
            )

            self.stack.reset()
            self.init_services()

    def call(self, *args, **kwargs):
        """
        Wrapper to same in the StackInABox instance
        """
        logger.debug(
            'Session {0}: Waiting for lock'.format(
                self.session_id
            )
        )
        with self.lock:
            logger.debug(
                'Session {0}: Acquired lock'.format(
                    self.session_id
                )
            )

            return self.stack.call(*args, **kwargs)

    def try_handle_route(self, *args, **kwargs):
        """
        Wrapper to same in the StackInABox instance
        """
        logger.debug(
            'Session {0}: Waiting for lock'.format(
                self.session_id
            )
        )
        with self.lock:
            logger.debug(
                'Session {0}: Acquired lock'.format(
                    self.session_id
                )
            )

            return self.stack.try_handle_route(*args, **kwargs)

    def request(self, *args, **kwargs):
        """
        Wrapper to same in the StackInABox instance
        """
        logger.debug(
            'Session {0}: Waiting for lock'.format(
                self.session_id
            )
        )
        with self.lock:
            logger.debug(
                'Session {0}: Acquired lock'.format(
                    self.session_id
                )
            )

            return self.stack.request(*args, **kwargs)

    def sub_request(self, *args, **kwargs):
        """
        Pass-thru to the StackInABox instance's sub_request
        """
        logger.debug(
            'Session {0}: Waiting for lock'.format(
                self.session_id
            )
        )
        with self.lock:
            logger.debug(
                'Session {0}: Acquired lock'.format(
                    self.session_id
                )
            )

            return self.stack.sub_request(*args, **kwargs)
