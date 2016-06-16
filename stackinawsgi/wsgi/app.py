"""
Stack-In-A-WSGI Application
"""
from __future__ import absolute_import

import logging
from collections import Iterable

from .request import Request
from .response import Response

from stackinawsgi.session.service import StackInAWsgiSessionManager
from stackinawsgi.admin.admin import StackInAWsgiAdmin

from stackinabox.services.service import StackInABoxService
from stackinabox.stack import StackInABox


logger = logging.getLogger(__name__)


class App(object):
    """
    A WSGI Application for running StackInABox under a WSGI host
    """

    def __init__(self, services=None):
        """
        Create the WSGI Application

        :param list services: list of :obj:`StackInABoxService`s to load into
            StackInABox.
        """
        self.stackinabox = StackInABox()
        self.stack_service = StackInAWsgiSessionManager()
        self.admin_service = StackInAWsgiAdmin(
            self.stack_service,
            'http://localhost/stackinabox/'
        )
        self.stackinabox.register(self.admin_service)
        self.stackinabox.register(self.stack_service)

        def __check_service(service_object):
            """
            Simple wrapper to check whether an object provide by the caller is
            a StackInABoxService by creating an instance
            """
            svc = service_object()
            if not isinstance(svc, StackInABoxService):
                raise TypeError(
                    "Service is not a Stack-In-A-Box Service"
                )

        # if the caller does not provide any services then just log it
        # to keep from user confusion
        if services is not None:

            # Allow the caller to provide either an iterable of services to
            # to provide to the session or to provide a single service object
            if isinstance(services, Iterable):
                # for each service verify it is a StackInABoxService
                for service in services:
                    __check_service(service)
                    self.RegisterWithStackInABox(service)

            else:
                # if it's not an iterable - e.g a single object - then
                # just check the variable itself
                __check_service(services)
                self.RegisterWithStackInABox(services)

        else:
            logger.debug(
                "No services registered on initialization"
            )

    def RegisterWithStackInABox(self, service):
        """
        Add a :obj:`StackInABoxService` to the StackInABox instance

        :param :obj:`StackInABoxService` service: the service to register with
            StackInABox
        """
        self.stack_service.register_service(service)

    def ResetStackInABox(self, session_uuid):
        """
        Reset StackInABox to its default state
        """
        self.stack_service.reset_session(session_uuid)

    def StackInABoxHoldOnto(self, name, obj):
        """
        Add something into the StackInABox KV store

        :param text_type name: name of the value for the KV store
        :param any obj: a value to associate in the KV store
        """
        self.stackinabox.into_hold(name, obj)

    def StackInABoxHoldOut(self, name):
        """
        Retrieve a value from the KV store

        :param text_type name: name of the value for the KV store
        :returns: the value if the KV store associated with the given name
        """
        return self.stackinabox.from_hold(name)

    def StackInABoxUriUpdate(self, uri):
        """
        Update StackInABox to use a new URI value.
        """
        self.stackinabox.base_url = uri

    def CallStackInABox(self, request, response):
        """
        Call into StackInABox with the given request and response objects.

        :param :obj:`Request` request: the :obj:`Request` object to use for
            as input
        :param :obj:`Response` response: the :obj:`Response` object to use
            for the output
        """
        # Parse the URL and determine where it's going
        # /stackinabox/<session>/<service>/<normal user path>
        # /admin for StackInAWSGI administrative functionality
        result = self.stackinabox.call(
            request.method,
            request,
            request.url,
            request.headers
        )
        response.from_stackinabox(
            result[0],
            result[1],
            result[2]
        )

    def __call__(self, environ, start_response):
        """
        Callable entry per the PEP-3333 WSGI spec

        :param dict environ: the environment dictionary from the WSGI stack
        :param callable start_response: the start_response callable for the
            WSGI stack
        :returns: generator for the response body
        """
        logger.debug('Instance ID: {0}'.format(id(self)))
        logger.debug('Environment: {0}'.format(environ))
        request = Request(environ)
        response = Response()
        self.CallStackInABox(request, response)
        start_response(
            str(response.status),
            [(k, v) for k, v in response.headers.items()]
        )
        yield response.body
