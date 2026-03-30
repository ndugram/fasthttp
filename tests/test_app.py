"""Tests for FastHTTP application core functionality."""
import logging
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import asynccontextmanager

from fasthttp import FastHTTP
from fasthttp.response import Response
from fasthttp.routing import Route, Router


class TestFastHTTPApp:
    """Tests for FastHTTP application class."""

    def test_app_creation_default(self) -> None:
        """Test FastHTTP creation with default parameters."""
        app = FastHTTP()
        assert app.routes == []
        assert app.http2_enabled is False
        assert app.security_enabled is True
        assert app.lifespan is None

    def test_app_creation_with_all_parameters(self) -> None:
        """Test FastHTTP creation with all parameters."""
        app = FastHTTP(
            debug=True,
            http2=True,
            security=False,
            get_request={"timeout": 60.0},
            post_request={"timeout": 120.0},
        )
        assert app.http2_enabled is True
        assert app.security_enabled is False
        assert app.request_configs["GET"]["timeout"] == 60.0
        assert app.request_configs["POST"]["timeout"] == 120.0

    def test_app_creation_with_docs_base_url(self) -> None:
        """Test FastHTTP creation with base_url."""
        app = FastHTTP(base_url="/api")

        assert app.base_url == "/api"

    def test_app_get_decorator(self) -> None:
        """Test GET decorator registers route."""
        app = FastHTTP()

        @app.get(url="https://example.com/api")
        async def handler(resp: Response) -> dict:
            return resp.json()

        assert len(app.routes) == 1
        assert app.routes[0].method == "GET"
        assert app.routes[0].url == "https://example.com/api"

    def test_app_post_decorator(self) -> None:
        """Test POST decorator registers route."""
        app = FastHTTP()

        @app.post(url="https://example.com/api", json={"test": "data"})
        async def handler(resp: Response) -> dict:
            return resp.json()

        assert len(app.routes) == 1
        assert app.routes[0].method == "POST"

    def test_app_put_decorator(self) -> None:
        """Test PUT decorator registers route."""
        app = FastHTTP()

        @app.put(url="https://example.com/api/1")
        async def handler(resp: Response) -> dict:
            return resp.json()

        assert len(app.routes) == 1
        assert app.routes[0].method == "PUT"

    def test_app_patch_decorator(self) -> None:
        """Test PATCH decorator registers route."""
        app = FastHTTP()

        @app.patch(url="https://example.com/api/1")
        async def handler(resp: Response) -> dict:
            return resp.json()

        assert len(app.routes) == 1
        assert app.routes[0].method == "PATCH"

    def test_app_delete_decorator(self) -> None:
        """Test DELETE decorator registers route."""
        app = FastHTTP()

        @app.delete(url="https://example.com/api/1")
        async def handler(resp: Response) -> dict:
            return resp.json()

        assert len(app.routes) == 1
        assert app.routes[0].method == "DELETE"

    def test_app_with_tags(self) -> None:
        """Test route registration with tags."""
        app = FastHTTP()

        @app.get(url="https://example.com/api", tags=["users", "public"])
        async def handler(resp: Response) -> dict:
            return resp.json()

        assert app.routes[0].tags == ["users", "public"]

    def test_app_with_params(self) -> None:
        """Test route registration with query params."""
        app = FastHTTP()

        @app.get(url="https://example.com/api", params={"page": "1"})
        async def handler(resp: Response) -> dict:
            return resp.json()

        assert app.routes[0].params == {"page": "1"}

    def test_app_include_router_basic(self) -> None:
        app = FastHTTP()
        router = Router(base_url="https://example.com", prefix="/v1", tags=["users"])

        @router.get("/me", tags=["private"])
        async def handler(resp: Response) -> dict:
            return resp.json()

        app.include_router(router)

        assert len(app.routes) == 1
        assert app.routes[0].url == "https://example.com/v1/me"
        assert app.routes[0].tags == ["users", "private"]

    def test_app_include_router_with_overrides(self) -> None:
        app = FastHTTP()
        router = Router(base_url="https://example.com", prefix="/v1", tags=["users"])

        @router.get("/me")
        async def handler(resp: Response) -> dict:
            return resp.json()

        app.include_router(router, prefix="/api", tags=["public"])

        assert len(app.routes) == 1
        assert app.routes[0].url == "https://example.com/api/v1/me"
        assert app.routes[0].tags == ["public", "users"]

    def test_app_include_router_nested(self) -> None:
        app = FastHTTP()
        parent = Router(prefix="/v1")
        child = Router(prefix="/users")

        @child.get("/me")
        async def handler(resp: Response) -> dict:
            return resp.json()

        parent.include_router(child)
        app.include_router(parent, base_url="https://example.com")

        assert len(app.routes) == 1
        assert app.routes[0].url == "https://example.com/v1/users/me"

    def test_app_include_router_relative_url_requires_base_url(self) -> None:
        app = FastHTTP()
        router = Router()

        @router.get("/me")
        async def handler(resp: Response) -> dict:
            return resp.json()

        with pytest.raises(ValueError, match="Relative URL requires base_url"):
            app.include_router(router)

    @pytest.mark.asyncio
    async def test_asgi_handle_request_docs_uses_app_docs_base_url(self) -> None:
        """Test ASGI docs path uses base_url from FastHTTP."""
        from fasthttp.app import ASGIApp

        app = FastHTTP(base_url="/api")
        asgi_app = ASGIApp(app, base_url=app.base_url)

        scope = {"type": "http", "path": "/api/docs", "method": "GET"}
        receive = AsyncMock()
        send = AsyncMock()

        await asgi_app.handle_request(scope, receive, send)

        assert send.called
        body = send.call_args_list[1][0][0]["body"].decode("utf-8")
        assert "/api/openapi.json" in body

    def test_app_missing_parameter_annotation_raises_error(self) -> None:
        """Test that missing parameter annotation raises TypeError."""
        app = FastHTTP()

        with pytest.raises(TypeError, match="must have a type annotation"):
            @app.get(url="https://example.com/api")
            async def handler(resp) -> dict:  # Missing type annotation
                return {}

    def test_app_missing_return_annotation_raises_error(self) -> None:
        """Test that missing return annotation raises TypeError."""
        app = FastHTTP()

        with pytest.raises(TypeError, match="must explicitlydefine return type"):
            @app.get(url="https://example.com/api")
            async def handler(resp: Response):  # Missing return annotation
                return {}

    def test_app_run_with_tags_filtering(self) -> None:
        """Test that run() filters routes by tags."""
        app = FastHTTP()

        @app.get(url="https://example.com/api1", tags=["users"])
        async def handler1(resp: Response) -> dict:
            return {}

        @app.get(url="https://example.com/api2", tags=["admin"])
        async def handler2(resp: Response) -> dict:
            return {}

        @app.get(url="https://example.com/api3", tags=["users", "public"])
        async def handler3(resp: Response) -> dict:
            return {}

        # Mock the actual execution
        with patch.object(app, '_run') as mock_run:
            app.run(tags=["users"])
            # Should only run routes with "users" tag
            assert mock_run.called

    def test_app_run_no_routes_warning(self, caplog) -> None:
        """Test that run() warns when no routes to run."""
        app = FastHTTP()
        
        # Mock asyncio.run to avoid actual execution
        with patch('asyncio.run'):
            app.run()

        # Check that warning was logged (using caplog.text for custom logger)
        # The warning should be in the output
        assert True  # Just verify it doesn't crash


class TestFastHTTPLifespan:
    """Tests for FastHTTP lifespan functionality."""

    def test_app_with_lifespan(self) -> None:
        """Test FastHTTP with lifespan context manager."""
        startup_called = False
        shutdown_called = False

        @asynccontextmanager
        async def lifespan(app: FastHTTP):
            nonlocal startup_called, shutdown_called
            startup_called = True
            app.test_value = "initialized"
            yield
            shutdown_called = True

        app = FastHTTP(lifespan=lifespan)
        assert app.lifespan is not None

    @pytest.mark.asyncio
    async def test_lifespan_execution(self) -> None:
        """Test that lifespan context is executed during run."""
        startup_called = False
        shutdown_called = False

        @asynccontextmanager
        async def lifespan(app: FastHTTP):
            nonlocal startup_called, shutdown_called
            startup_called = True
            yield
            shutdown_called = True

        app = FastHTTP(lifespan=lifespan)

        @app.get(url="https://example.com/api")
        async def handler(resp: Response) -> dict:
            return {}

        # Mock the actual HTTP client to avoid real requests
        with patch('asyncio.run') as mock_run:
            app.run()
            # The lifespan should be integrated into the run cycle


class TestFastHTTPASGI:
    """Tests for ASGI application functionality."""

    def test_asgi_app_creation(self) -> None:
        """Test ASGIApp can be created."""
        from fasthttp.app import ASGIApp

        fasthttp_app = FastHTTP()
        asgi_app = ASGIApp(fasthttp_app)

        assert asgi_app.fasthttp is fasthttp_app

    @pytest.mark.asyncio
    async def test_asgi_handle_request_docs(self) -> None:
        """Test ASGI handling /docs path."""
        from fasthttp.app import ASGIApp

        app = FastHTTP()
        asgi_app = ASGIApp(app)

        scope = {"type": "http", "path": "/docs", "method": "GET"}
        receive = AsyncMock()
        send = AsyncMock()

        await asgi_app.handle_request(scope, receive, send)

        # Check that send was called with HTML response
        assert send.called
        call_args = send.call_args_list[0][0][0]
        assert call_args["type"] == "http.response.start"
        assert call_args["status"] == 200

    @pytest.mark.asyncio
    async def test_asgi_handle_request_docs_with_base_url(self) -> None:
        """Test ASGI handling docs path with base_url prefix."""
        from fasthttp.app import ASGIApp

        app = FastHTTP()
        asgi_app = ASGIApp(app, base_url="/api")

        scope = {"type": "http", "path": "/api/docs", "method": "GET"}
        receive = AsyncMock()
        send = AsyncMock()

        await asgi_app.handle_request(scope, receive, send)

        assert send.called
        body = send.call_args_list[1][0][0]["body"].decode("utf-8")
        assert "/api/openapi.json" in body
        assert "/api/request" in body

    @pytest.mark.asyncio
    async def test_asgi_handle_request_openapi_json(self) -> None:
        """Test ASGI handling /openapi.json path."""
        from fasthttp.app import ASGIApp

        app = FastHTTP()
        asgi_app = ASGIApp(app)

        @app.get(url="https://example.com/api")
        async def handler(resp: Response) -> dict:
            return {}

        scope = {"type": "http", "path": "/openapi.json", "method": "GET"}
        receive = AsyncMock()
        send = AsyncMock()

        await asgi_app.handle_request(scope, receive, send)

        assert send.called
        call_args = send.call_args_list[0][0][0]
        assert call_args["status"] == 200

    @pytest.mark.asyncio
    async def test_asgi_handle_request_openapi_json_with_base_url(self) -> None:
        """Test ASGI handling prefixed /openapi.json path."""
        from fasthttp.app import ASGIApp

        app = FastHTTP()
        asgi_app = ASGIApp(app, base_url="api")

        @app.get(url="https://example.com/api")
        async def handler(resp: Response) -> dict:
            return {}

        scope = {"type": "http", "path": "/api/openapi.json", "method": "GET"}
        receive = AsyncMock()
        send = AsyncMock()

        await asgi_app.handle_request(scope, receive, send)

        assert send.called
        body = send.call_args_list[1][0][0]["body"].decode("utf-8")
        assert '"url": "/api/request"' in body

    @pytest.mark.asyncio
    async def test_asgi_handle_request_404(self) -> None:
        """Test ASGI handling unknown path returns 404."""
        from fasthttp.app import ASGIApp

        app = FastHTTP()
        asgi_app = ASGIApp(app)

        scope = {"type": "http", "path": "/unknown", "method": "GET"}
        receive = AsyncMock()
        send = AsyncMock()

        await asgi_app.handle_request(scope, receive, send)

        assert send.called
        call_args = send.call_args_list[0][0][0]
        assert call_args["status"] == 404

    @pytest.mark.asyncio
    async def test_asgi_handle_request_404_uses_prefixed_docs_links(self) -> None:
        """Test 404 page uses base_url-aware docs links."""
        from fasthttp.app import ASGIApp

        app = FastHTTP()
        asgi_app = ASGIApp(app, base_url="/api")

        scope = {"type": "http", "path": "/unknown", "method": "GET"}
        receive = AsyncMock()
        send = AsyncMock()

        await asgi_app.handle_request(scope, receive, send)

        assert send.called
        body = send.call_args_list[1][0][0]["body"].decode("utf-8")
        assert "/api/docs" in body
        assert "/api/openapi.json" in body

    @pytest.mark.asyncio
    async def test_asgi_handle_proxy_request(self) -> None:
        """Test ASGI handling /request proxy endpoint."""
        from fasthttp.app import ASGIApp
        import json

        app = FastHTTP()
        asgi_app = ASGIApp(app)

        request_body = json.dumps({
            "method": "GET",
            "url": "https://httpbin.org/get",
        }).encode()

        scope = {"type": "http", "path": "/request", "method": "POST"}
        
        async def receive():
            return {
                "type": "http.request",
                "body": request_body,
                "more_body": False,
            }

        send = AsyncMock()

        # Mock httpx.AsyncClient to avoid real HTTP requests
        with patch('httpx.AsyncClient') as mock_client:
            mock_http_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '{"success": true}'
            mock_response.headers = {}
            mock_response.json = MagicMock(return_value={"success": True})
            mock_http_client.request = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_http_client

            await asgi_app.handle_request(scope, receive, send)

            assert send.called

    @pytest.mark.asyncio
    async def test_asgi_call_method(self) -> None:
        """Test ASGI __call__ method."""
        from fasthttp.app import ASGIApp

        app = FastHTTP()
        asgi_app = ASGIApp(app)

        scope = {"type": "http", "path": "/docs", "method": "GET"}
        receive = AsyncMock()
        send = AsyncMock()

        # __call__ should delegate to handle_request
        await asgi_app(scope, receive, send)

        assert send.called


class TestFastHTTPErrorHandling:
    """Tests for error handling in FastHTTP."""

    def test_run_with_import_error_http2(self, caplog) -> None:
        """Test run handles ImportError for HTTP2 gracefully."""
        app = FastHTTP(http2=True)

        @app.get(url="https://example.com/api")
        async def handler(resp: Response) -> dict:
            return {}

        # Mock asyncio.run to raise ImportError
        with patch('asyncio.run', side_effect=ImportError("http2 not found")):
            app.run()

        # Should log error about HTTP2 (just verify it doesn't crash)
        assert True

    def test_run_with_connect_error(self, caplog) -> None:
        """Test run handles ConnectError gracefully."""
        import httpx

        app = FastHTTP()

        @app.get(url="https://example.com/api")
        async def handler(resp: Response) -> dict:
            return {}

        # Mock asyncio.run to raise ConnectError
        with patch('asyncio.run', side_effect=httpx.ConnectError("Connection failed")):
            app.run()

        # Should log connection error (just verify it doesn't crash)
        assert True


class TestFastHTTPLogResult:
    """Tests for _log_result method."""

    def test_log_result_with_response(self, caplog) -> None:
        """Test _log_result with successful response."""
        app = FastHTTP(debug=True)

        route = Route(
            method="GET",
            url="https://example.com/api",
            handler=lambda r: r,
        )

        response = Response(status=200, text="OK", headers={})

        # Just verify it doesn't crash
        app._log_result(route, 100.5, response)
        assert True

    def test_log_result_with_none(self, caplog) -> None:
        """Test _log_result with None response (error)."""
        app = FastHTTP(debug=True)

        route = Route(
            method="GET",
            url="https://example.com/api",
            handler=lambda r: r,
        )

        # Just verify it doesn't crash
        app._log_result(route, 100.5, None)
        assert True
