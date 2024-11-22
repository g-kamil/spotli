from .commons import TOKEN_PATH

class BaseSpotliException(Exception):
    """Base Spotli Exception"""

class SpotliAPIException(BaseSpotliException):
    """API call Exception"""

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status

    def __str__(self):
        return f"SpotliBaseException[{self.status}] - {self.message}"

class AuthorizationError(BaseSpotliException):
    """Unsuccessful Authorization"""

    def __str__(self):
        return "Authorization Error, please authorize yourself with 'spotli auth'."

class MissingRequiredArgumentsError(BaseSpotliException):
    """Missing on of the required arguments"""

    def __init__(self, missing_args: list[str]):
        super().__init__()
        self.missing_args = missing_args

    def __str__(self):
        return f"Missing required arguments:" \
               "".join(f"\n - {arg}" for arg in self.missing_args)


class MissingApiTokenError(SpotliBaseException):
    """API token not available"""

    def __str__(self):
        return f"API token not available under {TOKEN_PATH}"