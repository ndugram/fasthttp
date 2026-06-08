from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from annotated_doc import Doc

from .base import BaseMiddleware

try:
    from fasthttp._core import (
        build_cookie_header as _rs_build_cookie_header,  # type: ignore
    )
    from fasthttp._core import (
        parse_set_cookie_header as _rs_parse_set_cookie,  # type: ignore
    )

    _HAVE_RUST_COOKIE = True
except ImportError:
    _HAVE_RUST_COOKIE = False

if TYPE_CHECKING:
    from collections.abc import Iterator

    from fasthttp.response import Response


class CookieJar:
    """
    Cookie storage for FastHTTP.

    Holds cookies that are injected into every outgoing request
    and updated from ``Set-Cookie`` headers in responses.

    Pass to :class:`FastHTTP` via the ``cookie_jar`` parameter.

    Example:
    ```python
        from fasthttp import FastHTTP, CookieJar

        app = FastHTTP(cookie_jar=CookieJar())

        app = FastHTTP(cookie_jar=CookieJar({"session_id": "abc"}))

        app = FastHTTP(cookie_jar=CookieJar(unsafe=True))
    ```
    """

    def __init__(
        self,
        cookies: Annotated[
            dict[str, str] | None,
            Doc("Initial cookies to pre-seed the jar with."),
        ] = None,
        *,
        unsafe: Annotated[
            bool,
            Doc(
                """
                Allow cookies for IP addresses and localhost.

                By default, cookies for non-domain hosts are rejected.
                Set to ``True`` to allow them — useful for local development
                and testing against internal services.
                """
            ),
        ] = False,
    ) -> None:
        self._cookies: dict[str, str] = dict(cookies) if cookies else {}
        self.unsafe = unsafe

    def set(
        self,
        name: Annotated[str, Doc("Cookie name.")],
        value: Annotated[str, Doc("Cookie value.")],
    ) -> None:
        self._cookies[name] = value

    def get(
        self,
        name: Annotated[str, Doc("Cookie name.")],
        default: Annotated[
            str | None, Doc("Fallback value if cookie not found.")
        ] = None,
    ) -> str | None:
        return self._cookies.get(name, default)

    def clear(self) -> None:
        self._cookies.clear()

    def items(self) -> list[tuple[str, str]]:
        return list(self._cookies.items())

    def __iter__(self) -> Iterator[tuple[str, str]]:
        return iter(self._cookies.items())

    def __len__(self) -> int:
        return len(self._cookies)

    def __repr__(self) -> str:
        return f"<CookieJar cookies={list(self._cookies.keys())} unsafe={self.unsafe}>"


class DummyCookieJar(CookieJar):
    """
    No-op cookie jar that discards all cookies.

    Use when you want to explicitly disable cookie handling
    without removing ``cookie_jar`` from the constructor call.

    Example:
    ```python
        from fasthttp import FastHTTP, DummyCookieJar

        app = FastHTTP(cookie_jar=DummyCookieJar())
    ```
    """

    def set(self, name: str, value: str) -> None:  # noqa: ARG002
        return

    def __repr__(self) -> str:
        return "<DummyCookieJar>"


class SessionMiddleware(BaseMiddleware):
    """
    Middleware for persisting cookies across requests and ``app.run()`` calls.

    Captures ``Set-Cookie`` headers from responses and injects them as
    ``Cookie`` headers into subsequent requests. State survives between
    separate ``app.run()`` calls as long as the same instance is used.

    Example:
        ```python
            from fasthttp import FastHTTP
            from fasthttp.middleware import SessionMiddleware

            session = SessionMiddleware()
            app = FastHTTP(middleware=session)

            # or chain with other middleware
            app = FastHTTP(middleware=session | CacheMiddleware())

            @app.post("https://example.com/login", json={"user": "x", "pass": "y"})
            async def login(resp: Response) -> dict:
                return resp.json()

            @app.get("https://example.com/profile")
            async def profile(resp: Response) -> dict:
                return resp.json()

            app.run(tags=["auth"])
            app.run(tags=["protected"])
        ```
    """

    __priority__ = -10

    def __init__(
        self,
        cookies: Annotated[
            dict[str, str] | None,
            Doc("Pre-seed cookies to inject from the first request. Optional."),
        ] = None,
        *,
        jar: Annotated[
            CookieJar | None,
            Doc(
                "CookieJar instance to use as backing store. Takes priority over cookies."
            ),
        ] = None,
    ) -> None:
        self._jar: CookieJar = jar if jar is not None else CookieJar(cookies)

    @property
    def cookies(self) -> dict[str, str]:
        return self._jar._cookies  # noqa: SLF001

    def __repr__(self) -> str:
        return f"<SessionMiddleware cookies={list(self._jar._cookies.keys())}>"  # noqa: SLF001

    async def request(
        self,
        method: Annotated[str, Doc("HTTP method.")],  # noqa: ARG002
        url: Annotated[str, Doc("Request URL.")],  # noqa: ARG002
        kwargs: Annotated[dict[str, Any], Doc("Request kwargs passed to httpx.")],
    ) -> dict[str, Any]:
        if self._jar._cookies:  # noqa: SLF001
            headers = dict(kwargs.get("headers") or {})
            if _HAVE_RUST_COOKIE:
                headers["Cookie"] = _rs_build_cookie_header(self._jar._cookies)  # type: ignore[possibly-unbound] # noqa: SLF001
            else:
                headers["Cookie"] = "; ".join(
                    f"{k}={v}"
                    for k, v in self._jar._cookies.items()  # noqa: SLF001
                )
            kwargs["headers"] = headers
        return kwargs

    async def response(
        self,
        response: Annotated[Response, Doc("Wrapped response object.")],
    ) -> Response:
        raw = response.headers.get("set-cookie", "")
        if raw:
            if _HAVE_RUST_COOKIE:
                for k, v in _rs_parse_set_cookie(raw).items():
                    self._jar.set(k, v)
            else:
                for cookie_str in raw.split(","):
                    name_value = cookie_str.split(";")[0].strip()
                    if "=" in name_value:
                        k, v = name_value.split("=", 1)
                        self._jar.set(k.strip(), v.strip())
        return response

    def clear(self) -> None:
        self._jar.clear()

    def get_cookies(self) -> dict[str, str]:
        return dict(self._jar._cookies)  # noqa: SLF001
