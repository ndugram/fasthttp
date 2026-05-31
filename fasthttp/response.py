from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

import orjson
from pydantic import BaseModel, ConfigDict, PrivateAttr

try:
    from fasthttp._core import extract_assets  # type: ignore
except ImportError:
    import re
    from urllib.parse import urljoin as _urljoin

    _CSS_RE = re.compile(
        r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    _JS_RE = re.compile(
        r'<script[^>]+src=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )

    def extract_assets(html: str, base_url: str) -> dict:  # type: ignore[misc]
        css = [_urljoin(base_url, m) for m in _CSS_RE.findall(html)]
        js = [_urljoin(base_url, m) for m in _JS_RE.findall(html)]
        return {"css": css, "js": js}


T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """
    HTTP response object.

    Represents an HTTP response returned by the server,
    including status code, raw body text, and response headers.

    Used by FastHTTP to pass response data to route handlers.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    status: int
    """HTTP status code of the response (e.g. 200, 404, 500)."""

    text: str
    """Raw response body as a string."""

    headers: dict[str, Any]
    """HTTP response headers returned by the server."""

    method: str | None = None
    """HTTP method used for the request (GET, POST, PUT, etc.)."""

    req_headers: dict[str, Any] | None = None
    """HTTP headers sent with the request."""

    query: dict[str, Any] | None = None
    """Query parameters encoded into the request URL."""

    _url: str | None = PrivateAttr(default=None)
    _handler_result: Any = PrivateAttr(default=None)
    _req_json: dict[str, Any] | None = PrivateAttr(default=None)
    _req_data: object | None = PrivateAttr(default=None)

    def model_post_init(self, __context: object, /) -> None:
        extra = self.__pydantic_extra__ or {}
        self._req_json = extra.pop("req_json", None)
        self._req_data = extra.pop("req_data", None)

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            status: int,
            text: str,
            headers: dict[str, Any],
            method: str | None = None,
            req_headers: dict[str, Any] | None = None,
            query: dict[str, Any] | None = None,
            req_json: dict[str, Any] | None = None,
            req_data: object | None = None,
        ) -> None:
            super().__init__(
                status=status,
                text=text,
                headers=headers,
                method=method,
                req_headers=req_headers,
                query=query,
                req_json=req_json,
                req_data=req_data,
            )

    def _set_url(self, url: str | None) -> None:
        self._url = url

    @property
    def url(self) -> str | None:
        """URL of the request that produced this response."""
        return self._url

    @property
    def path_params(self) -> dict[str, Any]:
        """Always empty — FastHTTP does not use path parameters."""
        return {}

    def json(self) -> Any:  # noqa: ANN401
        """Parse the response body as JSON."""
        return orjson.loads(self.text)

    def req_json(self) -> dict[str, Any] | None:
        """Return the JSON body that was sent with the request."""
        return self._req_json

    def req_text(self) -> str | None:
        """Return the request body as text."""
        if self._req_json is not None:
            return orjson.dumps(self._req_json).decode()
        if self._req_data is not None:
            return str(self._req_data)
        return None

    def assets(self, *, css: bool = True, js: bool = True) -> dict[str, list[str]]:
        """Extract CSS and JS asset URLs from the response HTML."""
        base_url = self._url or ""
        result = extract_assets(self.text, base_url)
        if not css:
            result["css"] = []
        if not js:
            result["js"] = []
        return result

    def __repr__(self) -> str:
        return f"<Response [{self.status}]>"
