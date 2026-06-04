from unittest.mock import AsyncMock, MagicMock

import pytest

from fasthttp.__meta__ import __version__
from fasthttp.client import HTTPClient
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
