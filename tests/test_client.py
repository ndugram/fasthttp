import asyncio
from contextlib import AbstractContextManager
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from fasthttp.__meta__ import __version__
from fasthttp.auth import DigestAuth, OAuth2ClientCredentials
from fasthttp.client import HTTPClient
from fasthttp.events import EventHooks
from fasthttp.exceptions import FastHTTPBadStatusError
from fasthttp.middleware import MiddlewareManager as MM  # noqa: N817
from fasthttp.response import Response
from fasthttp.routing import Route


class TestHTTPClient:
    """Tests for the HTTPClient class."""

    def test_client_creation(self, mock_logger, request_configs) -> None:
        """Test that HTTPClient can be created."""
        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
        )

        assert client.request_configs == request_configs
        assert client.logger == mock_logger
        assert client.middleware_manager is None

    def test_client_with_middleware_manager(self, mock_logger, request_configs) -> None:
        """Test HTTPClient creation with middleware manager."""
        mm = MM()
        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
            middleware_manager=mm,
        )

        assert client.middleware_manager is mm

    @pytest.mark.asyncio
    async def test_send_get_request_success(
        self, http_client, mock_httpx_client
    ) -> None:
        """Test successful GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_response.headers = {"Content-Type": "text/plain"}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        async def handler(response) -> Response:
            return response

        route = Route(
            method="GET",
            url="http://example.com/",
            handler=handler,
        )

        result = await http_client.send(mock_httpx_client, route)

        assert result is not None
        assert result.status == 200
        assert result.text == "Success"

    @pytest.mark.asyncio
    async def test_send_post_request_with_json(
        self, http_client, mock_httpx_client
    ) -> None:
        """Test POST request with JSON body."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.text = '{"created": true}'
        mock_response.headers = {"Content-Type": "application/json"}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        async def handler(response) -> Response:
            return response

        route = Route(
            method="POST",
            url="http://example.com/api",
            handler=handler,
            json={"name": "test"},
        )

        result = await http_client.send(mock_httpx_client, route)

        assert result is not None
        assert result.status == 201

    @pytest.mark.asyncio
    async def test_send_request_adds_user_agent(
        self, http_client, mock_httpx_client
    ) -> None:
        """Test that User-Agent header is added automatically."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        async def handler(response) -> Response:
            return response

        route = Route(
            method="GET",
            url="http://example.com/",
            handler=handler,
        )

        await http_client.send(mock_httpx_client, route)

        call_kwargs = mock_httpx_client.request.call_args.kwargs
        headers = call_kwargs.get("headers", {})
        assert "User-Agent" in headers
        assert headers["User-Agent"] == f"fasthttp/{__version__}"

    @pytest.mark.asyncio
    async def test_send_request_handles_4xx_status(
        self, http_client, mock_httpx_client
    ) -> None:
        """Test handling of 4xx status codes."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        async def handler(response) -> Response:
            return response

        route = Route(
            method="GET",
            url="http://example.com/notfound",
            handler=handler,
        )

        result = await http_client.send(mock_httpx_client, route)

        assert result is None

    @pytest.mark.asyncio
    async def test_send_request_handles_connection_error(
        self, http_client, mock_httpx_client
    ) -> None:
        """Test handling of connection errors."""
        import httpx

        mock_httpx_client.request = AsyncMock(
            side_effect=httpx.ConnectError("Connection failed")
        )

        async def handler(response) -> Response:
            return response

        route = Route(
            method="GET",
            url="http://example.com/",
            handler=handler,
        )

        result = await http_client.send(mock_httpx_client, route)

        assert result is None

    @pytest.mark.asyncio
    async def test_send_request_handles_timeout(
        self, http_client, mock_httpx_client
    ) -> None:
        """Test handling of timeout errors."""
        import httpx

        mock_httpx_client.request = AsyncMock(
            side_effect=httpx.TimeoutException("Timeout")
        )

        async def handler(response) -> Response:
            return response

        route = Route(
            method="GET",
            url="http://example.com/slow",
            handler=handler,
        )

        result = await http_client.send(mock_httpx_client, route)

        assert result is None

    @pytest.mark.asyncio
    async def test_send_request_with_query_params(
        self, http_client, mock_httpx_client
    ) -> None:
        """Test request with query parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        async def handler(response) -> Response:
            return response

        route = Route(
            method="GET",
            url="http://example.com/search",
            handler=handler,
            params={"q": "test", "page": "1"},
        )

        await http_client.send(mock_httpx_client, route)

        call_kwargs = mock_httpx_client.request.call_args.kwargs
        assert call_kwargs.get("params") == {"q": "test", "page": "1"}

    @pytest.mark.asyncio
    async def test_send_request_with_custom_timeout(
        self, http_client, mock_httpx_client
    ) -> None:
        """Test request with custom timeout configuration."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        http_client.request_configs["GET"]["timeout"] = 60.0

        async def handler(response) -> Response:
            return response

        route = Route(
            method="GET",
            url="http://example.com/",
            handler=handler,
        )

        await http_client.send(mock_httpx_client, route)

    @pytest.mark.asyncio
    async def test_send_handler_result_string(
        self, http_client, mock_httpx_client
    ) -> None:
        """Test that handler returning string updates response text."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "original"
        mock_response.headers = {}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        async def handler(_response) -> str:
            return "modified"

        route = Route(
            method="GET",
            url="http://example.com/",
            handler=handler,
        )

        result = await http_client.send(mock_httpx_client, route)

        assert result.text == "modified"

    @pytest.mark.asyncio
    async def test_send_handler_result_response(
        self, http_client, mock_httpx_client
    ) -> None:
        """Test that handler returning Response returns that Response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "original"
        mock_response.headers = {}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        custom_response = Response(
            status=201,
            text="custom response",
            headers={"X-Custom": "true"},
        )

        async def handler(_response) -> Response:
            return custom_response

        route = Route(
            method="GET",
            url="http://example.com/",
            handler=handler,
        )

        result = await http_client.send(mock_httpx_client, route)

        assert result == custom_response
        assert result.status == 201

    @pytest.mark.asyncio
    async def test_raise_for_status_false_returns_none_on_4xx(
        self, mock_logger, request_configs, mock_httpx_client
    ) -> None:
        """Test that raise_for_status=False (default) returns None on 4xx."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {}
        mock_response.content = b"Not Found"

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
            raise_for_status=False,
        )

        async def handler(response) -> Response:
            return response

        route = Route(method="GET", url="http://example.com/notfound", handler=handler)

        result = await client.send(mock_httpx_client, route)

        assert result is None

    @pytest.mark.asyncio
    async def test_raise_for_status_true_raises_on_4xx(
        self, mock_logger, request_configs, mock_httpx_client
    ) -> None:
        """Test that raise_for_status=True raises FastHTTPBadStatusError on 4xx."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {}
        mock_response.content = b"Not Found"

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
            raise_for_status=True,
        )

        async def handler(response) -> Response:
            return response

        route = Route(method="GET", url="http://example.com/notfound", handler=handler)

        with pytest.raises(FastHTTPBadStatusError) as exc_info:
            await client.send(mock_httpx_client, route)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_raise_for_status_true_raises_on_5xx(
        self, mock_logger, request_configs, mock_httpx_client
    ) -> None:
        """Test that raise_for_status=True raises FastHTTPBadStatusError on 5xx."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.headers = {}
        mock_response.content = b"Internal Server Error"

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
            raise_for_status=True,
        )

        async def handler(response) -> Response:
            return response

        route = Route(method="GET", url="http://example.com/error", handler=handler)

        with pytest.raises(FastHTTPBadStatusError) as exc_info:
            await client.send(mock_httpx_client, route)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_raise_for_status_true_no_raise_on_2xx(
        self, mock_logger, request_configs, mock_httpx_client
    ) -> None:
        """Test that raise_for_status=True does NOT raise on 2xx."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"ok": true}'
        mock_response.headers = {}
        mock_response.content = b'{"ok": true}'

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
            raise_for_status=True,
        )

        async def handler(response) -> Response:
            return response

        route = Route(method="GET", url="http://example.com/ok", handler=handler)

        result = await client.send(mock_httpx_client, route)

        assert result is not None
        assert result.status == 200

    @pytest.mark.asyncio
    async def test_route_raise_for_status_raises_when_global_false(
        self, mock_logger, request_configs, mock_httpx_client
    ) -> None:
        """Test that route-level raise_for_status=True raises even when global is False."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {}
        mock_response.content = b"Not Found"

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
            raise_for_status=False,
        )

        async def handler(response) -> Response:
            return response

        route = Route(
            method="GET",
            url="http://example.com/notfound",
            handler=handler,
            raise_for_status=True,
        )

        with pytest.raises(FastHTTPBadStatusError) as exc_info:
            await client.send(mock_httpx_client, route)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_route_raise_for_status_global_true_route_false_still_raises(
        self, mock_logger, request_configs, mock_httpx_client
    ) -> None:
        """Test that global raise_for_status=True raises even when route flag is False."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = "Unprocessable Entity"
        mock_response.headers = {}
        mock_response.content = b"Unprocessable Entity"

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
            raise_for_status=True,
        )

        async def handler(response) -> Response:
            return response

        route = Route(
            method="GET",
            url="http://example.com/validate",
            handler=handler,
            raise_for_status=False,
        )

        with pytest.raises(FastHTTPBadStatusError) as exc_info:
            await client.send(mock_httpx_client, route)

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_route_raise_for_status_both_false_returns_none(
        self, mock_logger, request_configs, mock_httpx_client
    ) -> None:
        """Test that both global and route raise_for_status=False returns None on 4xx."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_response.headers = {}
        mock_response.content = b"Forbidden"

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
            raise_for_status=False,
        )

        async def handler(response) -> Response:
            return response

        route = Route(
            method="GET",
            url="http://example.com/forbidden",
            handler=handler,
            raise_for_status=False,
        )

        result = await client.send(mock_httpx_client, route)

        assert result is None


class TestExceptionHandler:
    """Tests for the exception_handler dispatch in HTTPClient.send()."""

    @pytest.mark.asyncio
    async def test_handler_result_replaces_default_none_on_generic_exception(
        self, mock_logger, request_configs, mock_httpx_client
    ) -> None:
        """A registered handler's return value replaces the usual None result."""
        mock_httpx_client.request = AsyncMock(
            side_effect=httpx.ConnectError("Connection failed")
        )

        event_hooks = EventHooks()

        @event_hooks.exception_handler(exc_type=httpx.ConnectError)
        async def handle_connect_error(route, exc):
            return {"error": str(exc), "url": route.url}

        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
            event_hooks=event_hooks,
        )

        async def handler(response) -> Response:
            return response

        route = Route(method="GET", url="http://example.com/", handler=handler)

        result = await client.send(mock_httpx_client, route)

        assert result is not None
        assert result._handler_result == {
            "error": "Connection failed",
            "url": "http://example.com/",
        }

    @pytest.mark.asyncio
    async def test_handler_replaces_bad_status_error_when_raise_for_status(
        self, mock_logger, request_configs, mock_httpx_client
    ) -> None:
        """A handler for FastHTTPBadStatusError intercepts it instead of raising."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.headers = {}
        mock_response.content = b"Internal Server Error"

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        event_hooks = EventHooks()

        @event_hooks.exception_handler(exc_type=FastHTTPBadStatusError)
        async def handle_bad_status(route, exc):
            return {"status": exc.status_code}

        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
            raise_for_status=True,
            event_hooks=event_hooks,
        )

        async def handler(response) -> Response:
            return response

        route = Route(method="GET", url="http://example.com/error", handler=handler)

        result = await client.send(mock_httpx_client, route)

        assert result is not None
        assert result._handler_result == {"status": 500}

    @pytest.mark.asyncio
    async def test_most_specific_handler_wins_via_mro(
        self, mock_logger, request_configs, mock_httpx_client
    ) -> None:
        """When both a base and a specific handler are registered, the specific one wins."""
        mock_httpx_client.request = AsyncMock(side_effect=httpx.ConnectError("boom"))

        event_hooks = EventHooks()

        @event_hooks.exception_handler(exc_type=Exception)
        async def generic(route, exc):
            return "generic"

        @event_hooks.exception_handler(exc_type=httpx.ConnectError)
        async def specific(route, exc):
            return "specific"

        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
            event_hooks=event_hooks,
        )

        async def handler(response) -> Response:
            return response

        route = Route(method="GET", url="http://example.com/", handler=handler)

        result = await client.send(mock_httpx_client, route)

        assert result is not None
        assert result._handler_result == "specific"

    @pytest.mark.asyncio
    async def test_unhandled_exception_type_still_returns_none(
        self, mock_logger, request_configs, mock_httpx_client
    ) -> None:
        """No matching handler falls back to prior behavior (None)."""
        mock_httpx_client.request = AsyncMock(
            side_effect=httpx.TimeoutException("slow")
        )

        event_hooks = EventHooks()

        @event_hooks.exception_handler(exc_type=httpx.ConnectError)
        async def handle_connect_error(route, exc):
            return "should not be called"

        client = HTTPClient(
            request_configs=request_configs,
            logger=mock_logger,
            event_hooks=event_hooks,
        )

        async def handler(response) -> Response:
            return response

        route = Route(method="GET", url="http://example.com/", handler=handler)

        result = await client.send(mock_httpx_client, route)

        assert result is None


class TestOAuth2ClientCredentials:
    """Tests for the OAuth2 client-credentials auth flow."""

    @staticmethod
    def _mock_response(json_body: dict, status_code: int = 200) -> httpx.Response:
        """Build a mock response that carries an elapsed time.

        httpx only sets ``Response.elapsed`` once the response stream is
        closed, which never happens for ``MockTransport`` responses.
        """
        response = httpx.Response(status_code, json=json_body)
        response.elapsed = timedelta(seconds=0.01)
        return response

    @staticmethod
    def _auth() -> OAuth2ClientCredentials:
        return OAuth2ClientCredentials(
            token_url="https://auth.example.com/oauth/token",  # noqa: S106
            client_id="client-id",
            client_secret="client-secret",  # noqa: S106
        )

    @staticmethod
    def _route(auth: OAuth2ClientCredentials) -> Route:
        async def handler(response) -> Response:
            return response

        return Route(
            method="GET",
            url="https://api.example.com/protected",
            handler=handler,
            auth=auth,
        )

    @staticmethod
    def _token_client_patch(
        token_transport: httpx.MockTransport,
    ) -> AbstractContextManager[object]:
        """Route the adapter's own token-endpoint client to a mock transport.

        The API client is created before patching, so only the token
        request (which builds a fresh ``httpx.AsyncClient``) is affected.
        """
        original_client = httpx.AsyncClient

        def client_factory(**_kwargs: object) -> httpx.AsyncClient:
            return original_client(transport=token_transport)

        return patch.object(httpx, "AsyncClient", client_factory)

    @pytest.mark.asyncio
    async def test_access_token_is_cached_between_requests(self, mock_logger) -> None:
        """The token endpoint is queried once and the token is reused."""
        token_requests: list[httpx.Request] = []
        api_requests: list[httpx.Request] = []

        def token_handler(request: httpx.Request) -> httpx.Response:
            token_requests.append(request)
            return self._mock_response(
                {"access_token": "access-token-1", "expires_in": 3600}
            )

        def api_handler(request: httpx.Request) -> httpx.Response:
            api_requests.append(request)
            return self._mock_response({"ok": True})

        client = HTTPClient(
            request_configs={"GET": {"headers": {}, "timeout": 30.0}},
            logger=mock_logger,
        )
        route = self._route(self._auth())

        api_client = httpx.AsyncClient(transport=httpx.MockTransport(api_handler))
        with self._token_client_patch(httpx.MockTransport(token_handler)):
            async with api_client:
                for _ in range(3):
                    result = await client.send(api_client, route)

                    assert result is not None
                    assert result.status == 200

        assert len(api_requests) == 3
        assert len(token_requests) == 1
        assert all(
            request.headers["authorization"] == "Bearer access-token-1"
            for request in api_requests
        )

    @pytest.mark.asyncio
    async def test_expired_access_token_is_refetched(self, mock_logger) -> None:
        """A token that is already expired is fetched again for every request."""
        token_requests: list[httpx.Request] = []

        def token_handler(request: httpx.Request) -> httpx.Response:
            token_requests.append(request)
            return self._mock_response(
                {"access_token": "access-token-1", "expires_in": 0}
            )

        def api_handler(request: httpx.Request) -> httpx.Response:
            return self._mock_response({"ok": True})

        client = HTTPClient(
            request_configs={"GET": {"headers": {}, "timeout": 30.0}},
            logger=mock_logger,
        )
        route = self._route(self._auth())

        api_client = httpx.AsyncClient(transport=httpx.MockTransport(api_handler))
        with self._token_client_patch(httpx.MockTransport(token_handler)):
            async with api_client:
                for _ in range(2):
                    result = await client.send(api_client, route)

                    assert result is not None
                    assert result.status == 200

        assert len(token_requests) == 2

    @pytest.mark.asyncio
    async def test_concurrent_first_requests_fetch_token_once(
        self, mock_logger
    ) -> None:
        """Parallel requests with an empty cache share a single token fetch."""
        token_requests: list[httpx.Request] = []

        async def token_handler(request: httpx.Request) -> httpx.Response:
            token_requests.append(request)
            # Yield to the event loop so the other requests reach the adapter
            # while this token request is still in flight.
            await asyncio.sleep(0.01)
            return self._mock_response(
                {"access_token": "access-token-1", "expires_in": 3600}
            )

        def api_handler(request: httpx.Request) -> httpx.Response:
            return self._mock_response({"ok": True})

        client = HTTPClient(
            request_configs={"GET": {"headers": {}, "timeout": 30.0}},
            logger=mock_logger,
        )
        route = self._route(self._auth())

        api_client = httpx.AsyncClient(transport=httpx.MockTransport(api_handler))
        with self._token_client_patch(httpx.MockTransport(token_handler)):
            async with api_client:
                results = await asyncio.gather(
                    *(client.send(api_client, route) for _ in range(5))
                )

        assert all(result is not None and result.status == 200 for result in results)
        assert len(token_requests) == 1

    @pytest.mark.asyncio
    async def test_token_is_refetched_only_after_refresh_margin(
        self, mock_logger, monkeypatch
    ) -> None:
        """A token is reused until ``expires_in - 60`` seconds have passed."""
        clock = [1000.0]
        monkeypatch.setattr(
            "fasthttp.auth.time", SimpleNamespace(monotonic=lambda: clock[0])
        )
        token_requests: list[httpx.Request] = []

        def token_handler(request: httpx.Request) -> httpx.Response:
            token_requests.append(request)
            return self._mock_response(
                {
                    "access_token": f"access-token-{len(token_requests)}",
                    "expires_in": 120,
                }
            )

        def api_handler(request: httpx.Request) -> httpx.Response:
            return self._mock_response({"ok": True})

        client = HTTPClient(
            request_configs={"GET": {"headers": {}, "timeout": 30.0}},
            logger=mock_logger,
        )
        route = self._route(self._auth())

        api_client = httpx.AsyncClient(transport=httpx.MockTransport(api_handler))
        with self._token_client_patch(httpx.MockTransport(token_handler)):
            async with api_client:
                await client.send(api_client, route)  # t=0: fetch
                clock[0] += 59
                await client.send(api_client, route)  # t=59: still cached
                assert len(token_requests) == 1

                clock[0] += 2
                await client.send(api_client, route)  # t=61: inside margin
                assert len(token_requests) == 2

    def test_building_auth_does_not_create_http_client(self) -> None:
        """Creating the adapter must not open an HTTP client that is never closed."""
        with (
            patch.object(httpx, "Client", side_effect=AssertionError),
            patch.object(httpx, "AsyncClient", side_effect=AssertionError),
        ):
            auth = self._auth()
            assert auth.build_httpx_auth() is auth.build_httpx_auth()


class TestDigestAuth:
    """Tests for the HTTP Digest auth flow."""

    @pytest.mark.asyncio
    async def test_digest_challenge_is_reused_across_requests(
        self, mock_logger
    ) -> None:
        """Only the first request needs the 401 challenge round trip."""
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.headers.get("authorization", "").startswith("Digest "):
                response = httpx.Response(200, json={"ok": True})
            else:
                response = httpx.Response(
                    401,
                    headers={
                        "WWW-Authenticate": (
                            'Digest realm="api", nonce="abc123", qop="auth", '
                            "algorithm=MD5"
                        )
                    },
                )
            response.elapsed = timedelta(seconds=0.01)
            return response

        client = HTTPClient(
            request_configs={"GET": {"headers": {}, "timeout": 30.0}},
            logger=mock_logger,
        )

        async def handler_route(response) -> Response:
            return response

        route = Route(
            method="GET",
            url="https://api.example.com/protected",
            handler=handler_route,
            auth=DigestAuth("user", "pass"),
        )

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as api:
            for _ in range(3):
                result = await client.send(api, route)

                assert result is not None
                assert result.status == 200

        # 1 challenge (401) + 3 authorized requests; a new DigestAuth per
        # request would repeat the challenge every time (6 requests).
        assert len(requests) == 4
