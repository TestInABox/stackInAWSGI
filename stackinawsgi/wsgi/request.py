"""
Stack-In-A-WSGI Request Model
"""
import logging

import six

if six.PY2:
    from urllib import quote
else:
    from urllib.parse import quote


logger = logging.getLogger(__name__)


class Request(object):
    """
    The Request Object Model for the StackInAWSGI Framework

    Note: This needs to look like a :obj:`requests.Request`
    """

    @staticmethod
    def get_path(env_path):
        """
        Normalizes the provided path value across Py2 and Py3 environments

        :param text_type env_path: the URI Path value to normalize
        :returns: the normalized path

        Note: Compliments of the Falcon WSGI framework
        """
        # Compliments for falcon...normalize the path
        path = env_path
        if path:
            # According to PEP3333
            if six.PY3:
                path = path.encode('latin1').decode('utf-8', 'replace')

            if len(path) > 1 and path.endswith('/'):
                path = path[:-1]

        else:
            path = '/'

        return path

    def __init__(self, environment):
        """
        Create the Request Model object

        :param dict environment: the dictionary of WSGI/HTTP data describing
            the environment of the WSGI/HTTP Request
        """
        self.environment = environment
        self.stream = self.environment['wsgi.input']
        self.method = self.environment['REQUEST_METHOD']
        self.path = self.get_path(self.environment['PATH_INFO'])
        if 'QUERY_STRING' in self.environment:
            self.query = self.environment['QUERY_STRING']
        else:
            self.query = None

        self.headers = {}
        # build out the headers
        for k, v in self.environment.items():
            env_key = k.upper()
            if env_key.startswith('HTTP_'):
                header_key = k[len('HTTP_'):]
                self.headers[header_key] = v
                logger.debug(
                    'Headers[{0} -> {1}] = {2} -> {3}'.format(
                        k,
                        header_key,
                        v,
                        self.headers[header_key]
                    )
                )

    @property
    def url(self):
        """
        The complete URL of the Request, f.e http://localhost/...
        """
        env = self.environment
        # rebuild the URI, algorithm complements of PEP-3333
        url = env['wsgi.url_scheme'] + '://'

        if env.get('HTTP_HOST'):
            url += env['HTTP_HOST']
        else:
            url += env['SERVER_NAME']

            if env['wsgi.url_scheme'] == 'https':
                if env['SERVER_PORT'] != '443':
                    url += ':' + env['SERVER_PORT']
            else:
                if env['SERVER_PORT'] != '80':
                    url += ':' + env['SERVER_PORT']

        url += quote(env.get('SCRIPT_NAME', ''))
        url += quote(env.get('PATH_INFO', ''))
        if env.get('QUERY_STRING'):
            url += '?' + env['QUERY_STRING']

        return url
