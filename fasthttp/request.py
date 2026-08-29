from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Annotated, Any

import httpx
from annotated_doc import Doc

from fasthttp.helpers.curl import build_curl_command

if TYPE_CHECKING:
    from .app import FastHTTP
    from .routing import Route


class Request:
    """
    Outgoing HTTP request passed to ``@app.middleware("http")`` handlers.

    Unlike an ASGI server request, the body of an outgoing request is
    already fully built before any middleware runs — there is nothing to
    stream. ``.json`` / ``.content`` / ``.query_params`` are therefore
    read-only snapshots of what ``route`` will send; only ``.headers``
    is mutable and actually reaches the request that gets sent.

    Example:
        ```python
        @app.middleware("http")
        async def add_trace_id(request: Request, call_next):
            request.headers["X-Trace-Id"] = str(uuid.uuid4())
            response = await call_next(request)
            return response
        ```
    """

    __slots__ = ("_url", "app", "headers", "method", "route", "state")

    def __init__(
        self,
        method: Annotated[str, Doc("HTTP method of the request being sent.")],
        url: Annotated[str, Doc("Resolved target URL.")],
        route: Annotated[Route, Doc("The Route being executed.")],
        app: Annotated[FastHTTP, Doc("The FastHTTP application instance.")],
        headers: Annotated[
            dict[str, str],
            Doc("Mutable headers dict — changes are sent with the request."),
        ],
    ) -> None:
        self.method = method
        self._url = url
        self.route = route
        self.app = app
        self.state = SimpleNamespace()
        self.headers = headers

    @property
    def url(self) -> httpx.URL:
        """Structured URL — gives ``.host``, ``.port``, ``.scheme``, ``.path``, ``.params``."""
        return httpx.URL(self._url)

    @property
    def host(self) -> str | None:
        """Shortcut for ``request.url.host``."""
        return self.url.host

    @property
    def query_params(self) -> dict[str, Any]:
        """Read-only snapshot of the query parameters that will be sent."""
        return self.route.params or {}

    @property
    def json(self) -> dict[str, Any] | None:
        """Read-only snapshot of the JSON body that will be sent, if any."""
        return self.route.json

    @property
    def content(self) -> Any:  # noqa: ANN401
        """Read-only snapshot of the raw body/form data that will be sent, if any."""
        return self.route.data

    def to_curl(self, *, reveal_secrets: bool = False) -> str:
        """
        Build the ``curl`` command equivalent to this outgoing request.

        Sensitive headers (``Authorization``, cookies, API keys) and known
        sensitive query params are masked by default — pass
        ``reveal_secrets=True`` to get a command you can actually run yourself.
        """

        return build_curl_command(
            self.method,
            self._url,
            self.headers,
            self.json,
            self.content,
            reveal_secrets=reveal_secrets,
        )

    def __repr__(self) -> str:
        return f"<Request {self.method} {self._url}>"
