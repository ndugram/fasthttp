import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fasthttp.client import HTTPClient
from fasthttp.response import Response
from fasthttp.routing import Route
from fasthttp.middleware import MiddlewareManager as MM


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
    async def test_send_get_request_success(self, http_client, mock_httpx_client) -> None:
        """Test successful GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_response.headers = {"Content-Type": "text/plain"}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        async def handler(response):
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
    async def test_send_post_request_with_json(self, http_client, mock_httpx_client) -> None:
        """Test POST request with JSON body."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.text = '{"created": true}'
        mock_response.headers = {"Content-Type": "application/json"}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        async def handler(response):
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
    async def test_send_request_adds_user_agent(self, http_client, mock_httpx_client) -> None:
        """Test that User-Agent header is added automatically."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        async def handler(response):
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
        assert headers["User-Agent"] == "fasthttp/0.1.16"

    @pytest.mark.asyncio
    async def test_send_request_handles_4xx_status(self, http_client, mock_httpx_client) -> None:
        """Test handling of 4xx status codes."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        async def handler(response):
            return response

        route = Route(
            method="GET",
            url="http://example.com/notfound",
            handler=handler,
        )

        result = await http_client.send(mock_httpx_client, route)

        assert result is None

    @pytest.mark.asyncio
    async def test_send_request_handles_connection_error(self, http_client, mock_httpx_client) -> None:
        """Test handling of connection errors."""
        import httpx

        mock_httpx_client.request = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))

        async def handler(response):
            return response

        route = Route(
            method="GET",
            url="http://example.com/",
            handler=handler,
        )

        result = await http_client.send(mock_httpx_client, route)

        assert result is None

    @pytest.mark.asyncio
    async def test_send_request_handles_timeout(self, http_client, mock_httpx_client) -> None:
        """Test handling of timeout errors."""
        import httpx

        mock_httpx_client.request = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        async def handler(response):
            return response

        route = Route(
            method="GET",
            url="http://example.com/slow",
            handler=handler,
        )

        result = await http_client.send(mock_httpx_client, route)

        assert result is None

    @pytest.mark.asyncio
    async def test_send_request_with_query_params(self, http_client, mock_httpx_client) -> None:
        """Test request with query parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        async def handler(response):
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
    async def test_send_request_with_custom_timeout(self, http_client, mock_httpx_client) -> None:
        """Test request with custom timeout configuration."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        http_client.request_configs["GET"]["timeout"] = 60.0

        async def handler(response):
            return response

        route = Route(
            method="GET",
            url="http://example.com/",
            handler=handler,
        )

        await http_client.send(mock_httpx_client, route)

    @pytest.mark.asyncio
    async def test_send_handler_result_string(self, http_client, mock_httpx_client) -> None:
        """Test that handler returning string updates response text."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "original"
        mock_response.headers = {}

        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        async def handler(response):
            return "modified"

        route = Route(
            method="GET",
            url="http://example.com/",
            handler=handler,
        )

        result = await http_client.send(mock_httpx_client, route)

        assert result.text == "modified"

    @pytest.mark.asyncio
    async def test_send_handler_result_response(self, http_client, mock_httpx_client) -> None:
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

        async def handler(response):
            return custom_response

        route = Route(
            method="GET",
            url="http://example.com/",
            handler=handler,
        )

        result = await http_client.send(mock_httpx_client, route)

        assert result == custom_response
        assert result.status == 201
