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

    # List of well-known status codes
    status_values = {
        # Official Status Codes
        100: "Continue",
        101: "Switching Protocols",
        102: "Processing",
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        207: "Multi-Status Response",
        208: "Already Reported",
        226: "IM Used",
        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        305: "Use Proxy",
        306: "Switch Proxy",
        307: "Temporary Redirect",
        308: "Permanent Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Timeout",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Payload Too Large",
        414: "URI Too Long",
        415: "Unsupported Media Type",
        416: "Range Not Satisfiable",
        417: "Expectation Failed",
        418: "I'm a teapot",
        421: "Misdirected Request",
        422: "Unprocessable Entity",
        423: "Locked",
        424: "Failed Dependency",
        426: "Upgrade Required",
        428: "Precondition Required",
        429: "Too Many Requests",
        431: "Requested Header Fields Too Large",
        451: "Unavailable for Legal Reasons",
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
        505: "HTTP Version Not Supported",
        506: "Variant Also Negotiates",
        507: "Insufficient Storage",
        508: "Loop Detected",
        510: "Not Extended",
        511: "Network Authentication Required",

        # Unofficial Status Codes:
        103: "Checkpoint",
        420: "Method Failure",
        450: "Blocked by Windows Parental Control (MS)",
        498: "Invalid Token",
        499: "Token Required",
        509: "Bandwidth Limit Exceeded",
        530: "Site Frozen",
        440: "Login Timeout",
        449: "Retry With",
        # 451 - Redirect (re-defined)

        444: "No Response",
        495: "SSL Certificate Error",
        496: "SSL Certificate Required",
        497: "HTTP Request Sent to HTTPS Port",
        499: "Client Closed Request",

        520: "Unknown Error",
        521: "Web Server Is Down",
        522: "Connection Timed Out",
        523: "Origin Is Unreachable",
        524: "A Timeout Occurred",
        525: "SSL Handshake Failed",
        526: "Invalid SSL Certificate",

        # The below codes are specific cases for the infrastructure
        # supported here and should not conflict with anything above.

        # StackInABox Status Codes
        595: "Route Not Handled",
        596: "Unhandled Exception",
        597: "URI Is For Service That Is Unknown",

        # StackInAWSGI Status Codes
        593: "Session ID Missing from URI",
        594: "Invalid Session ID"
    }

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
        self.admin_service.base_uri = uri

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

    def response_for_status(cls, status):
        """
        Generate a status string for the status code

        :param int status: the status code to look-up
        :returns: string for the value or an appropriate Unknown value
        """
        if status in cls.status_values:
            return cls.status_values[status]

        elif status >= 100 and status < 200:
            return "Unknown Informational Status"

        elif status >= 200 and status < 300:
            return "Unknown Success Status"

        elif status >= 300 and status < 400:
            return "Unknown Redirection Status"

        elif status >= 400 and status < 500:
            return "Unknown Client Error"

        elif status >= 500 and status < 600:
            return "Unknown Server Error"

        else:
            return "Unknown Status"

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
            "{0} {1}".format(
                response.status,
                self.response_for_status(
                    response.status
                )
            ),
            [(k, v) for k, v in response.headers.items()]
        )
        yield response.body
