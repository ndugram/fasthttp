from __future__ import annotations

import time
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from collections.abc import Generator


class BasicAuth:
    """HTTP Basic authentication (username + password)."""

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password


class DigestAuth:
    """HTTP Digest authentication (username + password)."""

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password


class BearerAuth:
    """HTTP Bearer token authentication."""

    def __init__(self, token: str) -> None:
        self.token = token


class OAuth2ClientCredentials:
    """
    OAuth2 Client Credentials flow with automatic token refresh.

    Acquires an access token from the token endpoint on first use
    and automatically refreshes it before expiry.

    Usage:
        auth = OAuth2ClientCredentials(
            token_url="https://auth.example.com/oauth/token",
            client_id="my-client",
            client_secret="my-secret",
            scopes=["read", "write"],
        )
    """

    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        scopes: list[str] | None = None,
        extra: dict[str, str] | None = None,
    ) -> None:
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.extra = extra or {}


class _HttpxBearerAuth(httpx.Auth):
    def __init__(self, token: str) -> None:
        self._token = token

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request


class _HttpxOAuth2Auth(httpx.Auth):
    """
    httpx-compatible auth that handles the OAuth2 Client Credentials flow.

    Fetches a token on first request and automatically refreshes
    before the current token expires.
    """

    def __init__(self, config: OAuth2ClientCredentials) -> None:
        self._config = config
        self._access_token: str | None = None
        self._expires_at: float = 0.0
        self._client = httpx.Client()

    def _ensure_token(self) -> str:
        if self._access_token and time.monotonic() < self._expires_at:
            return self._access_token

        data: dict[str, str] = {
            "grant_type": "client_credentials",
            "client_id": self._config.client_id,
            "client_secret": self._config.client_secret,
        }
        if self._config.scopes:
            data["scope"] = " ".join(self._config.scopes)
        data.update(self._config.extra)

        resp = self._client.post(
            self._config.token_url,
            data=data,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        body = resp.json()

        self._access_token = body["access_token"]
        expires_in = body.get("expires_in", 3600)
        self._expires_at = time.monotonic() + expires_in - 60

        return self._access_token

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self._ensure_token()}"
        yield request


def resolve_auth(
    auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None,
) -> httpx.Auth | None:
    """Convert a fasthttp auth object to an httpx-compatible auth."""
    if isinstance(auth, BasicAuth):
        return httpx.BasicAuth(auth.username, auth.password)
    if isinstance(auth, DigestAuth):
        return httpx.DigestAuth(auth.username, auth.password)
    if isinstance(auth, BearerAuth):
        return _HttpxBearerAuth(auth.token)
    if isinstance(auth, OAuth2ClientCredentials):
        return _HttpxOAuth2Auth(auth)
    return None
