"""
Stack-In-A-WSGI Response Module
"""


from stackinabox.util.tools import CaseInsensitiveDict


class Response(object):
    """
    The Response Object Model for the StackInAWSGI Framework
    """

    def __init__(self):
        """
        Create the Response Model Object
        """
        self.headers = CaseInsensitiveDict()
        self.status = 500
        self._body = b'Internal Server Error'

    def from_stackinabox(self, status, headers, body):
        """
        Build the Response Model based on the return values from StackInABox

        :param integer status: the HTTP Status Code for the Response Message
        :param dict headers: the HTTP Headers for the Response Message
        :param generator body: the HTTP Message Body for the Response Message
        """
        self.status = status
        if headers is not self.headers:
            self.headers.update(headers)
        self._body = body

    @property
    def body(self):
        """
        The Response Message Body

        :returns: generator containing the data
        """
        # Note: This needs to act like an iterable or FILE-like object
        return self._body
