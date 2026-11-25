from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from .types import OAuth2Scope


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
        self._httpx_auth: httpx.DigestAuth | None = None

    def build_httpx_auth(self) -> httpx.Auth:
        """Return the httpx auth adapter for this configuration.

        Reused across requests so the server's challenge is remembered and
        later requests are sent authorized without a new 401 round trip.
        """
        if self._httpx_auth is None:
            self._httpx_auth = httpx.DigestAuth(self.username, self.password)
        return self._httpx_auth


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
        scopes: list[OAuth2Scope] | None = None,
        extra: dict[str, str] | None = None,
    ) -> None:
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.extra = extra or {}
        self._httpx_auth: _HttpxOAuth2Auth | None = None

    def build_httpx_auth(self) -> httpx.Auth:
        """Return the httpx auth adapter for this configuration.

        The adapter is built once and then reused. It owns the access token,
        so a new adapter per request would fetch a new token every time
        instead of caching it until it is close to expiring.
        """
        if self._httpx_auth is None:
            self._httpx_auth = _HttpxOAuth2Auth(self)
        return self._httpx_auth


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
        # Serializes token requests so parallel first requests fetch one token.
        self._lock = asyncio.Lock()

    def _fresh_token(self) -> str | None:
        if self._access_token and time.monotonic() < self._expires_at:
            return self._access_token
        return None

    def _token_form(self) -> dict[str, str]:
        data: dict[str, str] = {
            "grant_type": "client_credentials",
            "client_id": self._config.client_id,
            "client_secret": self._config.client_secret,
        }
        if self._config.scopes:
            data["scope"] = " ".join(self._config.scopes)
        data.update(self._config.extra)
        return data

    def _store_token(self, resp: httpx.Response) -> str:
        resp.raise_for_status()
        body = resp.json()

        self._access_token = body["access_token"]
        expires_in = body.get("expires_in", 3600)
        self._expires_at = time.monotonic() + expires_in - 60

        return self._access_token

    def _ensure_token(self) -> str:
        token = self._fresh_token()
        if token:
            return token

        # A short-lived client per token request: the token endpoint is hit
        # rarely, and this avoids holding a client that is never closed.
        with httpx.Client() as client:
            resp = client.post(
                self._config.token_url,
                data=self._token_form(),
                headers={"Accept": "application/json"},
            )
        return self._store_token(resp)

    async def _aensure_token(self) -> str:
        token = self._fresh_token()
        if token:
            return token

        async with self._lock:
            # Another request may have fetched the token while we waited.
            token = self._fresh_token()
            if token:
                return token
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self._config.token_url,
                    data=self._token_form(),
                    headers={"Accept": "application/json"},
                )
            return self._store_token(resp)

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self._ensure_token()}"
        yield request

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        request.headers["Authorization"] = f"Bearer {await self._aensure_token()}"
        yield request


def resolve_auth(
    auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None,
) -> httpx.Auth | None:
    """Convert a fasthttp auth object to an httpx-compatible auth."""
    if isinstance(auth, BasicAuth):
        return httpx.BasicAuth(auth.username, auth.password)
    if isinstance(auth, DigestAuth):
        return auth.build_httpx_auth()
    if isinstance(auth, BearerAuth):
        return _HttpxBearerAuth(auth.token)
    if isinstance(auth, OAuth2ClientCredentials):
        return auth.build_httpx_auth()
    return None
