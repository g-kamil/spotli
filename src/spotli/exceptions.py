

class SpotliBaseException(Exception):
    """"""

class AuthorizationError(SpotliBaseException):
    """"""

class MissingRequiredArgumentsError(SpotliBaseException):
    """"""

class MissingApiTokenError(SpotliBaseException):
    """"""