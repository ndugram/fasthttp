from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING, Annotated, Any, get_args, get_origin

import orjson
from annotated_doc import Doc

from .exceptions import FastHTTPBadStatusError

if TYPE_CHECKING:
    import datetime

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


class Response:
    """
    HTTP response object.

    Represents an HTTP response returned by the server,
    including status code, raw body text, and response headers.

    Used by FastHTTP to pass response data to route handlers.
    """

    def __init__(
        self,
        status: Annotated[int, Doc("HTTP status code (e.g. 200, 404, 500).")],
        text: Annotated[str, Doc("Raw response body as a string.")],
        headers: Annotated[dict[str, str], Doc("HTTP response headers returned by the server.")],
        method: Annotated[str | None, Doc("HTTP method used for the request.")] = None,
        req_headers: Annotated[dict[str, str] | None, Doc("HTTP headers sent with the request.")] = None,
        query: Annotated[dict[str, Any] | None, Doc("Query parameters encoded into the request URL.")] = None,
        req_json: Annotated[dict[str, Any] | None, Doc("JSON body sent with the request.")] = None,
        req_data: Annotated[object | None, Doc("Raw body or form data sent with the request.")] = None,
        content: Annotated[bytes | None, Doc("Raw response body as bytes.")] = None,
        *,
        history: Annotated[list[Response] | None, Doc("List of intermediate responses from redirects.")] = None,
        elapsed: Annotated[datetime.timedelta | None, Doc("Time taken for the request.")] = None,
        http_version: Annotated[str | None, Doc("HTTP version used (e.g. HTTP/1.1, HTTP/2).")] = None,
        reason_phrase: Annotated[str | None, Doc("Reason phrase (e.g. OK, Not Found).")] = None,
    ) -> None:
        self.status = status
        self.text = text
        self.headers = headers
        self._handler_result: Any = None
        self._response_model: type | None = None
        self._method = method
        self._req_headers = req_headers
        self._query = query
        self._req_json = req_json
        self._req_data = req_data
        self._url: str | None = None
        self._content: bytes | None = content
        self._history: list[Response] = history or []
        self._elapsed = elapsed
        self._http_version = http_version
        self._reason_phrase = reason_phrase

    def _set_url(self, url: str | None) -> None:
        self._url = url

    @property
    def url(self) -> str | None:
        """URL of the request that produced this response."""
        return self._url

    @property
    def method(self) -> str | None:
        """HTTP method used for the request (GET, POST, PUT, etc.)."""
        return self._method

    @method.setter
    def method(self, value: str | None) -> None:
        self._method = value

    @property
    def req_headers(self) -> dict[str, str] | None:
        """HTTP headers sent with the request."""
        return self._req_headers

    @req_headers.setter
    def req_headers(self, value: dict[str, str] | None) -> None:
        self._req_headers = value

    @property
    def query(self) -> dict[str, Any] | None:
        """Query parameters encoded into the request URL."""
        return self._query

    @query.setter
    def query(self, value: dict[str, Any] | None) -> None:
        self._query = value

    @property
    def path_params(self) -> dict[str, Any]:
        """Always empty — FastHTTP does not use path parameters."""
        return {}

    @property
    def history(self) -> list[Response]:
        """List of intermediate responses from redirects (if any)."""
        return self._history

    @property
    def elapsed(self) -> datetime.timedelta | None:
        """Time taken for the request."""
        return self._elapsed

    @property
    def http_version(self) -> str | None:
        """HTTP version used (e.g. ``HTTP/1.1``, ``HTTP/2``)."""
        return self._http_version

    @property
    def reason_phrase(self) -> str | None:
        """Reason phrase (e.g. ``OK``, ``Not Found``)."""
        return self._reason_phrase

    @property
    def is_success(self) -> bool:
        """``True`` if status code is 2xx (200-299)."""
        return 200 <= self.status < 300

    @property
    def is_redirect(self) -> bool:
        """``True`` if status code is 3xx (300-399)."""
        return 300 <= self.status < 400

    @property
    def is_error(self) -> bool:
        """``True`` if status code is 4xx or 5xx (400-599)."""
        return 400 <= self.status < 600

    @property
    def is_client_error(self) -> bool:
        """``True`` if status code is 4xx (400-499)."""
        return 400 <= self.status < 500

    @property
    def is_server_error(self) -> bool:
        """``True`` if status code is 5xx (500-599)."""
        return 500 <= self.status < 600

    @property
    def is_informational(self) -> bool:
        """``True`` if status code is 1xx (100-199)."""
        return 100 <= self.status < 200

    def raise_for_status(self) -> None:
        """Raise :class:`FastHTTPBadStatusError` if status code is 4xx or 5xx."""
        if self.is_error:
            raise FastHTTPBadStatusError(
                message=f"HTTP {self.status}",
                url=self._url,
                method=self._method,
                status_code=self.status,
                response_body=self.text,
            )

    def json(self) -> Any:  # noqa: ANN401
        """Parse the response body as JSON, validating against response_model if set."""
        if self._response_model is not None:
            if get_origin(self._response_model) is list:
                item_model = get_args(self._response_model)[0]
                return [item_model.model_validate(item) for item in orjson.loads(self.text)]
            return self._response_model.model_validate_json(self.text)  # type: ignore[union-attr]
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

    def bytes(self) -> bytes:
        """Return raw response body as bytes."""
        if self._content is not None:
            return self._content
        return self.text.encode()

    def html(self) -> str:
        """Return response body as HTML string.

        Raises ValueError if Content-Type is not HTML.
        """
        content_type = self.headers.get("content-type", "")
        if content_type and "html" not in content_type.lower():
            msg = f"Expected HTML response, got Content-Type: {content_type}"
            raise ValueError(msg)
        return self.text

    def xml(self) -> ET.Element:
        """Parse response body as XML and return root Element.

        Only use with trusted sources — stdlib XML parser is vulnerable to
        entity expansion attacks (XXE). For untrusted data, use defusedxml.

        Raises xml.etree.ElementTree.ParseError on invalid XML.
        """
        return ET.fromstring(self.text)  # noqa: S314

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
