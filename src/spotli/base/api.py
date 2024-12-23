import requests
import json

from .models import TOKEN_PATH
from .exceptions import (
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    InternalServerError,
    SpotliAPIException,
    MissingApiTokenError,
)


class SpotifyAPI:
    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self):
        self.access_token = self._load_tokens()
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _load_tokens(self) -> str | None:
        if TOKEN_PATH.exists():
            with open(TOKEN_PATH, "r") as f:
                return json.load(f).get("access_token")
        raise MissingApiTokenError()

    def _request(
        self, method: str, endpoint: str, params: dict = None, data: dict = None
    ) -> dict | None:
        """Basic request to the API"""

        url = f"{self.BASE_URL}/{endpoint}"

        response = requests.request(
            method,
            url,
            headers=self.headers,
            params=params,
            data=json.dumps(data) if data else None,
        )

        match response.status_code:
            case 200:
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError:
                    return response.content
            case 201 | 202 | 204:
                return None
            case 400:
                raise BadRequestError(response.json())
            case 401:
                raise UnauthorizedError(response.json())
            case 403:
                raise ForbiddenError(response.json())
            case 404:
                raise NotFoundError(response.json())
            case 429:
                raise RateLimitError(response.json())
            case 500 | 502 | 503:
                raise InternalServerError(response.json())
            case _:
                raise SpotliAPIException(response.json())

    def get(self, endpoint: str, data: dict = None, params: dict = None) -> dict | None:
        """GET request to specified endpoint with given params"""
        return self._request("GET", endpoint, data=data, params=params)

    def post(self, endpoint: str, data: dict = None, params: dict = None) -> dict | None:
        """POST request to specified endpoint with given params"""
        return self._request("POST", endpoint, data=data, params=params)

    def put(self, endpoint: str, data: dict = None, params: dict = None) -> dict | None:
        """PUT request to specified endpoint with given params"""
        return self._request("PUT", endpoint, data=data, params=params)

    def delete(self, endpoint: str, data: dict = None, params: dict = None) -> dict | None:
        """DELETE request to specified endpoint with given params"""
        return self._request("DELETE", endpoint, data=data, params=params)
