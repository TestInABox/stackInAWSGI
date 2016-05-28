"""
Stack-In-A-WSGI Application
"""
from __future__ import absolute_import

import logging

from .request import Request
from .response import Response

from stackinabox.services.service import StackInABoxService
from stackinabox.stack import StackInABox


logger = logging.getLogger(__name__)


class App(object):
    """
    A WSGI Application for running StackInABox under a WSGI host
    """

    def __init__(self, services=[]):
        """
        Create the WSGI Application

        :param list services: list of :obj:`StackInABoxService`s to load into
            StackInABox.
        """
        self.stackinabox = StackInABox()

        # for each StackInABox Service in the configuration,
        # register with StackInABox
        for service in services:
            if isinstance(service, StackInABoxService):
                self.RegisterWithStackInABox(service)
            else:
                raise TypeError(
                    "Service is not a Stack-In-A-Box Service"
                )

    def RegisterWithStackInABox(self, service):
        """
        Add a :obj:`StackInABoxService` to the StackInABox instance

        :param :obj:`StackInABoxService` service: the service to register with
            StackInABox
        """
        self.stackinabox.register(service)

    def ResetStackInABox(self):
        """
        Reset StackInABox to its default state
        """
        self.stackinabox.reset()

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
        result = self.stackinabox.call(
            request.method,
            request,
            request.url,
            response.headers
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
