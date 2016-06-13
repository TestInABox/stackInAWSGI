"""
Stack-In-A-WSGI: stackinawsgi.exceptions
"""


class InvalidSessionId(ValueError):
    pass


class InvalidServiceList(TypeError):
    pass


class NoServicesProvided(ValueError):
    pass
