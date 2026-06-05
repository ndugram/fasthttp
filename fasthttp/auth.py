from __future__ import annotations

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


class _HttpxBearerAuth(httpx.Auth):
    def __init__(self, token: str) -> None:
        self._token = token

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request


def resolve_auth(
    auth: BasicAuth | DigestAuth | BearerAuth | None,
) -> httpx.Auth | None:
    """Convert a fasthttp auth object to an httpx-compatible auth."""
    if isinstance(auth, BasicAuth):
        return httpx.BasicAuth(auth.username, auth.password)
    if isinstance(auth, DigestAuth):
        return httpx.DigestAuth(auth.username, auth.password)
    if isinstance(auth, BearerAuth):
        return _HttpxBearerAuth(auth.token)
    return None
