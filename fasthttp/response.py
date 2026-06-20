from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Annotated, Any, get_args, get_origin

import orjson
from annotated_doc import Doc

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
