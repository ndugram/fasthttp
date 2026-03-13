"""Tests for GraphQL functionality."""
import pytest
from unittest.mock import AsyncMock, Mock, patch

from fasthttp.graphql.types import GraphQLRequest, GraphQLResponse


class TestGraphQLRequest:
    """Tests for GraphQLRequest class."""

    def test_graphql_request_basic(self) -> None:
        """Test basic GraphQLRequest creation."""
        request = GraphQLRequest(query="{ user { name } }")
        assert request.query == "{ user { name } }"
        assert request.variables is None
        assert request.operation_name is None

    def test_graphql_request_with_variables(self) -> None:
        """Test GraphQLRequest with variables."""
        request = GraphQLRequest(
            query="query GetUser($id: Int!) { user(id: $id) { name } }",
            variables={"id": 1},
        )
        assert request.query.startswith("query GetUser")
        assert request.variables == {"id": 1}

    def test_graphql_request_with_operation_name(self) -> None:
        """Test GraphQLRequest with operation name."""
        request = GraphQLRequest(
            query="query { user { name } }",
            operation_name="GetUser",
        )
        assert request.operation_name == "GetUser"

    def test_graphql_request_to_dict(self) -> None:
        """Test GraphQLRequest to_dict conversion."""
        request = GraphQLRequest(
            query="{ user { name } }",
            variables={"id": 1},
            operation_name="GetUser",
        )
        result = request.to_dict()
        assert result == {
            "query": "{ user { name } }",
            "variables": {"id": 1},
            "operationName": "GetUser",
        }

    def test_graphql_request_to_dict_minimal(self) -> None:
        """Test GraphQLRequest to_dict with minimal data."""
        request = GraphQLRequest(query="{ test }")
        result = request.to_dict()
        assert result == {"query": "{ test }"}
        assert "variables" not in result
        assert "operationName" not in result


class TestGraphQLResponse:
    """Tests for GraphQLResponse class."""

    def test_graphql_response_success(self) -> None:
        """Test GraphQLResponse with successful data."""
        response = GraphQLResponse(data={"user": {"name": "John"}})
        assert response.data == {"user": {"name": "John"}}
        assert response.errors is None
        assert response.ok is True
        assert response.has_errors is False

    def test_graphql_response_with_errors(self) -> None:
        """Test GraphQLResponse with errors."""
        response = GraphQLResponse(
            data=None,
            errors=[{"message": "User not found"}],
        )
        assert response.data is None
        assert response.errors == [{"message": "User not found"}]
        assert response.ok is False
        assert response.has_errors is True

    def test_graphql_response_with_extensions(self) -> None:
        """Test GraphQLResponse with extensions."""
        response = GraphQLResponse(
            data={"test": "data"},
            extensions={"traceId": "abc123"},
        )
        assert response.extensions == {"traceId": "abc123"}

    def test_graphql_response_all_fields(self) -> None:
        """Test GraphQLResponse with all fields."""
        response = GraphQLResponse(
            data={"user": {"name": "John"}},
            errors=None,
            extensions={"traceId": "xyz789"},
        )
        assert response.data == {"user": {"name": "John"}}
        assert response.ok is True
        assert response.extensions == {"traceId": "xyz789"}


class TestGraphQLClient:
    """Tests for GraphQL client functionality."""

    @pytest.mark.asyncio
    async def test_graphql_client_query(self) -> None:
        """Test GraphQL client query execution."""
        from fasthttp.graphql.client import create_graphql_client

        mock_response = AsyncMock()
        mock_response.json = Mock(return_value={
            "data": {"user": {"name": "John"}},
            "errors": None,
        })

        with patch("httpx.AsyncClient") as mock_client:
            mock_http_client = AsyncMock()
            mock_http_client.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_http_client

            client = create_graphql_client(url="https://api.example.com/graphql")
            result = await client.query(query="{ user { name } }")

            assert result.data == {"user": {"name": "John"}}
            assert result.errors is None
            assert result.ok is True

    @pytest.mark.asyncio
    async def test_graphql_client_query_with_variables(self) -> None:
        """Test GraphQL client query with variables."""
        from fasthttp.graphql.client import create_graphql_client

        mock_response = AsyncMock()
        mock_response.json = Mock(return_value={
            "data": {"user": {"name": "John"}},
            "errors": None,
        })

        with patch("httpx.AsyncClient") as mock_client:
            mock_http_client = AsyncMock()
            mock_http_client.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_http_client

            client = create_graphql_client(url="https://api.example.com/graphql")
            result = await client.query(
                query="query GetUser($id: Int!) { user(id: $id) { name } }",
                variables={"id": 1},
            )

            assert result.ok is True

    @pytest.mark.asyncio
    async def test_graphql_client_mutation(self) -> None:
        """Test GraphQL client mutation execution."""
        from fasthttp.graphql.client import create_graphql_client

        mock_response = AsyncMock()
        mock_response.json = Mock(return_value={
            "data": {"createUser": {"id": 1, "name": "John"}},
            "errors": None,
        })

        with patch("httpx.AsyncClient") as mock_client:
            mock_http_client = AsyncMock()
            mock_http_client.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_http_client

            client = create_graphql_client(url="https://api.example.com/graphql")
            result = await client.mutation(
                mutation="mutation { createUser(name: \"John\") { id name } }",
            )

            assert result.data == {"createUser": {"id": 1, "name": "John"}}

    @pytest.mark.asyncio
    async def test_graphql_client_with_errors(self) -> None:
        """Test GraphQL client with errors."""
        from fasthttp.graphql.client import create_graphql_client

        mock_response = AsyncMock()
        mock_response.json = Mock(return_value={
            "data": None,
            "errors": [{"message": "User not found"}],
        })

        with patch("httpx.AsyncClient") as mock_client:
            mock_http_client = AsyncMock()
            mock_http_client.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_http_client

            client = create_graphql_client(url="https://api.example.com/graphql")
            result = await client.query(query="{ user(id: 999) { name } }")

            assert result.data is None
            assert result.has_errors is True
            assert result.errors == [{"message": "User not found"}]

    @pytest.mark.asyncio
    async def test_graphql_client_with_headers(self) -> None:
        """Test GraphQL client with custom headers."""
        from fasthttp.graphql.client import create_graphql_client

        mock_response = AsyncMock()
        mock_response.json = Mock(return_value={"data": {"test": "data"}, "errors": None})

        with patch("httpx.AsyncClient") as mock_client:
            mock_http_client = AsyncMock()
            mock_http_client.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_http_client

            client = create_graphql_client(
                url="https://api.example.com/graphql",
                headers={"Authorization": "Bearer token"},
            )
            result = await client.query(query="{ test }")

            mock_http_client.post.assert_called_once()
            call_kwargs = mock_http_client.post.call_args.kwargs
            assert "Authorization" in call_kwargs["headers"]
            assert call_kwargs["headers"]["Authorization"] == "Bearer token"


class TestFastHTTPGraphQL:
    """Tests for FastHTTP @app.graphql() decorator."""

    def test_graphql_decorator_registration(self) -> None:
        """Test that @app.graphql() registers routes."""
        from fasthttp import FastHTTP
        from fasthttp.response import Response

        app = FastHTTP()

        @app.graphql(url="https://api.example.com/graphql")
        async def get_user(resp: Response) -> dict:
            return {"query": "{ user { name } }"}

        assert len(app.routes) == 1
        # Note: GRAPHQL routes are registered internally
        assert app.routes[0].url == "https://api.example.com/graphql"

    def test_graphql_decorator_mutation(self) -> None:
        """Test @app.graphql() with operation_type='mutation'."""
        from fasthttp import FastHTTP
        from fasthttp.response import Response

        app = FastHTTP()

        @app.graphql(url="https://api.example.com/graphql", operation_type="mutation")
        async def create_user(resp: Response) -> dict:
            return {"query": "mutation { test }"}

        assert len(app.routes) == 1

    def test_graphql_decorator_with_tags(self) -> None:
        """Test @app.graphql() with tags."""
        from fasthttp import FastHTTP
        from fasthttp.response import Response

        app = FastHTTP()

        @app.graphql(url="https://api.example.com/graphql", tags=["users"])
        async def get_user(resp: Response) -> dict:
            return {"query": "{ user { name } }"}

        assert app.routes[0].tags == ["users"]

    def test_graphql_decorator_multiple_routes(self) -> None:
        """Test multiple GraphQL routes."""
        from fasthttp import FastHTTP
        from fasthttp.response import Response

        app = FastHTTP()

        @app.graphql(url="https://api.example.com/graphql")
        async def get_user(resp: Response) -> dict:
            return {"query": "{ user { name } }"}

        @app.graphql(url="https://api.example.com/graphql", operation_type="mutation")
        async def create_user(resp: Response) -> dict:
            return {"query": "mutation { test }"}

        assert len(app.routes) == 2

    @pytest.mark.asyncio
    async def test_graphql_handler_execution(self) -> None:
        """Test GraphQL handler execution with mocked client."""
        from fasthttp import FastHTTP
        from fasthttp.response import Response

        app = FastHTTP()

        @app.graphql(url="https://api.example.com/graphql")
        async def get_user(resp: Response) -> dict:
            return {"query": "{ user { name } }"}

        # Mock the GraphQL client to avoid real HTTP requests
        mock_response = Mock()
        mock_response.data = {"user": {"name": "John"}}
        mock_response.errors = None

        with patch("fasthttp.app.create_graphql_client") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.query = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            route = app.routes[0]
            response = Response(status=200, text="test", headers={})

            result = await route.handler(response)

            assert result is not None