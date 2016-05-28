"""
Stack-In-A-WSGI: Test Helpers
"""

import logging
import tempfile

from stackinabox.util.tools import CaseInsensitiveDict


class InvalidService(object):
    """
    Invalid Stack-In-A-Box Service, does not implement StackInABoxService
    """
    pass


class WsgiMock(object):
    """
    StackInAWSGI WSGI Mock for the WSGI start_response() callable

    The WsgiMock object is used is place of the start_response callable
    when running a raw WSGI application for testing.
    """

    def __init__(self):
        """
        Initialize the WsgiMock object
        """
        self.headers = CaseInsensitiveDict()
        self.status = "550 start_response() was not called"
        self.logger = logging.getLogger(__name__)
        self.logger.info('Created WSGI Mock - ID = {0}'.format(id(self)))

    def __call__(self, http_status_code, http_headers):
        """
        start_response callable interface
        """
        self.logger.debug(
            'Received WSGI Callback: Status {0}'.format(
                http_status_code
            )
        )
        self.status = http_status_code
        self.headers.update(http_headers)
        self.logger.debug(
            'Completed saving values'
        )


def make_environment(case, method='HEAD', path=u'/', qs=None, host=None,
                     server_name='localhost', port=80, script_name='',
                     url_scheme='http', headers={},
                     content_type=None, content_length=None,
                     http_protocol='http/1.1'):
    """
    Build a WSGI environment for use in testing
    """
    if url_scheme == 'https' and port == 80:
        port = 443

    environment = {
        'wsgi.version': (1, 0),
        'wsgi.errors': tempfile.NamedTemporaryFile(),
        'wsgi.input': tempfile.NamedTemporaryFile(),
        'wsgi.multithreaded': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': True,
        'wsgi.url_scheme': url_scheme,
        'SERVER_PROTOCOL': http_protocol,
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'SERVER_NAME': server_name,
        'SERVER_PORT': str(port),
        'SCRIPT_NAME': script_name
    }
    case.assertIsNotNone(environment['wsgi.input'])
    case.assertIsNotNone(environment['wsgi.errors'])

    for k, v in headers.items():
        environment['HTTP_' + k] = v

    if host is not None:
        environment['HTTP_HOST'] = host

    if qs is not None:
        environment['QUERY_STRING'] = qs
    if content_type is not None:
        environment['CONTENT_TYPE'] = content_type

    if content_length is not None:
        environment['CONTENT_LENGTH'] = 0

    return environment
