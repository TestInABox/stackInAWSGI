"""
Stack-In-A-WSGI: stackinawsgi.exceptions
"""


class InvalidSessionId(ValueError):
    """
    Invalid Session ID as provided
    """
    pass


class InvalidServiceList(TypeError):
    """
    Service List has invalid entries
    """
    pass


class NoServicesProvided(ValueError):
    """
    Services were not provided
    """
    pass
