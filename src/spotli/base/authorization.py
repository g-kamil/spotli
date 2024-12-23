import json
from base64 import b64encode
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import NoReturn
from urllib.parse import parse_qs, urlencode, urlparse

import click
import requests

from .models import TOKEN_PATH
from .exceptions import AuthorizationError, MissingRequiredArgumentsError

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPES = [
    "user-read-private",
    "user-read-email",
    "user-read-playback-state",
    "user-read-recently-played",
]


class SpotifyAuth:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def _check_arguments(self):
        arg_dict = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }

        missing_args = [k for k, v in arg_dict.items() if not v]

        if missing_args:
            raise MissingRequiredArgumentsError(missing_args=missing_args)

    def _save_tokens(self, tokens: dict) -> NoReturn:
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)

        # add expires_at
        tokens["expires_at"] = (
            datetime.now() + timedelta(seconds=tokens["expires_in"])
        ).strftime("%Y-%m-%dT%H:%M:%S")

        with open(TOKEN_PATH, "w") as f:
            json.dump(tokens, f)

    def _load_tokens(self) -> dict | None:
        if TOKEN_PATH.exists():
            with open(TOKEN_PATH, "r") as f:
                return json.load(f)
        return None

    def _request_access_token(self, code: dict) -> dict:
        auth_header = b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        headers = {"Authorization": f"Basic {auth_header}"}
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        response = requests.post(TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    def _refresh_access_token(self, refresh_token: str) -> dict:
        auth_header = b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        headers = {"Authorization": f"Basic {auth_header}"}
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        response = requests.post(TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    def get_access_token(self) -> dict:
        click.echo("Checking for token existance...")
        tokens = self._load_tokens()
        if tokens:
            click.echo("Token already exists, checking if need for refresh... ")
            # Refresh token if expired
            expires_at = datetime.strptime(
                tokens.get("expires_at"), "%Y-%m-%dT%H:%M:%S"
            )

            if expires_at < datetime.now():
                self._check_arguments()
                new_tokens = self._refresh_access_token(tokens["refresh_token"])
                tokens.update(new_tokens)
                self._save_tokens(tokens)
                click.secho("Token refreshed", fg="green")
            else:
                click.secho("No need of creating new token", blink=True, fg="green")

            return tokens["access_token"]

        click.echo("Token doesn't exist, requesting new one")
        self._check_arguments()
        # Start new authorization flow
        return self._start_authorization_flow()

    def _start_authorization_flow(self) -> dict:
        auth_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(SCOPES),
        }
        auth_url = f"{AUTH_URL}?{urlencode(auth_params)}"
        click.echo(f"Open this URL in your browser to authorize the app:\n{auth_url}")

        # Start a simple HTTP server to handle the callback
        class CallbackHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                """skip sending server log messages"""
                return

            def do_GET(self):
                parsed_url = urlparse(self.path)
                query = parse_qs(parsed_url.query)
                self.server.code = query.get("code", [None])[0]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"<script>window.close()</script>")

        port = urlparse(self.redirect_uri).port

        server = HTTPServer(("localhost", port), CallbackHandler)
        server.handle_request()
        code = server.code

        if not code:
            raise AuthorizationError()

        tokens = self._request_access_token(code)
        self._save_tokens(tokens)
        click.echo(f"Access Token created at: {TOKEN_PATH}")

        return tokens["access_token"]


@click.command(context_settings={"auto_envvar_prefix": "SPOTLI"})
@click.option("--redirect_uri", help="Overwrites SPOTLI_REDIRECT_URI", type=str)
@click.option("--client_secret", help="Overwrites SPOTLI_CLIENT_SECRET", type=str)
@click.option("--client_id", help="Overwrites SPOTLI_CLIENT_ID", type=str)
def auth(client_id, client_secret, redirect_uri):
    """Authenticate user using oAuth and create access token\n
    prerequisition: Spotify App\n
    (see: https://developer.spotify.com/documentation/web-api/concepts/apps)

    You can pass your credentials to the the command directly or more convieniently
    store them in environment variables
    """
    try:
        SpotifyAuth(client_id, client_secret, redirect_uri).get_access_token()
    except KeyboardInterrupt:
        raise click.Abort()
    except MissingRequiredArgumentsError as err:
        click.echo("Missing required user credentials")
        for cred in err.missing_args:
            click.secho(f" - {cred}", fg="red")
    except Exception as err:
        raise err
