from .commons import TOKEN_PATH

class BaseSpotliException(Exception):
    """Base Spotli Exception
    """

class MissingApiTokenError(BaseSpotliException):
    """When token has not been created
    """

    def __init__(self):
        super().__init__()

    def __str__(self):
        return f"No token available at {TOKEN_PATH}. Request new with 'spotli auth'."

class AuthorizationError(BaseSpotliException):
    """When authorization failed
    """

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Unsuccessful authorization attemp. Please try again."

class MissingRequiredArgumentsError(BaseSpotliException):
    """When required arugments where not passed"""

    def __init__(self, missing_args: list[str]):
        super().__init__()
        self.missing_args = missing_args

    def __str__(self):
        return f"Missing one or more required arguments" \
                + "".join(f"\n- {arg}" for arg in self.missing_args)

class SpotliAPIException(BaseSpotliException):
    """General API call Exception
    """

    def __init__(self, response: dict):
        super().__init__()
        self.status = response['error']['status']
        self.response_message = response['error']['error_description']

    def __str__(self):
        return f"SpotliAPIException[{self.status}] - {self.response_message}"

class BadRequestError(SpotliAPIException):
    """Bad Request - The request could not be understood by the
    server due to malformed syntax.
    """
    def __init__(self, status: str, response_message: str):
        super().__init__(status, response_message)
        self.message = "Bad Request"

    def __str__(self):
        return f"{self.message}; " + super().__str__()


class UnauthorizedError(SpotliAPIException):
    """Unauthorized - The request requires user authentication or,
    if the request included authorization credentials,
    authorization has been refused for those credentials.
    """
    def __init__(self, response: dict):
        super().__init__(response)
        self.message = "Unauthorized"

    def __str__(self):
        return f"{self.message}; " + super().__str__()

class ForbiddenError(SpotliAPIException):
    """Forbidden - The server understood the request,
    but is refusing to fulfill it.
    """
    def __init__(self, response: dict):
        super().__init__(response)
        self.message = "Forbidden"

    def __str__(self):
        return f"{self.message}; " + super().__str__()

class NotFoundError(SpotliAPIException):
    """Not Found - The requested resource could not be found.
    This error can be due to a temporary or permanent condition.
    """
    def __init__(self, response: dict):
        super().__init__(response)
        self.message = "Not Found"

    def __str__(self):
        return f"{self.message}; " + super().__str__()

class RateLimitError(SpotliAPIException):
    """Too Many Requests - Rate limiting has been applied.
    """
    def __init__(self, response: dict):
        super().__init__(response)
        self.message = "Too Many Requests"

    def __str__(self):
        return f"{self.message}; " + super().__str__()

class InternalServerError(SpotliAPIException):
    """Container for all Internal Server Errors
    """
    def __init__(self, response: dict):
        super().__init__(response)
        self.message = "Internal Server Error"

    def __str__(self):
        return f"{self.message}; " + super().__str__()
